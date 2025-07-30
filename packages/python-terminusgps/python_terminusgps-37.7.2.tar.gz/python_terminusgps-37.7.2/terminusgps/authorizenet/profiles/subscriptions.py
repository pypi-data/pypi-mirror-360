import decimal

from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.constants import (
    ANET_XMLNS,
    AuthorizenetSubscriptionStatus,
)
from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class SubscriptionProfile(AuthorizenetSubProfileBase):
    """An Authorizenet subscription profile."""

    @property
    def name(self) -> str | None:
        """
        The subscription name.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        if self.id:
            name = (
                self._authorizenet_get_subscription()
                .find(f"{ANET_XMLNS}subscription")
                .find(f"{ANET_XMLNS}name")
            )
            return str(name) if name is not None else None

    @property
    def amount(self) -> decimal.Decimal | None:
        """
        The subscription amount.

        :type: :py:obj:`~decimal.Decimal` | :py:obj:`None`

        """
        if self.id:
            amount = (
                self._authorizenet_get_subscription()
                .find(f"{ANET_XMLNS}subscription")
                .find(f"{ANET_XMLNS}amount")
            )
            decimal.getcontext().prec = 4
            return decimal.Decimal(float(amount)) * 1 if amount is not None else None

    @property
    def status(self) -> AuthorizenetSubscriptionStatus | None:
        """
        Current subscription status.

        :type: :py:obj:`~terminusgps.authorizenet.constants.AuthorizenetSubscriptionStatus` | :py:obj:`None`

        """
        if self.id:
            status = self._authorizenet_get_subscription_status().find(
                f"{ANET_XMLNS}status"
            )
            return (
                AuthorizenetSubscriptionStatus(status) if status is not None else None
            )

    @property
    def transactions(self) -> list[dict[str, str]]:
        """
        Subscription transaction list.

        :type: :py:obj:`list`

        """
        if not self.id:
            return []

        subscription = self._authorizenet_get_subscription(
            include_transactions=True
        ).find(f"{ANET_XMLNS}subscription")

        transactions = (
            subscription.find(f"{ANET_XMLNS}arbTransactions")
            if subscription is not None
            else None
        )
        return (
            transactions.findall(f"{ANET_XMLNS}arbTransaction")
            if transactions is not None
            else []
        )

    @property
    def address_id(self) -> int | None:
        """
        Subscription address id.

        :type: :py:obj:`int` | :py:obj:`None`

        """
        if self.id:
            address_id = (
                self._authorizenet_get_subscription()
                .find(f"{ANET_XMLNS}subscription")
                .find(f"{ANET_XMLNS}profile")
                .find(f"{ANET_XMLNS}shippingProfile")
                .find(f"{ANET_XMLNS}customerAddressId")
            )
            return int(address_id) if address_id is not None else None

    @property
    def payment_id(self) -> int | None:
        """
        Subscription payment id.

        :type: :py:obj:`int` | :py:obj:`None`

        """
        if self.id:
            payment_id = (
                self._authorizenet_get_subscription()
                .find(f"{ANET_XMLNS}subscription")
                .find(f"{ANET_XMLNS}profile")
                .find(f"{ANET_XMLNS}paymentProfile")
                .find(f"{ANET_XMLNS}customerPaymentProfileId")
            )
            return int(payment_id) if payment_id is not None else None

    def create(self, subscription: apicontractsv1.ARBSubscriptionType) -> int:
        """
        Creates a subscription in Authorizenet.

        :param subscription: A subscription.
        :type subscription: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: A subscription id.
        :rtype: :py:obj:`int`

        """
        return int(
            self._authorizenet_create_subscription(subscription).find(
                f"{ANET_XMLNS}subscriptionId"
            )
        )

    def update(self, subscription: apicontractsv1.ARBSubscriptionType) -> None:
        """
        Updates a subscription in Authorizenet if :py:attr:`id` is set.

        :param subscription: A subscription.
        :type subscription: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_update_subscription(subscription)

    def delete(self) -> None:
        """
        Deletes (cancels) a subscription in Authorizenet if :py:attr:`id` is set.

        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_cancel_subscription()

    def _authorizenet_create_subscription(
        self, subscription: apicontractsv1.ARBSubscriptionType
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.ARBCreateSubscriptionRequest` using the Authorizenet API.

        `ARBCreateSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-create-a-subscription-from-customer-profile>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.ARBCreateSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication,
            subscription=subscription,
        )

        return self.execute_controller(
            apicontrollers.ARBCreateSubscriptionController(request)
        )

    def _authorizenet_get_subscription(
        self, include_transactions: bool = False
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.ARBGetSubscriptionRequest` using the Authorizenet API.

        `ARBGetSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-get-subscription>`_

        :param include_transactions: Whether or not to include subscription transactions in the Authorizenet API response. Default is :py:obj:`False`.
        :type include_transaction: :py:obj:`bool`
        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.ARBGetSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication,
            subscriptionId=self.id,
            includeTransactions=str(include_transactions).lower(),
        )

        return self.execute_controller(
            apicontrollers.ARBGetSubscriptionController(request)
        )

    def _authorizenet_get_subscription_status(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.ARBGetSubscriptionStatusRequest` using the Authorizenet API.

        `ARBGetSubscriptionStatusRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-get-subscription-status>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.ARBGetSubscriptionStatusRequest(
            merchantAuthentication=self.merchantAuthentication, subscriptionId=self.id
        )

        return self.execute_controller(
            apicontrollers.ARBGetSubscriptionStatusController(request)
        )

    def _authorizenet_update_subscription(
        self, subscription: apicontractsv1.ARBSubscriptionType
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.ARBUpdateSubscriptionRequest` using the Authorizenet API.

        `ARBUpdateSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-update-a-subscription>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.ARBUpdateSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication,
            subscriptionId=self.id,
            subscription=subscription,
        )

        return self.execute_controller(
            apicontrollers.ARBUpdateSubscriptionController(request)
        )

    def _authorizenet_cancel_subscription(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.ARBCancelSubscriptionRequest` using the Authorizenet API.

        `ARBCancelSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-cancel-a-subscription>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' was not set."

        request = apicontractsv1.ARBCancelSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication, subscriptionId=self.id
        )

        return self.execute_controller(
            apicontrollers.ARBCancelSubscriptionController(request)
        )
