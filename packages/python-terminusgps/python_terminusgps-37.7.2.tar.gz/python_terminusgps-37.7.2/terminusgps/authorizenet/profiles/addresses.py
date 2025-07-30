from authorizenet import apicontractsv1, apicontrollers

from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.profiles.base import AuthorizenetSubProfileBase


class AddressProfile(AuthorizenetSubProfileBase):
    """An Authorizenet customer address profile."""

    def create(self, address: apicontractsv1.customerAddressType) -> int:
        """
        Creates the customer shipping address profile in Authorizenet.

        :param address: A customer address.
        :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :returns: An address profile id.
        :rtype: :py:obj:`int`

        """
        return int(
            self._authorizenet_create_shipping_address(address).find(
                f"{ANET_XMLNS}customerAddressId"
            )
        )

    def update(self, address: apicontractsv1.customerAddressType) -> None:
        """
        Updates the customer shipping address to the new address in Authorizenet.

        :param address: A customer address.
        :type address: :py:obj:`~authorizenet.apicontractsv1.customerAddressType`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_update_shipping_address(address)

    def delete(self) -> None:
        """
        Deletes the customer address profile in Authorizenet and sets :py:attr:`id` to :py:obj:`None` if :py:attr:`id` is set.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.id:
            self._authorizenet_delete_shipping_address()
            self.id = None

    def _authorizenet_get_shipping_address(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.getCustomerShippingAddressRequest` using the Authorizenet API.

        `getCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-shipping-address>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AssertionError: If :py:attr:`customerProfileId` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' wasn't set."
        assert self.customerProfileId, "'customerProfileId' wasn't set."

        request = apicontractsv1.getCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerAddressId=self.id,
        )

        return self.execute_controller(
            apicontrollers.getCustomerShippingAddressController(request)
        )

    def _authorizenet_create_shipping_address(
        self, address: apicontractsv1.customerAddressType
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.createCustomerShippingAddressRequest` using the Authorizenet API.

        `createCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-shipping-address>`_

        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        request = apicontractsv1.createCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            address=address,
            defaultShippingAddress=self.default,
        )

        return self.execute_controller(
            apicontrollers.createCustomerShippingAddressController(request)
        )

    def _authorizenet_update_shipping_address(
        self, address: apicontractsv1.customerAddressType
    ) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.updateCustomerShippingAddressRequest` using the Authorizenet API.

        `updateCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-shipping-address>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AssertionError: If :py:attr:`customerProfileId` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' wasn't set."
        assert self.customerProfileId, "'customerProfileId' wasn't set."

        address.customerAddressId = self.id
        request = apicontractsv1.updateCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            address=address,
            default=self.default,
        )

        return self.execute_controller(
            apicontrollers.updateCustomerShippingAddressController(request)
        )

    def _authorizenet_delete_shipping_address(self) -> dict | None:
        """
        Executes a :py:obj:`~authorizenet.apicontractsv1.deleteCustomerShippingAddressRequest` using the Authorizenet API.

        `deleteCustomerShippingAddressRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-shipping-address>`_

        :raises AssertionError: If :py:attr:`id` wasn't set.
        :raises AssertionError: If :py:attr:`customerProfileId` wasn't set.
        :raises ControllerExecutionError: If something goes wrong during an Authorizenet API call.
        :returns: An Authorizenet API response, if any.
        :rtype: :py:obj:`dict` | :py:obj:`None`

        """
        assert self.id, "'id' wasn't set."
        assert self.customerProfileId, "'customerProfileId' wasn't set."

        request = apicontractsv1.deleteCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=self.customerProfileId,
            customerAddressId=self.id,
        )

        return self.execute_controller(
            apicontrollers.deleteCustomerShippingAddressController(request)
        )
