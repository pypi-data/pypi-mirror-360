from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.auth import get_validation_mode
from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.profiles.base import AuthorizenetProfileBase


class CustomerProfile(AuthorizenetProfileBase):
    """An Authorizenet customer profile."""

    def __init__(
        self,
        id: int | str | None = None,
        merchant_id: str | None = None,
        email: str | None = None,
        desc: str | None = None,
    ) -> None:
        """
        Sets :py:attr:`merchant_id`, :py:attr:`email` and :py:attr:`desc`.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        super().__init__(id=id)
        self._merchant_id = merchant_id
        self._email = email
        self._desc = desc

    @property
    def merchant_id(self) -> str:
        """
        A merchant designated id.

        :type: :py:obj:`str`

        """
        if self.id or self._email and not self._merchant_id:
            self._merchant_id = (
                self._authorizenet_get_customer_profile()
                .find(f"{ANET_XMLNS}profile")
                .find(f"{ANET_XMLNS}merchantCustomerId")
            )
        return str(self._merchant_id)

    @merchant_id.setter
    def merchant_id(self, other: str | int) -> None:
        self._merchant_id = other
        self._authorizenet_update_customer_profile()

    @property
    def email(self) -> str:
        """
        A customer email address.

        :type: :py:obj:`str`

        """
        if self.id or self._merchant_id and not self._email:
            self._email = (
                self._authorizenet_get_customer_profile()
                .find(f"{ANET_XMLNS}profile")
                .find(f"{ANET_XMLNS}email")
            )
        return str(self._email)

    @email.setter
    def email(self, other: str) -> None:
        self._email = other
        self._authorizenet_update_customer_profile()

    @property
    def desc(self) -> str:
        """
        A customer profile description.

        :type: :py:obj:`str`

        """
        if self.id or self._merchant_id or self._email and not self._desc:
            self._desc = (
                self._authorizenet_get_customer_profile()
                .find(f"{ANET_XMLNS}profile")
                .find(f"{ANET_XMLNS}description")
            )
        return str(self._desc)

    @desc.setter
    def desc(self, other: str) -> None:
        self._desc = other
        self._authorizenet_update_customer_profile()

    @property
    def validationMode(self) -> str:
        """
        The current Authorizenet validation mode.

        :type: :py:obj:`str`

        """
        return get_validation_mode()

    def create(self) -> int:
        """
        Creates the customer profile in Authorizenet.

        :raises AssertionError: If neither :py:attr:`merchant_id` nor :py:attr:`email` were set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An id for the new customer profile.
        :rtype: :py:obj:`int`

        """
        assert self.merchant_id or self.email, (
            "Neither 'merchant_id' nor 'email' were set."
        )
        return int(
            self._authorizenet_create_customer_profile().find(
                f"{ANET_XMLNS}customerProfileId"
            )
        )

    def update(self) -> None:
        """
        Updates the customer profile in Authorizenet if :py:attr:`id` is set.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_update_customer_profile()

    def delete(self) -> None:
        """
        Deletes the customer profile in Authorizenet and sets :py:attr:`id` to :py:obj:`None` if :py:attr:`id` is set.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_delete_customer_profile()
            self.id = None

    def get_payment_profile_ids(self) -> list[int]:
        """
        Returns a list of payment profile ids assigned to the customer profile.

        :returns: A list of payment profile ids.
        :rtype: :py:obj:`list`

        """
        payment_profiles = (
            self._authorizenet_get_customer_profile()
            .find(f"{ANET_XMLNS}profile")
            .findall(f"{ANET_XMLNS}paymentProfiles")
        )
        return (
            [
                int(profile.find(f"{ANET_XMLNS}customerPaymentProfileId"))
                for profile in payment_profiles
            ]
            if payment_profiles is not None
            else []
        )

    def get_address_profile_ids(self) -> list[int]:
        """
        Returns a list of address profile ids assigned to the customer profile.

        :returns: A list of address profile ids.
        :rtype: :py:obj:`list`

        """
        address_profiles = (
            self._authorizenet_get_customer_profile()
            .find(f"{ANET_XMLNS}profile")
            .find(f"{ANET_XMLNS}shipToList")
        )
        return (
            [
                int(profile.find(f"{ANET_XMLNS}customerAddressId"))
                for profile in address_profiles
            ]
            if address_profiles is not None
            else []
        )

    def _get_id(self) -> int:
        return int(
            self._authorizenet_get_customer_profile()
            .find(f"{ANET_XMLNS}profile")
            .find(f"{ANET_XMLNS}customerProfileId")
        )

    def _generate_customer_profile_ex_type(
        self,
    ) -> apicontractsv1.customerProfileExType:
        """
        Generates and returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileExType`.

        :returns: A customer profile object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.customerProfileExType`

        """
        cprofile_obj = apicontractsv1.customerProfileExType()

        if self.id:
            cprofile_obj.customerProfileId = self.id
        if self.merchant_id:
            cprofile_obj.merchantCustomerId = self.merchant_id
        if self.email:
            cprofile_obj.email = self.email
        if self.desc:
            cprofile_obj.description = self.desc

        return cprofile_obj

    def _generate_customer_profile_type(self) -> apicontractsv1.customerProfileType:
        """
        Generates and returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileType`.

        :returns: A customer profile object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.customerProfileType`

        """
        cprofile_obj = apicontractsv1.customerProfileType()

        if self._merchant_id:
            cprofile_obj.merchantCustomerId = self._merchant_id
        if self._email:
            cprofile_obj.email = self._email
        if self._desc:
            cprofile_obj.description = self._desc

        return cprofile_obj

    def _authorizenet_get_customer_profile(
        self, issuer_info: bool = True
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerProfileRequest` using the Authorizenet API.

        `getCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-profile>`_

        :param issuer_info: Whether or not to include issuer info in the response. Default is :py:obj:`True`.
        :type issuer_info: :py:obj:`bool`
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.getCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            includeIssuerInfo=str(issuer_info).lower(),
        )

        if self.id:
            request.customerProfileId = self.id
        if self._merchant_id:
            request.merchantCustomerId = self._merchant_id
        if self._email:
            request.email = self._email

        return self.execute_controller(
            apicontrollers.getCustomerProfileController(request)
        )

    def _authorizenet_create_customer_profile(
        self, validate: bool = False
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerProfileRequest` using the Authorizenet API.

        `createCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-profile>`_

        :param validate: Whether or not to validate the customer profile in Authorizenet.
        :type validate: :py:obj:`bool`
        :raises AssertionError: If neither :py:attr:`merchantCustomerId` nor :py:attr:`email` were set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.merchant_id or self.email, (
            "Neither 'merchant_id' nor 'email' were set."
        )

        request = apicontractsv1.createCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=self._generate_customer_profile_type(),
        )
        if validate:
            request.validationMode = self.validationMode

        return self.execute_controller(
            apicontrollers.createCustomerProfileController(request)
        )

    def _authorizenet_update_customer_profile(
        self, validate: bool = False
    ) -> dict | None:
        """
        Executes an :py:obj:`~authorizenet.apicontractsv1.updateCustomerProfileRequest` using the Authorizenet API.

        `updateCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-profile>`_

        :param validate: Whether or not to validate the customer profile in Authorizenet.
        :type validate: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.updateCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=self._generate_customer_profile_ex_type(),
        )
        if validate:
            request.validationMode = self.validationMode

        return self.execute_controller(
            apicontrollers.updateCustomerProfileController(request)
        )

    def _authorizenet_delete_customer_profile(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerProfileRequest` using the Authorizenet API.

        `deleteCustomerProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-profile>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.id,
        )

        return self.execute_controller(
            apicontrollers.deleteCustomerProfileController(request)
        )
