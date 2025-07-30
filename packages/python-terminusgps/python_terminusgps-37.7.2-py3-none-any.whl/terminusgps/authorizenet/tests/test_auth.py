from unittest import TestCase

from authorizenet.apicontractsv1 import merchantAuthenticationType
from authorizenet.constants import constants
from django.test import override_settings

from terminusgps.authorizenet import auth

TEST_MERCHANT_AUTH_LOGIN_ID = "test_id"
TEST_MERCHANT_AUTH_TRANSACTION_KEY = "test_key"


class MerchantAuthenticationTestCase(TestCase):
    @override_settings(
        MERCHANT_AUTH_LOGIN_ID=TEST_MERCHANT_AUTH_LOGIN_ID,
        MERCHANT_AUTH_TRANSACTION_KEY=TEST_MERCHANT_AUTH_TRANSACTION_KEY,
        DEBUG=True,
    )
    def test_merchant_authentication_init(self) -> None:
        auth_obj = auth.get_merchant_auth()
        self.assertIsInstance(auth_obj, merchantAuthenticationType)
        self.assertTrue(auth_obj.name == TEST_MERCHANT_AUTH_LOGIN_ID)
        self.assertTrue(auth_obj.transactionKey == TEST_MERCHANT_AUTH_TRANSACTION_KEY)


class ValidationModeTestCase(TestCase):
    @override_settings(DEBUG=True)
    def test_validation_mode_debug_enabled(self) -> None:
        self.assertTrue(auth.get_validation_mode() == "testMode")

    @override_settings(DEBUG=False)
    def test_validation_mode_debug_disabled(self) -> None:
        self.assertTrue(auth.get_validation_mode() == "liveMode")


class EnvironmentTestCase(TestCase):
    @override_settings(DEBUG=True)
    def test_environment_debug_enabled(self) -> None:
        self.assertTrue(auth.get_environment() == constants.SANDBOX)

    @override_settings(DEBUG=False)
    def test_environment_debug_disabled(self) -> None:
        self.assertTrue(auth.get_environment() == constants.PRODUCTION)
