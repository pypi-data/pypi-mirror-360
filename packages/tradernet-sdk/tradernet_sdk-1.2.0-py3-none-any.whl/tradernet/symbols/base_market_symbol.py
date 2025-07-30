from __future__ import annotations

from abc import ABCMeta, abstractmethod
from datetime import datetime, date
from logging import getLogger

from numpy import (
    array,
    diff,
    datetime64,
    float64,
    int64,
    isfinite,
    isnan,
    log,
    nan
)
from numpy.typing import NDArray

from ..client import TraderNetAPI


def np_to_date(value: datetime64) -> date:
    dt = datetime.fromtimestamp(value.astype('O')/1e9)
    return date(dt.year, dt.month, dt.day)


class BaseMarketSymbol(metaclass=ABCMeta):
    """
    An abstract base class to get market data containing methods for their
    processing.

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
    symbol : str
        A symbol name on a remote service.
    api : API class instance, optional
        API is to be used to get market data.
    start : datetime
        The first date of the period market data to be acquired within.
    end : datetime
        The last date of the period.
    logger : Logger
        Saving info and debugging.
    timestamps : array_like
        Timestamps of candles.
    candles : array_like
        High, low, open and close prices of candles.
    volumes : array_like
        Volumes of trades.
    """
    __slots__ = (
        'symbol',
        'api',
        'start',
        'end',
        'logger',
        'timestamps',
        'candles',
        'volumes'
    )

    def __init__(
        self,
        symbol: str,
        api: TraderNetAPI | None = None,
        start: datetime = datetime(1970, 1, 1),
        end: datetime = datetime.now()
    ) -> None:
        self.symbol = symbol
        self.api = api

        # Dates interval
        self.start = start
        self.end = end

        self.logger = getLogger(self.__class__.__name__)

        self.timestamps: NDArray[datetime64] = array([], dtype=datetime64)
        self.candles: NDArray[float64] = array([], dtype=float64)
        self.volumes: NDArray[int64] = array([], dtype=int64)

    def returns(self, kind: str = 'percent') -> NDArray[float64]:
        """
        Computing returns from market data.

        Parameters
        ----------
        kind : str
            A kind of returns. Allowed values are `percent` and `log` meaning
            per cent to previous close or natural logarithm of closes ratio.

        Returns
        -------
        result : array_like
            Symbol returns free of null values.
        """
        if self.candles.size == 0:
            return array([])

        close_prices = self.candles[:, 3]

        if kind == 'percent':
            data = diff(close_prices)/close_prices[:-1]
        elif kind == 'log':
            data = log(close_prices[1:]/close_prices[:-1])
        else:
            raise RuntimeError('Invalid return kind')
        # Filtering infinities out
        data = data[isfinite(data)]
        # Filtering non-numbers
        return data[~isnan(data)]

    def gaps(self, kind: str = 'percent') -> NDArray[float64]:
        """
        Computing gaps from market data.

        Parameters
        ----------
        kind : str
            A kind of returns. Allowed values are `percent` and `log` meaning
            per cent to previous close or natural logarithm of closes ratio.

        Returns
        -------
        result : array_like
            Symbol gaps free of null values.

        Notes
        -----
        Gap is a distance from the close price to the open price next business
        day.
        """
        if self.candles.size == 0:
            return array([])

        open_prices = self.candles[:, 2]
        close_prices = self.candles[:, 3]

        if kind == 'percent':
            data = open_prices[1:]/close_prices[:-1] - 1
        elif kind == 'log':
            data = log(open_prices[1:]/close_prices[:-1])
        else:
            raise RuntimeError('Invalid return kind')
        # Filtering infinities out
        data = data[isfinite(data)]
        # Filtering non-numbers
        return data[~isnan(data)]

    def last_price(self) -> float:
        """
        Extracts the last non-null price from market data, either at the market
        open, or at close.

        Returns
        -------
        float, optional
            The last price if there is one.
        """
        if self.candles.size == 0:
            self.logger.warning('No last price: market data is empty')
            return nan

        # Open prices first, then close
        price_sequence = self.candles[:, [0, 3]].flatten()

        # Throwing away nulls
        existing_prices = price_sequence[~isnan(price_sequence)]
        if existing_prices.size == 0:
            self.logger.warning('All prices found are null')
            return nan

        price = existing_prices[-1]  # Behold, the last price!
        self.logger.debug('Last price of %s is %s', self.symbol, price)
        return price

    @abstractmethod
    def get_data(self) -> BaseMarketSymbol:
        """
        Abstract method acquiring data and assigning
        BaseMarketSymbol.market_data to them.
        """
