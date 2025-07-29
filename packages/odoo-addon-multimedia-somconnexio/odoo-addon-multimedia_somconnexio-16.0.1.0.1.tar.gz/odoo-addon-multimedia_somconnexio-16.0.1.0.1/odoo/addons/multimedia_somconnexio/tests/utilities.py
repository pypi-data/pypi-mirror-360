def gen_multimedia_streaming_product(env):
    return env["product.product"].create(
        {
            "name": "Test Product Multimedia",
            "showed_name": "Test Product Multimedia",
            "product_tmpl_id": env.ref(
                "multimedia_somconnexio.streaming_product_template"
            ).id,
            "default_code": "test_multimedia_product",
            "custom_name": "Test Product Multimedia",
            "public": True,
        }
    )


def gen_multimedia_contract(env):
    return env["contract.contract"].create(
        {
            "name": "Test Contract Multimedia",
            "partner_id": env.ref("somconnexio.res_partner_1_demo").id,
            "service_partner_id": env.ref("somconnexio.res_partner_1_demo").id,
            "invoice_partner_id": env.ref("somconnexio.res_partner_1_demo").id,
            "service_supplier_id": env.ref(
                "multimedia_somconnexio.service_supplier_multimedia"
            ).id,
            "service_technology_id": env.ref(
                "multimedia_somconnexio.service_technology_multimedia"
            ).id,
            "payment_mode_id": env.ref("somconnexio.payment_mode_inbound_sepa").id,
            "mandate_id": env.ref("somconnexio.demo_mandate_partner_1_demo").id,
            "recurring_invoicing_type": "post-paid",
            "subscription_code": "MMS0001",
        }
    )
