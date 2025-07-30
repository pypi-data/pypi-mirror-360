from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class PaymentProfile(AuthorizenetSubProfileBase):
    """An Authorizenet customer payment profile."""

    @property
    def last_4(self) -> int | None:
        """
        Last 4 digits of the payment profile credit card.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        if self.id:
            cc_num = (
                self._authorizenet_get_payment_profile()
                .find(f"{ANET_XMLNS}paymentProfile")
                .find(f"{ANET_XMLNS}payment")
                .find(f"{ANET_XMLNS}creditCard")
                .find(f"{ANET_XMLNS}cardNumber")
            )  # returns string like: "XXXX<last_4>"
            return int(cc_num.text[-4:]) if cc_num is not None else None

    def create(
        self,
        address: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> int:
        """
        Creates the customer payment profile in Authorizenet.

        :param address: A customer address.
        :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :returns: A customer payment profile id.
        :rtype: :py:obj:`int`

        """
        return int(
            self._authorizenet_create_payment_profile(
                address=address, payment=payment
            ).find(f"{ANET_XMLNS}customerPaymentProfileId")
        )

    def update(
        self,
        address: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> None:
        """
        Updates the customer payment profile in Authorizenet if :py:attr:`id` is set.

        :param address: A customer address.
        :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_update_payment_profile(address, payment)

    def delete(self) -> None:
        """
        Deletes the customer payment profile in Authorizenet and sets :py:attr:`id` to :py:obj:`None` if :py:attr:`id` is set.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_delete_payment_profile()
            self.id = None

    def _authorizenet_get_transaction_list_for_customer(
        self,
        limit: int = 100,
        ordering: str = "submitTimeUTC",
        offset: int = 1,
        descending: bool = False,
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getTransactionListForCustomerRequest` using the Authorizenet API.

        `getTransactionListForCustomerRequest <https://developer.authorize.net/api/reference/index.html#transaction-reporting-get-transaction-list>`_

        :param limit: Total number of transactions to retrieve. Default is ``100``.
        :type limit: :py:obj:`int`
        :param ordering: A field to order the transactions by. Default is ``"submitTimeUTC"``.
        :type ordering: :py:obj:`str`
        :param offset: Page of the response to retrieve.
        :type offset: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param descending: Sort the results in descending order.
        :type descending: :py:obj:`bool`
        :raises ValueError: If ``ordering`` is invalid.
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        ordering_options: tuple[str, str] = ("id", "submitTimeUTC")
        if ordering not in ordering_options:
            raise ValueError(
                f"'ordering' must be one of {ordering_options}, got '{ordering}'."
            )

        request = apicontractsv1.getTransactionListForCustomerRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
            sorting={"orderBy": ordering, "orderDescending": str(descending).lower()},
            paging={"limit": str(limit), "offset": str(offset)},
        )

        return self.execute_controller(
            apicontrollers.getTransactionListForCustomerController(request)
        )

    def _authorizenet_create_payment_profile(
        self,
        address: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerPaymentProfileRequest` using the Authorizenet API.

        `createCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-payment-profile>`_

        :param address: A billing address.
        :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment method.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.createCustomerPaymentProfileRequest(
            customerProfileId=self.customerProfileId,
            merchantAuthentication=self.merchantAuthentication,
            paymentProfile=apicontractsv1.customerPaymentProfileType(
                billTo=address, payment=payment, defaultPaymentProfile=self.default
            ),
            validationMode=self.validationMode,
        )

        return self.execute_controller(
            apicontrollers.createCustomerPaymentProfileController(request)
        )

    def _authorizenet_get_payment_profile(
        self, issuer_info: bool = True
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerPaymentProfileRequest` using the Authorizenet API.

        `getCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-payment-profile>`_

        :param issuer_info: Whether or not to include issuer information in the response. Default is :py:obj:`True`.
        :type issuer_info: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.getCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
            includeIssuerInfo=str(issuer_info).lower(),
        )

        return self.execute_controller(
            apicontrollers.getCustomerPaymentProfileController(request)
        )

    def _authorizenet_update_payment_profile(
        self,
        address: apicontractsv1.customerAddressType,
        payment: apicontractsv1.paymentType,
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.updateCustomerPaymentProfileRequest` using the Authorizenet API.

        `updateCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-payment-profile>`_

        :param address: A customer address.
        :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :param payment: A payment method.
        :type payment: :py:obj:`~authorizenet.apicontractsv1.paymentType`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.updateCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            paymentProfile=apicontractsv1.customerPaymentProfileType(
                billTo=address,
                payment=payment,
                defaultPaymentProfile=self.default,
                customerPaymentProfileId=self.id,
            ),
            validationMode=self.validationMode,
        )

        return self.execute_controller(
            apicontrollers.updateCustomerPaymentProfileController(request)
        )

    def _authorizenet_validate_payment_profile(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.validateCustomerPaymentProfileRequest` using the Authorizenet API.

        `validateCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-validate-customer-payment-profile>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`


        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.validateCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
            validationMode=self.validationMode,
        )

        return self.execute_controller(
            apicontrollers.validateCustomerPaymentProfileController(request)
        )

    def _authorizenet_delete_payment_profile(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerPaymentProfileRequest` using the Authorizenet API.

        `deleteCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-payment-profile>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.deleteCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerPaymentProfileId=self.id,
        )

        return self.execute_controller(
            apicontrollers.deleteCustomerPaymentProfileController(request)
        )
