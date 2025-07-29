from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from ..helper_service import crm_lead_create
from ..utilities import gen_multimedia_streaming_product


class TestCRMLeadAddMultimediaLine(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.mm_product_id = gen_multimedia_streaming_product(self.env)

    def test_create_line(self):
        fiber_crm_lead = crm_lead_create(
            self.env, self.partner_id, "fiber", portability=False
        )

        self.assertFalse(fiber_crm_lead.has_multimedia_lead_lines)

        wizard_vals = {
            "product_id": self.mm_product_id.id,
            "bank_id": self.partner_id.bank_ids.id,
        }
        wizard = (
            self.env["crm.lead.add.multimedia.line.wizard"]
            .with_context(active_id=fiber_crm_lead.id)
            .create(wizard_vals)
        )

        self.assertEqual(wizard.crm_lead_id, fiber_crm_lead)
        self.assertEqual(wizard.partner_id, self.partner_id)

        wizard.button_create()

        self.assertTrue(fiber_crm_lead.has_multimedia_lead_lines)

        self.assertEqual(len(fiber_crm_lead.multimedia_lead_line_ids), 1)

        crm_lead_line = fiber_crm_lead.multimedia_lead_line_ids[0]

        self.assertEqual(
            crm_lead_line.iban,
            self.partner_id.bank_ids.sanitized_acc_number,
        )
