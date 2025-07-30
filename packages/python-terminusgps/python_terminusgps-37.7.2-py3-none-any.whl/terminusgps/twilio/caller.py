import asyncio
from typing import Any

import twilio.rest
from django.conf import settings
from loguru import logger
from twilio.http.async_http_client import AsyncTwilioHttpClient


class TwilioCaller:
    def __init__(
        self,
        client_sid: str | None = None,
        client_token: str | None = None,
        from_number: str | None = None,
        messaging_sid: str | None = None,
        log_level: int = 10,
        log_days: int = 10,
    ) -> None:
        """
        Sets Twilio client session variables.

        All parameters are optional, default values are pulled from a Django settings module.

        :param client_sid: A Twilio client session id.
        :type client_sid: :py:obj:`str` | :py:obj:`None`
        :param client_token: A Twilio client API token.
        :type client_token: :py:obj:`str` | :py:obj:`None`
        :param from_number: Phone number used to send notifications.
        :type from_number: :py:obj:`str` | :py:obj:`None`
        :param messaging_sid: A Twilio client messaging service session id.
        :type messaging_sid: :py:obj:`str` | :py:obj:`None`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        logger.add(
            f"logs/{self.__class__.__name__}.log",
            level=log_level,
            retention=f"{log_days} days",
        )
        self._client_sid = client_sid or settings.TWILIO_SID
        self._client_token = client_token or settings.TWILIO_TOKEN
        self._from_number = from_number or settings.TWILIO_FROM_NUMBER
        self._messaging_sid = messaging_sid or settings.TWILIO_MESSAGING_SID

    def __enter__(self) -> "TwilioCaller":
        """Opens a context manager and creates an asyncronous Twilio client."""
        self.client = twilio.rest.Client(
            self.client_sid, self._client_token, http_client=AsyncTwilioHttpClient()
        )
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        """Closes the context manager."""
        return None

    def create_notification(
        self, to_number: str, message: str, method: str = "sms"
    ) -> asyncio.Task[Any]:
        """
        Returns an awaitable notification task.

        Valid methods are ``"sms"``, ``"call"`` and ``"phone"``.

        :param to_number: A phone number to notify.
        :type to_number: :py:obj:`str`
        :param message: A notification message.
        :type message: :py:obj:`str`
        :param method: A notification method. Default is ``"sms"``.
        :type method: :py:obj:`str`
        :raises ValueError: If ``method`` is invalid.
        :returns: An awaitable task.
        :rtype: :py:obj:`~asyncio.Task`

        """
        match method:
            case "sms":
                return asyncio.create_task(
                    self.create_sms(to_number=to_number, message=message)
                )
            case "call" | "phone":
                return asyncio.create_task(
                    self.create_call(to_number=to_number, message=message)
                )
            case _:
                raise ValueError(f"Unsupported TwilioCaller method '{method}'.")

    async def create_call(self, to_number: str, message: str) -> None:
        """
        Calls ``to_number`` and reads ``message`` aloud.

        :param to_number: A phone number.
        :type to_number: :py:obj:`str`
        :param message: A message to be read aloud.
        :type message: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        logger.info("Creating a call notification...")
        logger.debug(f"Reading '{message}' to '{to_number}'...")
        await self.client.calls.create_async(
            to=to_number,
            from_=self.from_number,
            twiml=f"<Response><Say>{message}</Say></Response>",
        )

    async def create_sms(self, to_number: str, message: str) -> None:
        """
        Texts ``message`` to ``to_number``.

        :param to_number: A phone number.
        :type to_number: :py:obj:`str`
        :param message: A message to be texted.
        :type message: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        logger.info("Creating an sms notification...")
        logger.debug(f"Texting '{message}' to '{to_number}'...")
        await self.client.messages.create_async(
            to=to_number,
            from_=self.from_number,
            body=message,
            messaging_service_sid=self.messaging_sid,
        )

    @property
    def client_sid(self) -> str:
        """
        Client session id.

        :type: :py:obj:`str`

        """
        return self._client_sid

    @property
    def from_number(self) -> str:
        """
        Origin phone number.

        :type: :py:obj:`str`

        """
        return self._from_number

    @property
    def messaging_sid(self) -> str:
        """
        Messaging service session id.

        :type: :py:obj:`str`

        """
        return self._messaging_sid
