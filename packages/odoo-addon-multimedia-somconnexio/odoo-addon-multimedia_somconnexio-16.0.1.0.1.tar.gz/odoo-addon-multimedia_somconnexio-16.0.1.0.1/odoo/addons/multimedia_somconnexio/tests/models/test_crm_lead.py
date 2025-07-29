from odoo.addons.somconnexio.tests.sc_test_case import SCTestCase
from ..helper_service import crm_lead_create


class TestCRMLead(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")
        self.mm_lead = crm_lead_create(self.env, self.partner_id, "multimedia")

    def test_has_multimedia_lead_line(self):
        """
        Test that a multimedia CRM lead has a multimedia lead line.
        """
        self.assertTrue(self.mm_lead.multimedia_lead_line_ids)
        self.assertTrue(self.mm_lead.has_multimedia_lead_lines)

    def test_does_not_have_multimedia_lead_line(self):
        """
        Test that a fiber CRM lead does not have multimedia lines.
        """
        fiber_lead = crm_lead_create(self.env, self.partner_id, "fiber")
        self.assertFalse(fiber_lead.multimedia_lead_line_ids)
        self.assertFalse(fiber_lead.has_multimedia_lead_lines)

    def test_has_single_fiber_lead_line(self):
        """
        Test that a fiber CRM lead with a single fiber lead line has the
        has_single_fiber_lead_line field set to True.
        """
        fiber_lead = crm_lead_create(self.env, self.partner_id, "fiber")
        self.assertEqual(len(fiber_lead.lead_line_ids), 1)
        self.assertTrue(fiber_lead.lead_line_ids[0].is_fiber)
        self.assertTrue(fiber_lead.has_single_fiber_lead_line)

        # Add a second lead line to the fiber lead
        fiber_lead.lead_line_ids += self.mm_lead.lead_line_ids
        self.assertEqual(len(fiber_lead.lead_line_ids), 2)
        self.assertFalse(fiber_lead.has_single_fiber_lead_line)
