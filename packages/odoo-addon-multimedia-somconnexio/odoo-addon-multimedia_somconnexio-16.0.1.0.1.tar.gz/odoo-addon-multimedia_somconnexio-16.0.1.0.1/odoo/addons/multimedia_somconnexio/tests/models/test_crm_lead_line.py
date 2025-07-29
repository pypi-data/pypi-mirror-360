from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from odoo.exceptions import ValidationError
from ...models.crm_lead_line import ErrorNotImplemented
from ..helper_service import crm_lead_create


class CRMLeadLineTest(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.mm_lead = crm_lead_create(self.env, self.partner_id, "multimedia")

    def test_mms_lead_line_creation_ok(self):
        mms_crm_lead_line = self.mm_lead.lead_line_ids[0]
        self.assertTrue(mms_crm_lead_line.id)
        self.assertTrue(mms_crm_lead_line.is_multimedia)

    def test_create_multimedia_contract(self):
        """
        Test, on its own, this module cannot create a multimedia contract
        from a CRM lead line, since no service supplier is provided.
        """
        mms_crm_lead_line = self.mm_lead.lead_line_ids[0]
        mms_crm_lead_line.iban = self.partner_id.bank_ids[0].acc_number

        self.assertRaises(
            ErrorNotImplemented, mms_crm_lead_line.create_multimedia_contract
        )

    def test_create_multimedia_contract_non_multimedia_lead(self):
        """
        Test that a ValidationError raises when calling
        create_multimedia_contact with a non multimedia lead line.
        """
        fiber_crm_lead = crm_lead_create(
            self.env,
            self.partner_id,
            "fiber",
            portability=False,
        )
        crm_lead_line = fiber_crm_lead.lead_line_ids[0]

        self.assertRaisesRegex(
            ValidationError,
            "This lead line is not a multimedia service.",
            crm_lead_line.create_multimedia_contract,
        )
