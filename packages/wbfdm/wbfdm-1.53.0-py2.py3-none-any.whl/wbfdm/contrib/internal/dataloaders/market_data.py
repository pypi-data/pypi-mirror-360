from datetime import date
from decimal import Decimal
from typing import Iterator

from wbcore.contrib.dataloader.dataloaders import Dataloader

from wbfdm.dataloaders.protocols import MarketDataProtocol
from wbfdm.dataloaders.types import MarketDataDict
from wbfdm.enums import MarketData
from wbfdm.models.instruments.instrument_prices import InstrumentPrice

MarketDataMap = {
    "SHARES_OUTSTANDING": "internal_outstanding_shares",
    "OPEN": "net_value",
    "CLOSE": "net_value",
    "HIGH": "net_value",
    "LOW": "net_value",
    "BID": "net_value",
    "ASK": "net_value",
    "VOLUME": "internal_volume",
    "MARKET_CAPITALIZATION": "market_capitalization",
}

DEFAULT_VALUES = [MarketData[name] for name in MarketDataMap.keys()]


def _cast_decimal_to_float(value: float | Decimal) -> float:
    if isinstance(value, Decimal):
        value = float(value)
    return value


class MarketDataDataloader(MarketDataProtocol, Dataloader):
    def market_data(
        self,
        values: list[MarketData] | None = [MarketData.CLOSE],
        from_date: date | None = None,
        to_date: date | None = None,
        exact_date: date | None = None,
        calculated: bool | None = None,
        **kwargs,
    ) -> Iterator[MarketDataDict]:
        """Get prices for instruments.

        Args:
            values (list[MarketData]): List of values to include in the results.
            from_date (date | None): The starting date for filtering prices. Defaults to None.
            to_date (date | None): The ending date for filtering prices. Defaults to None.
            frequency (Frequency): The frequency of the requested data

        Returns:
            Iterator[MarketDataDict]: An iterator of dictionaries conforming to the DailyValuationDict.
        """
        prices = InstrumentPrice.objects.filter(instrument__in=self.entities).annotate_market_data()  # type: ignore
        if calculated is not None:
            prices = prices.filter(calculated=calculated)
        else:
            prices = prices.filter_only_valid_prices()

        prices = prices.order_by("date")
        if not values:
            values = DEFAULT_VALUES
        values_map = {value.name: MarketDataMap[value.name] for value in values if value.name in MarketDataMap}
        if exact_date:
            prices = prices.filter(date=exact_date)
        else:
            if from_date:
                prices = prices.filter(date__gte=from_date)
            if to_date:
                prices = prices.filter(date__lte=to_date)
        for row in prices.filter_only_valid_prices().values(
            "date",
            "instrument",
            "calculated",
            *set(values_map.values()),
        ):
            external_id = row.pop("instrument")
            val_date = row.pop("date")
            if row:
                yield MarketDataDict(
                    id=f"{external_id}_{val_date}",
                    valuation_date=val_date,
                    instrument_id=external_id,
                    external_id=external_id,
                    source="wbfdm",
                    calculated=row["calculated"],
                    **{MarketData[k].value: _cast_decimal_to_float(row[v]) for k, v in values_map.items()},
                )
