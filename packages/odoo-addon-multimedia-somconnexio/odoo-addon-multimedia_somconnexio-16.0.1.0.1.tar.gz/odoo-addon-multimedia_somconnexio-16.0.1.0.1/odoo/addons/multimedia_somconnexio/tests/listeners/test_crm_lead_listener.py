from odoo.addons.multimedia_somconnexio.tests.helper_service import crm_lead_create
from odoo.addons.somconnexio.tests.sc_test_case import SCComponentTestCase


class TestCRMLeadListener(SCComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCRMLeadListener, cls).setUpClass()
        # disable tracking test suite wise
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                test_queue_job_no_delay=False,
            )
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.partner_id = self.browse_ref("somconnexio.res_partner_2_demo")

        self.fiber_crm_lead = crm_lead_create(
            self.env, self.partner_id, "fiber", portability=True
        )
        self.mm_crm_lead = crm_lead_create(self.env, self.partner_id, "multimedia")
        self.fiber_crm_lead.action_set_remesa()
        self.mm_crm_lead.action_set_remesa()
        self.jobs_domain = [
            ("method_name", "=", "create_multimedia_contract"),
            ("model_name", "=", "crm.lead.line"),
        ]

    def test_multimedia_lead_on_record_validate(self):
        """
        Test that the listener correctly creates a multimedia contract
        when the lead is won and has multimedia technology.
        """
        queued_jobs_before = self.env["queue.job"].search(self.jobs_domain)

        self.mm_crm_lead.action_set_won()

        queued_jobs_after = self.env["queue.job"].search(self.jobs_domain)
        self.assertEqual(len(queued_jobs_before), len(queued_jobs_after) - 1)

    def test_fiber_lead_on_record_validate(self):
        """
        Test that the listener does not create a multimedia contract
        when the lead is won and does not have multimedia technology.
        """
        queued_jobs_before = self.env["queue.job"].search(self.jobs_domain)

        self.fiber_crm_lead.action_set_won()

        queued_jobs_after = self.env["queue.job"].search(self.jobs_domain)

        self.assertEqual(len(queued_jobs_before), len(queued_jobs_after))

    def test_mixed_lead_on_record_validate(self):
        """
        Test that the listener does not create a multimedia contract
        when the lead is won and has a multimedia line with a fiber.
        """
        queued_jobs_before = self.env["queue.job"].search(self.jobs_domain)

        self.assertEqual(len(self.mm_crm_lead.lead_line_ids), 1)

        # Add a fiber lead line to the multimedia lead
        self.mm_crm_lead.lead_line_ids |= self.fiber_crm_lead.lead_line_ids[0]

        self.assertEqual(len(self.mm_crm_lead.lead_line_ids), 2)

        self.mm_crm_lead.action_set_won()

        queued_jobs_after = self.env["queue.job"].search(self.jobs_domain)

        self.assertEqual(len(queued_jobs_before), len(queued_jobs_after))
