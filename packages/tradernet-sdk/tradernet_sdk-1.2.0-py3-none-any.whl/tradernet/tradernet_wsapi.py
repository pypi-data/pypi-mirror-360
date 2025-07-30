from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from json import loads as json_loads
from typing import Any

from .common import WSUtils, StringUtils
from .core import TraderNetCore


class TraderNetWSAPI(WSUtils, StringUtils):
    __slots__ = ('url',)

    def __init__(self, api: TraderNetCore) -> None:
        super().__init__()
        self.url = api.get_websocket_url()

    async def quotes(
        self,
        symbols: str | Sequence[str]
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribing quotes updates.

        Parameters
        ----------
        symbols : str | Sequence[str]
            A sequence of symbols or a single symbol.

        Yields
        ------
        AsyncIterator[dict[str, Any]]
            Quote updates.
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        query = self.stringify(['quotes', symbols])

        async for message in self.get_stream(query, self.url):
            event, data, _ = json_loads(message)
            if event == 'q':
                yield data

    async def market_depth(self, symbol: str) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribe to market depth updates.

        Parameters
        ----------
        symbol : str
            A Tradernet symbol.

        Yields
        ------
        AsyncIterator[dict[str, Any]]
            Market depth updates.
        """
        query = self.stringify(['orderBook', [symbol]])

        async for message in self.get_stream(query, self.url):
            event, data, _ = json_loads(message)
            if event == 'b':
                yield data

    async def portfolio(self) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribe to portfolio updates.

        Yields
        -------
        AsyncIterator[dict[str, Any]]
            Portfolio updates.
        """
        query = self.stringify(['portfolio'])

        async for message in self.get_stream(query, self.url):
            event, data, _ = json_loads(message)
            if event == 'portfolio':
                yield data

    async def orders(self) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribing orders updates.

        Yields
        -------
        AsyncIterator[dict[str, Any]]
            Orders updates.
        """
        query = self.stringify(['orders'])

        async for message in self.get_stream(query, self.url):
            event, data, _ = json_loads(message)
            if event == 'orders':
                yield data

    async def markets(self) -> dict[str, Any]:
        """
        Subscribing markets statuses.

        Yields
        -------
        AsyncIterator[dict[str, Any]]
            Markets statuses.
        """
        query = self.stringify(['markets'])

        async for message in self.get_stream(query, self.url):
            event, data, _ = json_loads(message)
            if event == 'markets':
                return data
        return {}
