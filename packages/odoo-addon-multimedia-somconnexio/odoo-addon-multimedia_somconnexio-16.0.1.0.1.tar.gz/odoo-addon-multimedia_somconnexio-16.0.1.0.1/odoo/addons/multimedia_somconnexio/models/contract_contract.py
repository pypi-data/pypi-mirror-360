from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    subscription_code = fields.Char(
        string="Subscription Code",
        readonly=True,
        help="Subscription code for FILMIN",
    )

    @api.depends("service_contract_type")
    def _compute_phone_number(self):
        super(Contract, self)._compute_phone_number()
        multimedia_technology = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        )
        for contract in self:
            if contract.service_technology_id == multimedia_technology:
                contract.phone_number = "-"

    @api.depends("phone_number")
    def _compute_name(self):
        """This method should be overriden for each multimedia child module
        to a set a meaningfull name for the specific contract"""
        super(Contract, self)._compute_name()
        multimedia_technology = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        )
        for contract in self:
            if contract.service_technology_id == multimedia_technology:
                contract.name = f"MEDIA - {contract.id}"

    @api.depends("service_technology_id")
    def _compute_contract_type(self):
        super(Contract, self)._compute_contract_type()
        multimedia_technology = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        )
        for record in self:
            if record.service_technology_id == multimedia_technology:
                record.service_contract_type = "multimedia"

    def _tariff_contract_line(self, field, current):
        super(Contract, self)._tariff_contract_line(field, current)

        multimedia_technology = self.env.ref(
            "multimedia_somconnexio.service_technology_multimedia"
        )
        for contract in self:
            if contract.service_technology_id != multimedia_technology:
                continue

            for line in contract.contract_line_ids:
                main_multimedia_service = self.env.ref(
                    "multimedia_somconnexio.multimedia_service"
                )
                all_multimedia_categories = self.env["product.category"].search(
                    [("id", "child_of", main_multimedia_service.id)]
                )

                if line.product_id.categ_id in all_multimedia_categories and (
                    contract._is_contract_line_active(line) or not current
                ):
                    setattr(contract, field, line)
                    break

    def _get_subscription_tech(self):
        """overrides method that inform subscription_technology in _to_dict parent"""
        return (
            self.service_contract_type
            if self.service_contract_type == "multimedia"
            else super()._get_subscription_tech()
        )
