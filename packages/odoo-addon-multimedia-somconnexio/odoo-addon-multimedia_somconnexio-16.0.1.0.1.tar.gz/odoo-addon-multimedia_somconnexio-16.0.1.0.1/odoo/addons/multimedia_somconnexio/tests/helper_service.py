from faker import Faker
import random
from odoo.addons.somconnexio.tests.helper_service import (
    crm_lead_create as _crm_lead_create,
    random_mobile_phone,
)
from .utilities import gen_multimedia_streaming_product

faker = Faker("es_CA")


def crm_lead_create(
    odoo_env,
    partner_id,
    service_category,
    portability=False,
):
    if service_category != "multimedia":
        return _crm_lead_create(odoo_env, partner_id, service_category, portability)
    crm_lead_line = _mm_crm_lead_line_create(odoo_env, partner_id)
    crm_lead = odoo_env["crm.lead"].create(
        {
            "name": "Test Lead",
            "partner_id": partner_id.id,
            "phone": random_mobile_phone(),
            "email_from": faker.email(),
            "stage_id": odoo_env.ref("crm.stage_lead1").id,
        }
    )
    crm_lead.lead_line_ids = [(4, crm_lead_line.id)]

    return crm_lead


def _mm_crm_lead_line_create(odoo_env, partner_id):
    iban = random.choice(partner_id.bank_ids.mapped("sanitized_acc_number"))
    mm_product = _search_or_gen_multimedia_streaming_product(odoo_env)
    crm_lead_line_args = {
        "name": "CRM Lead",
        "iban": iban,
        "product_id": mm_product.id,
    }

    return odoo_env["crm.lead.line"].create(crm_lead_line_args)


def _search_or_gen_multimedia_streaming_product(odoo_env):
    """
    Search for an existing multimedia streaming product or
    generate a new one if it doesn't exist.
    """
    mm_product_tmpl = odoo_env.ref(
        "multimedia_somconnexio.streaming_product_template",
    )
    product = odoo_env["product.product"].search(
        [
            (
                "product_tmpl_id",
                "=",
                mm_product_tmpl.id,
            )
        ],
        limit=1,
    )
    if not product:
        product = gen_multimedia_streaming_product(odoo_env)
    return product
