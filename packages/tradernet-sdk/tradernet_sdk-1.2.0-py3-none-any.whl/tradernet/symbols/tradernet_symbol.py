"""
Tradernet market data
"""
from __future__ import annotations

from datetime import datetime

from numpy import array, float64, int64, datetime64, timedelta64
from numpy.typing import NDArray

from ..client import TraderNetAPI
from .base_market_symbol import BaseMarketSymbol


class TraderNetSymbol(BaseMarketSymbol):
    """
    Acquiring and processing data from Tradernet.

    Parameters
    ----------
    symbol : str
        A symbol name on a remote service.
    start : datetime
        The first date of the period market data to be acquired within.
    end : datetime
        The last date of the period.

    Attributes
    ----------
    timeframe : int
        Timeframe of candles in seconds. Default is 86400 corresponding to day
        candles.
    """
    __slots__ = ('timeframe',)

    def __init__(
        self,
        symbol: str,
        api: TraderNetAPI | None = None,
        start: datetime = datetime(1970, 1, 1),
        end: datetime = datetime.now()
    ) -> None:
        super().__init__(symbol, api, start, end)
        self.timeframe = 86400

    def get_data(self) -> TraderNetSymbol:
        if not self.api or not isinstance(self.api, TraderNetAPI):
            self.api = TraderNetAPI()

        candles = self.api.get_candles(
            self.symbol,
            timeframe=self.timeframe,
            start=self.start,
            end=self.end
        )

        if 'hloc' in candles:
            self.timestamps: NDArray[datetime64] = array(
                candles['xSeries'][self.symbol],
                dtype='datetime64[s]'
            )
            self.timestamps += timedelta64(3, 'h')  # UTC adjustment

            self.candles = array(candles['hloc'][self.symbol], dtype=float64)
            self.volumes = array(candles['vl'][self.symbol], dtype=int64)

        return self
