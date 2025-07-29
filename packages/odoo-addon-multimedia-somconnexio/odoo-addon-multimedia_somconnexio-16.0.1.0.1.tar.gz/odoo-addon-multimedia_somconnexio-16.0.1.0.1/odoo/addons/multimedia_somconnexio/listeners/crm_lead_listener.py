from odoo.addons.component.core import Component


class CrmLeadListener(Component):
    _name = "multimedia.crm.lead.listener"
    _inherit = "crm.lead.listener"

    def on_record_write(self, record, fields=None):
        """
        This method is triggered when a CRM lead record is written.
        It checks if the lead is in the 'won' stage and has multimedia technology.
        If so, it creates a multimedia contract for the lead line.
        Except if the the lead also has a fiber technology line, when it
        does not create the multimedia contract.
        """

        super().on_record_write(record, fields)
        won_stage = self.env.ref("crm.stage_lead4")

        if "stage_id" in fields and record.stage_id == won_stage:
            mm_lines = record.lead_line_ids.filtered(lambda line: line.is_multimedia)
            fiber_lines = record.lead_line_ids.filtered(lambda line: line.is_fiber)
            if mm_lines and not fiber_lines:
                for mm_line in mm_lines:
                    # Create multimedia contract for each multimedia lead line
                    mm_line.with_delay().create_multimedia_contract()
