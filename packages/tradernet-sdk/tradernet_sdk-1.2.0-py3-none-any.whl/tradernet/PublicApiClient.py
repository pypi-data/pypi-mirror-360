from __future__ import annotations

from typing import Any, ClassVar

from .core import TraderNetCore


class PublicApiClient(TraderNetCore):
    """
    Legacy Tradernet API.

    Parameters
    ----------
    apiKey : str | None
        Tradernet API public key.
    apiSecret : str | None
        Tradernet API private key.
    version : int, optional
        Tradernet API version.
    """
    V1: ClassVar[int] = 1
    V2: ClassVar[int] = 2

    __slots__ = ('__version',)

    def __init__(
        self,
        apiKey: str | None = None,
        apiSecret: str | None = None,
        version: int = 1
    ) -> None:
        super().__init__(apiKey, apiSecret)
        self.__version = version

    def sendRequest(
        self,
        method: str,
        aParams: dict[str, Any] | None = None,
        format: str = 'JSON'
    ) -> Any:
        """
        Legacy interface to send a request to Tradernet.

        Parameters
        ----------
        method : str
            HTTP method.
        aParams : dict[str, Any] | None, optional
            HTTP parameters.
        format : str, optional
            Some format.

        Returns
        -------
        response : Any
            Response JSON.
        """
        return self.authorized_request(method, aParams, self.__version)
