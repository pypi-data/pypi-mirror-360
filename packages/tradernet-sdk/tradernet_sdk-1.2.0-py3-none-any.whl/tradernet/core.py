from __future__ import annotations

from configparser import ConfigParser
from copy import deepcopy
from datetime import datetime
from json import dumps as json_dumps
from logging import getLogger
from typing import Any, ClassVar, Type, TypeVar

from .common import NetUtils


Self = TypeVar('Self', bound='TraderNetCore')


class TraderNetCore(NetUtils):
    """
    Core tools to interact Tradernet API.

    Parameters
    ----------
    public : str, optional
        A Tradernet public key.
    private: str, optional
        A Tradernet private key.
    login : str, optional
        A Tradernet login.
    password : str, optional
        A password for the login.

    Attributes
    ----------
    logger : Logger
        Handling errors and warnings.
    """
    DOMAIN: ClassVar[str] = 'tradernet.com'  # Tradernet server
    SESSION_TIME: ClassVar[int] = 18000      # 18000 seconds == 5 hours
    HEADERS: ClassVar[dict[str, str]] = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    CHUNK_SIZE: ClassVar[int] = 7000         # Instruments per request
    MAX_EXPORT_SIZE: ClassVar[int] = 100     # Max instruments per export
    DURATION: ClassVar[dict[str, int]] = {
        'day': 1,  # The order will be valid until the end of the trading day.
        'ext': 2,  # Extended day order.
        'gtc': 3   # A.k.a. "Good Till Cancelled"
    }

    __slots__ = (
        'public',
        '_private',
        'login',
        '_password',
        '_session_id',
        '_session_time'
    )

    def __init__(
        self,
        public: str | None = None,
        private: str | None = None,
        login: str | None = None,
        password: str | None = None
    ) -> None:
        super().__init__()
        self.logger = getLogger(self.__class__.__name__)

        # Setting authorization data
        self.public = public
        self._private = private
        self.login = login
        self._password = password

        # Checking input
        if not self.public or not self._private:
            self.logger.warning(
                'A keypair was not set. It can be generated here: '
                '%s/tradernet-api/auth-api',
                self.url
            )

        self._session_id: str | None = None
        self._session_time: datetime | None = None

    @classmethod
    def from_config(cls: Type[Self], config_file: str) -> Self:
        """
        Getting a session ID with the use of the login-password
        authorization.

        Parameters
        ----------
        config_file : str
            A path to the configuration file.

        Returns
        -------
        Self
            A new instance.
        """
        config = ConfigParser()
        config.read(config_file)

        auth = config['auth'] if 'auth' in config else {}
        sid = config['sid'] if 'sid' in config else {}

        instance = cls(
            auth['public'] if 'public' in auth else None,
            auth['private'] if 'private' in auth else None,
            sid['login'] if 'login' in sid else None,
            sid['password'] if 'password' in sid else None
        )

        return instance

    @classmethod
    def from_instance(cls: Type[Self], instance: TraderNetCore) -> Self:
        """
        Creating a new instance from another one.

        Parameters
        ----------
        instance : TraderNetCore
            Other instance to initialize from.

        Returns
        -------
        Self
            A new instance.
        """
        # pylint: disable=protected-access
        core = cls(
            instance.public,
            instance._private,
            instance.login,
            instance._password
        )

        # Avoiding out of sync sessions
        if not instance._session_id:
            instance.get_authorized()

        core._session_id = instance._session_id
        core._session_time = instance._session_time

        return core

    @property
    def url(self) -> str:
        return f'https://{self.DOMAIN}'

    @property
    def websocket_url(self) -> str:
        return f'wss://wss.{self.DOMAIN}'

    def get_websocket_url(self) -> str:
        if not self._session_id:
            if self.login and self._password:
                # Trying to get a session key
                self.get_authorized()
                return self.get_websocket_url()

            # In the case of no success using demo access
            self.logger.warning(
                'No valid login or password is provided, '
                'market data will be delayed'
            )
            return self.websocket_url

        return f'{self.websocket_url}?SID={self._session_id}'

    def get_auth_info(self) -> dict[str, Any]:
        """
        Getting information about an opened session.

        Returns
        -------
        dict[str, Any]
            Information about the authorization.
        """
        return self.authorized_request('getSidInfo')

    def get_authorized(self) -> None:
        """
        Getting a session ID with the use of the login-password authorization.
        """
        auth_info = self.get_auth_info()
        # Trying to reuse a session
        if 'SID' in auth_info and auth_info['SID'] and self._session_time and (
            datetime.now() - self._session_time
        ).total_seconds() < self.SESSION_TIME:  # is the session expired?
            self._session_id = auth_info['SID']
            self.logger.debug('Session ID: %s', self._session_id)
            return

        url = f'{self.url}/api/check-login-password'
        message = {
            'login': self.login,
            'password': self._password,
            'remember_me': 1
        }
        response = self.request('post', url, params=message)
        result = response.json()
        self.logger.debug('Authorization result: %s', result)

        if 'SID' in result:
            # Setting session key
            self._session_id = result['SID']
            # Setting timer
            self._session_time = datetime.now()
        else:
            self.logger.warning('Cannot obtain session ID: %s', result)

    def plain_request(
        self,
        cmd: str,
        params: dict[str, Any] | None = None
    ) -> Any:
        """
        Unencoded GET request to Tradernet. It could use either use
        authorization or not (if the session ID is not set).

        Parameters
        ----------
        cmd : str
            A command.
        params : dict[str, Any] | None, optional
            Set of parameters in the request.

        Returns
        -------
        Any
            JSON-decoded answer from Tradernet.
        """
        self.logger.debug('Making a simple request to API')

        message = self.__compose_message(cmd, params)
        if self._session_id:
            message['SID'] = self._session_id
            self.logger.debug('Using authorization')

        url = f'{self.url}/api'
        query = {'q': json_dumps(message)}

        self.logger.debug('Message: %s', message)
        self.logger.debug('Query: %s', query)

        response = self.request('get', url, params=query)
        return response.json()

    def authorized_request(
        self,
        cmd: str,
        params: dict[str, Any] | None = None,
        version: int | None = 2
    ) -> Any:
        """
        Sending formatted and encoded request to Tradernet using keypair
        authorization.

        Parameters
        ----------
        cmd : str
            A command.
        params : dict, optional
            Set of parameters in the request.
        version : int, optional
            API version, by default 2

        Returns
        -------
        Answer from Tradernet.
        """
        self.logger.debug('Making request to v%s API with auth', version)

        if self._private is None:
            raise ValueError('Private key is not set')

        message = self.__compose_message(cmd, params)

        url = f'{self.url}/api'
        headers = None

        if not version:
            if not self._session_id:
                self.get_authorized()
            message['SID'] = self._session_id
            query: bytes | dict[str, str] = {'q': json_dumps(message)}

        elif version == 1:
            message['sig'] = self.sign(self._private)
            query = {'q': json_dumps(message)}

        elif version in (2, 3):
            url = f'{self.url}/api/v{version}/cmd/{cmd}'
            message['apiKey'] = self.public
            message_string = self.str_from_dict(message)

            # Signing the body of the request
            headers = deepcopy(self.HEADERS)
            headers['X-NtApi-Sig'] = self.sign(self._private, message_string)
            query = self.http_build_query(message).encode('utf-8')
            self.logger.debug('Message string: %s', message_string)

        else:
            raise ValueError('Unknown API version')

        # Making proper lists of parameters
        if params:
            for key, value in params.items():
                if isinstance(value, list) \
                        and all(isinstance(val, str) for val in value):
                    params[key] = '+'.join(value)

        self.logger.debug(
            'Sending POST to %s, parameters: %s, query: %s',
            url,
            params,
            query
        )

        response = self.request(
            'post',
            url,
            headers=headers,
            params=params,
            data=query
        )
        result = response.json()

        if 'errMsg' in result:
            self.logger.error('Error: %s', result['errMsg'])

        return result

    def list_security_sessions(self) -> dict[str, Any]:
        """
        Getting a list of open security sessions.

        Notes
        -----
        https://tradernet.ru/tradernet-api/security-get-list
        """
        return self.authorized_request('getSecuritySessions')

    def send_security_sms(
        self,
        telegram_only: bool = False,
        push_only: bool = False
    ) -> dict[str, Any]:
        """
        Requesting a security code via SMS.

        Parameters
        ----------
        telegram_only : bool | None
            Send Telegram bot notifications only.
        push_only : bool | None
            Send Push notifications only (for mobile devices).

        Notes
        -----
        https://tradernet.ru/tradernet-api/security-open-sms
        """
        if telegram_only and push_only:
            raise ValueError('Please choose only one option')

        return self.authorized_request(
            'getSecuritySms',
            {'telegram_only': telegram_only, 'push_only': push_only},
            version=None
        )

    def open_with_sms(
        self,
        token: str
    ) -> dict[str, Any]:
        """
        Opening a security session with a security code sent via SMS.

        Parameters
        ----------
        token : str
            A security code.
        """
        return self.authorized_request(
            'openSecuritySession',
            {'validationKey': token, 'safetyTypeId': 3},
            version=None
        )

    def open_with_token(
        self,
        token: str,
        digital_signature: bool = False
    ) -> dict[str, Any]:
        """
        Opening a session with a web token or a digital signature.

        Parameters
        ----------
        token : str
            A signature token.
        digital_signature : bool
            A flag indicating whether the token is a digital signature or a web
            token.

        Notes
        -----
        https://tradernet.ru/tradernet-api/security-open-web-token
        https://tradernet.ru/tradernet-api/security-open-eds
        """
        return self.authorized_request(
            'openSecuritySession',
            {
                'safetyTypeId': 7 if digital_signature else 8,
                'signature': token,
                'message': self._session_id
            },
            version=None
        )

    @staticmethod
    def __compose_message(
        cmd: str,
        params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        message: dict[str, Any] = {'cmd': cmd}
        if params:
            message['params'] = params

        return message
