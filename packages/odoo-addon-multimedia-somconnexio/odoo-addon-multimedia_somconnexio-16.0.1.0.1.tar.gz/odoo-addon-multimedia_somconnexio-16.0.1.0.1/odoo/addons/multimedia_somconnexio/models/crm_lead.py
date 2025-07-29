from odoo import models, fields, api


class CRMLead(models.Model):
    _inherit = "crm.lead"

    multimedia_lead_line_ids = fields.One2many(
        "crm.lead.line",
        string="Multimedia lead lines",
        compute="_compute_mms_lead_line_ids",
    )
    has_multimedia_lead_lines = fields.Boolean(
        compute="_compute_has_mms_lead_lines", store=True
    )
    has_single_fiber_lead_line = fields.Boolean(
        compute="_compute_has_single_fiber_lead_line",
    )

    @api.depends("lead_line_ids")
    def _compute_mms_lead_line_ids(self):
        for crm in self:
            crm.multimedia_lead_line_ids = crm.lead_line_ids.filtered(
                lambda p: p.is_multimedia
            )

    @api.depends("multimedia_lead_line_ids")
    def _compute_has_mms_lead_lines(self):
        for crm in self:
            crm.has_multimedia_lead_lines = bool(crm.multimedia_lead_line_ids)

    @api.depends("lead_line_ids")
    def _compute_has_single_fiber_lead_line(self):
        """Check if there is a single fiber lead line in the lead."""
        for crm in self:
            crm.has_single_fiber_lead_line = (
                len(crm.lead_line_ids) == 1 and crm.lead_line_ids[0].is_fiber
            )
