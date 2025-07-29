from odoo import models


class CreateLeadFromPartner(models.TransientModel):
    _inherit = "partner.create.lead.wizard"

    def _get_available_product_templates(self):
        """Get available product templates based on the selected product category.
        If is multimedia service, it returns all product templates related to
        child categories from the multimedia category."""

        multimedia_categ_id = self.env.ref("multimedia_somconnexio.multimedia_service")

        if self.product_categ_id == multimedia_categ_id:
            service_product_templates = self.env["product.template"].search(
                [
                    ("categ_id", "child_of", multimedia_categ_id.id),
                ]
            )
            return service_product_templates
        return super()._get_available_product_templates()
