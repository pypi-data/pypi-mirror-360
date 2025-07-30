import dataclasses
import datetime
import typing

import wialon.api
from django.conf import settings
from loguru import logger

from . import flags as wialon_flags

logger.disable(__name__)


@dataclasses.dataclass
class WialonAPICall:
    action: str
    timestamp: datetime.datetime
    result: typing.Any = None
    error: Exception | None = None


class Wialon(wialon.api.Wialon):
    def __init__(self, token: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.token = token
        self.call_history: list[WialonAPICall] = []

    @property
    def total_calls(self) -> int:
        return len(self.call_history)

    @property
    def call_actions(self) -> list[str]:
        return [call.action for call in self.call_history]

    def token_login(self, *args, **kwargs) -> typing.Any:
        kwargs.setdefault("appName", "python-terminusgps")
        return self.call("token_login", *args, **kwargs)

    def call(self, action_name: str, *argc, **kwargs) -> dict[str, typing.Any]:
        try:
            timestamp = datetime.datetime.now()
            result = super().call(action_name, *argc, **kwargs)
            call_record = WialonAPICall(
                action=action_name, timestamp=timestamp, result=result
            )
            return result
        except wialon.api.WialonError as e:
            print(e)
            call_record = WialonAPICall(
                action=action_name, timestamp=timestamp, error=e
            )
            return {}
        finally:
            if call_record.result:
                logger.debug("Successfully executed '{}'", action_name)
            elif call_record.error:
                logger.warning(
                    "Failed to execute '{}': {}", action_name, call_record.error
                )
            self.call_history.append(call_record)


class WialonSession:
    def __init__(
        self,
        token: str | None = None,
        sid: str | None = None,
        scheme: str = "https",
        host: str = "hst-api.wialon.com",
        port: int = 443,
    ) -> None:
        """
        Starts or continues a Wialon API session.

        :param token: An optional Wialon API token. Default is :confval:`WIALON_TOKEN`.
        :type token: :py:obj:`str` | :py:obj:`None`
        :param sid: An optional Wialon API session id. If provided, the session is continued.
        :type sid: :py:obj:`str` | :py:obj:`None`
        :param scheme: HTTP request scheme to use. Default is ``"https"``.
        :type scheme: :py:obj:`str`
        :param host: Wialon API host url. Default is ``"hst-api.wialon.com"``.
        :type host: :py:obj:`str`
        :param host: Wialon API rendering url. Default is ``"render-maps.wialon.com"``.
        :type host: :py:obj:`str`
        :param port: Wialon API host port. Default is ``443``.
        :type port: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self._token = token or settings.WIALON_TOKEN
        self._username = None
        self._gis_sid = None
        self._hw_gp_ip = None
        self._wsdk_version = None
        self._uid = None
        self._wialon_api = Wialon(
            scheme=scheme, host=host, port=port, sid=sid, token=self.token
        )

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self) -> str:
        return f"{self.__class__}(sid={self.id})"

    def __enter__(self) -> "WialonSession":
        """
        Logs into the Wialon API using :py:meth:`login`.

        :raises AssertionError: If the session's Wialon API :py:attr:`token` wasn't set.
        :returns: A valid Wialon API session.
        :rtype: :py:obj:`~terminusgps.wialon.session.WialonSession`

        """
        assert self.token, "Wialon API token wasn't set."
        self.login(self.token)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Logs out of the session by calling :py:meth:`logout`.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.logout()

    @property
    def wialon_api(self) -> Wialon:
        return self._wialon_api

    @property
    def gis_geocode(self) -> str | None:
        """
        Gis geocode URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_geocode

    @property
    def gis_render(self) -> str | None:
        """
        Gis rendering URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_render

    @property
    def gis_routing(self) -> str | None:
        """
        Gis routing URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_routing

    @property
    def gis_search(self) -> str | None:
        """
        Gis search URL.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_search

    @property
    def gis_sid(self) -> str | None:
        """
        Gis session id.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._gis_sid

    @property
    def host(self) -> str | None:
        """
        IP of the client hosting the Wialon session.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._host

    @property
    def hw_gw_ip(self) -> str | None:
        """
        Hardware gateway IP.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._hw_gw_ip

    @property
    def hw_gw_dns(self) -> str | None:
        """
        Hardware gateway domain name, should evaluate to :py:attr:`hw_gw_ip` if present.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._hw_gw_dns

    @property
    def wsdk_version(self) -> str | None:
        """
        The Wialon Source Developer Kit (WSDK) version number of the session.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._wsdk_version

    @property
    def uid(self) -> str | None:
        """
        A Wialon user ID this session is operating as.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`
        """
        return self._uid

    @property
    def username(self) -> str | None:
        """
        A Wialon username the session is operating as.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self._username

    @property
    def id(self) -> str | None:
        """
        Shortcut property for :py:attr:`WialonSession.wialon_api.sid`.

        Returns :py:obj:`None` if the session wasn't logged in.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

        """
        return self.wialon_api.sid

    @property
    def token(self) -> str:
        """
        A Wialon API token set during :py:meth:`WialonSession.__init__`.

        Default token value is :confval:`WIALON_TOKEN`.

        :type: :py:obj:`str`
        :value: :confval:`WIALON_TOKEN`

        """
        return str(self._token)

    def login(self, token: str, flags: int | None = None) -> str:
        """
        Logs into the Wialon API and starts a new session.

        :param token: An active Wialon API token.
        :type token: :py:obj:`str`
        :param flags: A login response flag integer.
        :type flags: :py:obj:`int`
        :raises WialonError: If the login fails.
        :raises AssertionError: If the login token was not set.
        :returns: The new session id.
        :rtype: :py:obj:`str`

        """
        if flags is None:
            flags = (
                wialon_flags.TokenFlag.ONLINE_TRACKING
                | wialon_flags.TokenFlag.VIEW_ACCESS
                | wialon_flags.TokenFlag.MANAGE_NONSENSITIVE
            )
        try:
            response = self.wialon_api.token_login(**{"token": token, "fl": flags})
            self._set_login_response(response)
            return response.get("eid", "")
        except (wialon.api.WialonError, ValueError):
            logger.critical("Failed to login to the Wialon API.")
            raise

    def logout(self) -> None:
        """
        Logs out of the Wialon API session.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        response: dict = self.wialon_api.core_logout({})
        self.wialon_api.sid = None

        if response.get("error") != 0:
            logger.warning(
                "Failed to logout of the session: '{}'", response.get("message")
            )

    def _set_login_response(self, login_response: dict | None) -> None:
        """
        Sets the Wialon API session's attributes based on a login response.

        :param login_response: A dictionary returned from :py:meth:`login`.
        :type login_response: :py:obj:`dict`
        :raises ValueError: If ``login_response`` wasn't provided.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if login_response is None:
            raise ValueError("Failed to login to Wialon.")

        self.wialon_api.sid = login_response.get("eid")
        self._gis_geocode = login_response.get("gis_geocode")
        self._gis_render = login_response.get("gis_render")
        self._gis_routing = login_response.get("gis_routing")
        self._gis_search = login_response.get("gis_search")
        self._gis_sid = login_response.get("gis_sid")
        self._host = login_response.get("host")
        self._hw_gw_dns = login_response.get("hw_gw_dns")
        self._hw_gw_ip = login_response.get("hw_gw_ip")
        self._uid = login_response.get("user", {}).get("id")
        self._nm = login_response.get("user", {}).get("nm")
        self._username = login_response.get("au")
        self._video_service_url = login_response.get("video_service_url")
        self._wsdk_version = login_response.get("wsdk_version")
