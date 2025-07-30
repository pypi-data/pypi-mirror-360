from authorizenet import apicontractsv1

from terminusgps.authorizenet.auth import get_merchant_auth, get_validation_mode
from terminusgps.authorizenet.controllers import AuthorizenetControllerExecutor


class AuthorizenetProfileBase(AuthorizenetControllerExecutor):
    """Base class for Authorizenet profiles."""

    def __init__(self, id: int | str | None = None, *args, **kwargs) -> None:
        """
        Sets :py:attr:`id` if provided.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.id = id

    def __str__(self) -> str:
        """
        Returns a string representation of the profile, if :py:attr:`id` was set.

        :returns: A string in the format '#id' where 'id' is the profile's Authorizenet generated id number, or a blank string if :py:attr:`id` wasn't set.
        :rtype: :py:obj:`str`

        """
        return f"#{self.id}" if self.id else ""

    @property
    def id(self) -> str | None:
        """
        An Authorizenet generated id.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        return self._id

    @id.setter
    def id(self, other: int | str | None) -> None:
        """
        Sets :py:attr:`id` to ``other``.

        :raises ValueError: If ``other`` was provided as a string containing non-digit characters.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if isinstance(other, str) and not other.isdigit():
            raise ValueError(f"'id' can only contain digit characters, got '{other}'.")
        self._id = str(other) if other is not None else None

    @property
    def merchantAuthentication(self) -> apicontractsv1.merchantAuthenticationType:
        """
        A merchant authentication object to authenticate Authorizenet API calls.

        :returns: A merchant authentication object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.merchantAuthenticationType`

        """
        return get_merchant_auth()

    @property
    def validationMode(self) -> str:
        """
        The current Authorizenet API validation mode.

        :returns: An Authorizenet API validation mode string.
        :rtype: :py:obj:`str`

        """
        return get_validation_mode()


class AuthorizenetSubProfileBase(AuthorizenetProfileBase):
    """Base class for Authorizenet 'sub-profiles', profiles that have an associated customer profile."""

    def __init__(
        self,
        customer_profile_id: int | str,
        id: int | str | None = None,
        default: bool = False,
    ) -> None:
        """
        Sets :py:attr:`customerProfileId` for the sub-profile.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        super().__init__(id=id)
        self.customerProfileId = customer_profile_id
        self.default = default

    @property
    def customerProfileId(self) -> str:
        """
        A customer profile id.

        :type: :py:obj:`str`

        """
        return str(self._customerProfileId)

    @customerProfileId.setter
    def customerProfileId(self, other: int | str) -> None:
        """
        Sets :py:attr:`customerProfileId` to ``other``.

        :raises ValueError: If the new customer profile id is a string that contains non-digits.
        :param other: A new customer profile id.
        :type other: :py:obj:`int` | :py:obj:`str`

        """
        if isinstance(other, str) and not other.isdigit():
            raise ValueError(
                f"'customerProfileId' can only contain digits, got '{other}'."
            )
        self._customerProfileId = str(other)

    @property
    def default(self) -> str:
        """
        Whether or not the sub-profile is set as default.

        :type: :py:obj:`str`

        """
        return str(self._default).lower()

    @default.setter
    def default(self, other: bool) -> None:
        """Sets :py:attr:`default` to ``other``."""
        self._default = other
