from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_multimedia = fields.Boolean(
        string="Is Multimedia",
        compute="_compute_is_multimedia",
        default=False,
    )

    def _compute_is_multimedia(self):
        main_multimedia_service = self.env.ref(
            "multimedia_somconnexio.multimedia_service", raise_if_not_found=False
        )
        if not main_multimedia_service:
            # If the main multimedia service is not found,
            # set all products to not multimedia
            for product in self:
                product.is_multimedia = False

        all_multimedia_categories = self.env["product.category"].search(
            [("id", "child_of", main_multimedia_service.id)]
        )
        for product in self:
            product_category = product.product_tmpl_id.categ_id
            if product_category:
                product.is_multimedia = product_category in all_multimedia_categories
            else:
                product.is_multimedia = False
