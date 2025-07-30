import logging
from contextlib import suppress
from datetime import date
from decimal import Decimal

import numpy as np
import pandas as pd
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.validators import DecimalValidator
from django.db.models import (
    AutoField,
    Exists,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
)
from django.db.models.functions import Coalesce
from wbcore.contrib.currency.models import CurrencyFXRates

from wbfdm.enums import MarketData

logger = logging.getLogger("pms")


class InstrumentQuerySet(QuerySet):
    def filter_active_at_date(self, val_date: date):
        return self.filter(
            (Q(delisted_date__isnull=True) | Q(delisted_date__gte=val_date))
            & (Q(inception_date__isnull=True) | Q(inception_date__lte=val_date))
        )

    def annotate_classification_for_group(
        self, classification_group, classification_height: int = 0, **kwargs
    ) -> QuerySet:
        return classification_group.annotate_queryset(
            self, classification_height, "", annotation_label="ancestor_classifications", **kwargs
        )

    def annotate_base_data(self):
        base_qs = InstrumentQuerySet(self.model, using=self._db)
        return self.annotate(
            is_investable=~Exists(base_qs.filter(parent=OuterRef("pk"))),
            root=Subquery(base_qs.filter(tree_id=OuterRef("tree_id"), level=0).values("id")[:1]),
            primary_security=ExpressionWrapper(
                Coalesce(
                    Subquery(
                        base_qs.filter(
                            parent=OuterRef("pk"),
                            is_primary=True,
                            is_security=True,
                        ).values("id")[:1]
                    ),
                    F("id"),
                ),
                output_field=AutoField(),
            ),
            primary_quote=ExpressionWrapper(
                Coalesce(
                    Subquery(
                        base_qs.filter(
                            parent=OuterRef("primary_security"),
                            is_primary=True,
                        ).values("id")[:1]
                    ),
                    F("primary_security"),
                ),
                output_field=AutoField(),
            ),
        )

    def annotate_all(self):
        return self.annotate_base_data()

    @property
    def dl(self):
        """Provides access to the dataloader proxy for the entities in the QuerySet.

        This method allows for easy retrieval of the DataloaderProxy instance
        associated with the QuerySet. It enables the utilization of dataloader
        functionalities directly from the QuerySet, facilitating data fetching and
        processing tasks.

        Returns:
            DataloaderProxy: An instance of DataloaderProxy associated with the
                entities in the QuerySet.
        """
        return self.model.dl_proxy(self)

    def get_instrument_prices_from_market_data(self, from_date: date, to_date: date):
        from wbfdm.models import InstrumentPrice

        def _dict_to_object(instrument, row):
            close = row.get("close", None)
            price_date = row.get("date")
            if price_date and close is not None:
                close = round(Decimal(close), 6)
                # we validate that close can be inserting into our table<
                with suppress(ValidationError):
                    validator = DecimalValidator(16, 6)
                    validator(close)
                    try:
                        try:
                            InstrumentPrice.objects.get(instrument=instrument, date=price_date)
                        except MultipleObjectsReturned:
                            InstrumentPrice.objects.get(
                                instrument=instrument, date=price_date, calculated=False
                            ).delete()
                        p = InstrumentPrice.objects.get(instrument=instrument, date=price_date)
                        p.net_value = close
                        p.gross_value = close
                        p.calculated = row["calculated"]
                        p.volume = row.get("volume", p.volume)
                        p.market_capitalization = row.get("market_capitalization", p.market_capitalization)
                        p.market_capitalization_consolidated = p.market_capitalization
                        p.set_dynamic_field(False)
                        p.id = None
                        return p
                    except InstrumentPrice.DoesNotExist:
                        with suppress(CurrencyFXRates.DoesNotExist):
                            p = InstrumentPrice(
                                currency_fx_rate_to_usd=CurrencyFXRates.objects.get(
                                    # we need to get the currency rate because we bulk create the object, and thus save is not called
                                    date=price_date,
                                    currency=instrument.currency,
                                ),
                                instrument=instrument,
                                date=price_date,
                                calculated=row["calculated"],
                                net_value=close,
                                gross_value=close,
                                volume=row.get("volume", None),
                                market_capitalization=row.get("market_capitalization", None),
                            )
                            p.set_dynamic_field(False)
                            return p

        df = pd.DataFrame(
            self.dl.market_data(
                from_date=from_date,
                to_date=to_date,
                values=[MarketData.CLOSE, MarketData.VOLUME, MarketData.MARKET_CAPITALIZATION],
            )
        )
        if not df.empty:
            df["valuation_date"] = pd.to_datetime(df["valuation_date"])
            df = df.rename(columns={"valuation_date": "date"})
            df = df.drop(
                columns=df.columns.difference(
                    ["calculated", "close", "market_capitalization", "volume", "instrument_id", "date"]
                )
            )
            df["calculated"] = False

            for instrument_id, dff in df.groupby("instrument_id", group_keys=False, as_index=False):
                dff = dff.drop(columns=["instrument_id"]).set_index("date").sort_index()
                if dff.index.duplicated().any():
                    dff = dff.groupby(level=0).first()
                    logger.warning(
                        f"We detected a duplicated index for instrument id {instrument_id}. Please correct the dl parameter which likely introduced this issue."
                    )

                dff = dff.reindex(pd.date_range(dff.index.min(), dff.index.max(), freq="B"))

                dff[["close", "market_capitalization"]] = dff[["close", "market_capitalization"]].astype(float).ffill()
                dff.volume = dff.volume.astype(float).fillna(0)
                dff.calculated = dff.calculated.astype(bool).fillna(
                    True
                )  # we do not ffill calculated but set the to True to mark them as "estimated"/"not real"

                dff = dff.reset_index(names="date").dropna(subset=["close"])
                dff = dff.replace([np.inf, -np.inf, np.nan], None)
                instrument = self.get(id=instrument_id)

                yield from filter(
                    lambda x: x, map(lambda row: _dict_to_object(instrument, row), dff.to_dict("records"))
                )
