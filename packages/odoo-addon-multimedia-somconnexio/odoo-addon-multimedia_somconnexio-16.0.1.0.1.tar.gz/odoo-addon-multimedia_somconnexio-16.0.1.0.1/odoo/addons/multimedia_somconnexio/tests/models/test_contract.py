from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from ..utilities import gen_multimedia_contract


class TestContract(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.contract = gen_multimedia_contract(self.env)

    def test_contract_name(self):
        self.assertEqual(self.contract.name, f"MEDIA - {self.contract.id}")

    def test_contract_type(self):
        self.assertEqual(self.contract.service_contract_type, "multimedia")

    def test_phone_number(self):
        self.assertEqual(self.contract.phone_number, "-")

    def test_multimedia_contract_to_dict(self):
        self.assertEqual(
            self.contract._to_dict()["subscription_technology"], "multimedia"
        )
