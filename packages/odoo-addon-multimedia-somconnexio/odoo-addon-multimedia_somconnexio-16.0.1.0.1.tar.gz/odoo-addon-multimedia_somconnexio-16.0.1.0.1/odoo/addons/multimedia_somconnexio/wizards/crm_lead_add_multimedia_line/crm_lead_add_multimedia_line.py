from odoo import api, fields, models


class CRMLeadAddMultimediaLine(models.TransientModel):
    _name = "crm.lead.add.multimedia.line.wizard"
    crm_lead_id = fields.Many2one("crm.lead")

    @api.model
    def _product_id_domain(self):
        multimedia_categ_id = self.env.ref("multimedia_somconnexio.multimedia_service")
        service_product_templates = self.env["product.template"].search(
            [
                ("categ_id", "child_of", multimedia_categ_id.id),
            ]
        )
        return [("product_tmpl_id", "in", service_product_templates.ids)]

    product_id = fields.Many2one(
        "product.product",
        string="Requested product",
        required=True,
        domain=_product_id_domain,
    )
    partner_id = fields.Many2one("res.partner")
    bank_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        required=True,
    )

    def button_create(self):
        self.ensure_one()
        lead_line = self.env["crm.lead.line"].create(
            {
                "name": self.product_id.name,
                "product_id": self.product_id.id,
                "iban": self.bank_id.sanitized_acc_number,
            }
        )
        self.crm_lead_id.write({"lead_line_ids": [(4, lead_line.id, 0)]})
        return True

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        crm_lead_id = self.env["crm.lead"].browse(self.env.context["active_id"])
        defaults["crm_lead_id"] = crm_lead_id.id
        defaults["partner_id"] = crm_lead_id.partner_id.id
        return defaults
