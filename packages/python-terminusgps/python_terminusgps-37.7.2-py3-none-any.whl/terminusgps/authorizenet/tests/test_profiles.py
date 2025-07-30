from unittest import TestCase
from uuid import uuid4

from authorizenet import apicontractsv1

from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)


class CustomerProfileTestCase(TestCase):
    def setUp(self) -> None:
        self.test_merchant_id = str(uuid4())[:13]
        self.test_email = f"{self.test_merchant_id}@domain.com"
        self.test_desc = f"{self.test_merchant_id} Description"
        self.test_customer_profile = CustomerProfile(
            id=None,
            merchant_id=self.test_merchant_id,
            email=self.test_email,
            desc=self.test_desc,
        )

    def tearDown(self) -> None:
        self.test_customer_profile.delete()

    def test_customer_profile_init(self) -> None:
        """Fails if :py:attr:`email`, :py:attr:`desc` or :py:attr:`merchantCustomerId` weren't set properly."""
        self.assertTrue(self.test_customer_profile.email == self.test_email)
        self.assertTrue(self.test_customer_profile.desc == self.test_desc)
        self.assertTrue(self.test_customer_profile.merchant_id == self.test_merchant_id)

    def test_customer_profile_generate_customer_profile_type(self) -> None:
        """Fails if :py:meth:`_generate_customer_profile_type` returns an object of the wrong type."""
        profile_obj = self.test_customer_profile._generate_customer_profile_type()
        self.assertIsInstance(profile_obj, apicontractsv1.customerProfileType)

    def test_customer_profile_generate_customer_profile_ex_type(self) -> None:
        """Fails if :py:meth:`_generate_customer_profile_ex_type` returns an object of the wrong type."""
        profile_obj = self.test_customer_profile._generate_customer_profile_ex_type()
        self.assertIsInstance(profile_obj, apicontractsv1.customerProfileExType)

    def test_customer_profile_required_attributes_unset(self) -> None:
        """Fails if :py:exec:`AssertionError` is not raised when attempting to create a customer profile without setting required attributes."""
        test_profile = CustomerProfile(id=None, merchant_id=None, email=None, desc=None)
        with self.assertRaises(AssertionError) as context:
            test_profile.create()
        self.assertTrue(
            "Neither 'merchantCustomerId' nor 'email' were set."
            in str(context.exception)
        )

    def test_customer_profile_email_only(self) -> None:
        """Fails if a customer profile isn't created with just an email provided."""
        test_profile = CustomerProfile(
            id=None, merchant_id=None, email="test@domain.com", desc=None
        )
        self.assertIsNotNone(test_profile.id)
        test_profile.delete()

    def test_customer_profile_merchant_id_only(self) -> None:
        """Fails if a customer profile isn't created with just a merchant id provided."""
        test_profile = CustomerProfile(
            id=None, merchant_id=str(uuid4())[:13], email=None, desc=None
        )
        self.assertIsNotNone(test_profile.id)
        test_profile.delete()
        self.assertIsNone(test_profile.id)


class AddressProfileTestCase(TestCase):
    def setUp(self) -> None:
        self.test_merchant_id = str(uuid4())[:13]
        self.test_email = f"{self.test_merchant_id}@domain.com"
        self.test_desc = f"{self.test_merchant_id} Description"
        self.test_customer_profile = CustomerProfile(
            id=None,
            merchant_id=self.test_merchant_id,
            email=self.test_email,
            desc=self.test_desc,
        )
        self.test_address_obj = apicontractsv1.customerAddressType(
            firstName="TestFirst",
            lastName="TestLast",
            company="TestCompany",
            address="123 Main St.",
            city="Houston",
            state="TX",
            zip=str(77065),
            country="US",
            phoneNumber="555-555-5555",
        )

    def tearDown(self) -> None:
        self.test_customer_profile.delete()

    def test_address_profile_create(self) -> None:
        """Fails if an address profile is not properly created in Authorizenet."""
        test_address_profile = AddressProfile(
            id=None, customer_profile_id=self.test_customer_profile.id, default=True
        )
        test_address_profile.id = test_address_profile.create(self.test_address_obj)
        self.assertIsNotNone(test_address_profile.id)

    def test_address_profile_delete(self) -> None:
        """Fails if an address profile is not properly deleted in Authorizenet."""
        test_address_profile = AddressProfile(
            id=None, customer_profile_id=self.test_customer_profile.id
        )
        test_address_profile.id = test_address_profile.create(self.test_address_obj)
        test_address_profile.delete()
        self.assertIsNone(test_address_profile.id)


class PaymentProfileTestCase(TestCase):
    def setUp(self) -> None:
        self.test_merchant_id = str(uuid4())[:13]
        self.test_email = f"{self.test_merchant_id}@domain.com"
        self.test_desc = f"{self.test_merchant_id} Description"
        self.test_customer_profile = CustomerProfile(
            id=None,
            merchant_id=self.test_merchant_id,
            email=self.test_email,
            desc=self.test_desc,
        )
        self.test_address_obj = apicontractsv1.customerAddressType(
            firstName="TestFirst",
            lastName="TestLast",
            company="TestCompany",
            address="123 Main St.",
            city="Houston",
            state="TX",
            zip=str(77065),
            country="US",
            phoneNumber="555-555-5555",
        )
        self.test_payment_obj = apicontractsv1.paymentType(
            creditCard=apicontractsv1.creditCardType(
                cardNumber="4111111111111111", expirationDate="04-99", cardCode="444"
            )
        )

    def tearDown(self) -> None:
        self.test_customer_profile.delete()

    def test_payment_profile_create(self) -> None:
        """Fails if a payment profile is not properly created in Authorizenet."""
        test_payment_profile = PaymentProfile(
            id=None,
            customer_profile_id=str(self.test_customer_profile.id),
            default=True,
        )
        test_payment_profile.id = test_payment_profile.create(
            address=self.test_address_obj, payment=self.test_payment_obj
        )
        self.assertIsNotNone(test_payment_profile.id)

    def test_payment_profile_delete(self) -> None:
        """Fails if a payment profile is not properly deleted in Authorizenet."""
        test_payment_profile = PaymentProfile(
            id=None,
            customer_profile_id=str(self.test_customer_profile.id),
            default=True,
        )
        test_payment_profile.id = test_payment_profile.create(
            address=self.test_address_obj, payment=self.test_payment_obj
        )
        test_payment_profile.delete()
        self.assertIsNone(test_payment_profile.id)

    def test_payment_profile_last_4(self) -> None:
        """Fails if a payment profile's last 4 credit card digits are not properly retrieved."""
        test_payment_profile = PaymentProfile(
            id=None,
            customer_profile_id=str(self.test_customer_profile.id),
            default=True,
        )
        test_payment_profile.id = test_payment_profile.create(
            address=self.test_address_obj, payment=self.test_payment_obj
        )
        self.assertTrue(test_payment_profile.last_4, "1111")
