from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ErrorNotImplemented(Exception):
    pass


class CRMLeadLine(models.Model):
    _inherit = "crm.lead.line"

    is_multimedia = fields.Boolean(
        compute="_compute_is_multimedia",
        store=True,
    )

    @api.depends("product_id")
    def _compute_is_multimedia(self):
        service_multimedia = self.env.ref(
            "multimedia_somconnexio.multimedia_service", raise_if_not_found=False
        )
        if not service_multimedia:
            # If the main multimedia service is not found,
            # set all lines to not multimedia
            for record in self:
                record.is_multimedia = False
            return
        for record in self:
            record.is_multimedia = (
                service_multimedia.id == record.product_id.categ_id.parent_id.id
            )

    def create_multimedia_contract(self):
        """
        Create a multimedia contract from a lead line
        """

        if not self.is_multimedia:
            raise ValidationError(_("This lead line is not a multimedia service."))

        contract_vals = self._prepare_multimedia_contract_vals()
        contract = self.env["contract.contract"].create(contract_vals)

        return contract

    def _prepare_multimedia_contract_vals(self):
        """
        Prepare the values for creating a multimedia contract.
        as paramether.
        :return: Dictionary of values for the contract creation.
        """

        partner = self.lead_id.partner_id
        mandate = partner.get_mandate(self.iban.replace(" ", "").upper())
        partner_email = partner.get_or_create_contract_email(self.lead_id.email_from)
        service_supplier_id = self._get_service_supplier()
        contract_line = {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "date_start": fields.Date.today(),
        }

        return {
            "name": "Multimedia Contract - {}".format(self.id),
            "partner_id": self.lead_id.partner_id.id,
            "mandate_id": mandate.id,
            "email_ids": [(4, partner_email.id, False)],
            "service_technology_id": self.env.ref(
                "multimedia_somconnexio.service_technology_multimedia"
            ).id,
            "service_supplier_id": service_supplier_id.id,
            "payment_mode_id": self.env.ref("somconnexio.payment_mode_inbound_sepa").id,
            "contract_line_ids": [(0, False, contract_line)],
        }

    def _get_service_supplier(self):
        """
        Get the service supplier for the multimedia contract.
        This needs to overridden in subclasses to provide specific suppliers.
        :return: Service supplier record (or raise an error if not implemented).
        """
        raise ErrorNotImplemented()
