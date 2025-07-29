{
    "name": "multimedia_somconnexio",
    "version": "16.0.1.0.1",
    "depends": ["somconnexio", "product_product_sale_subscription_template"],
    "summary": """
        Sets a basic structure for multimedia subscriptions within the SomConnexio ERP
    """,
    "author": "Coopdevs Treball SCCL, " "Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "category": "Cooperative management",
    "data": [
        "data/product_attribute.xml",
        "data/product_attribute_value.xml",
        "data/product_category.xml",
        "data/product_template.xml",
        "data/product_template_attribute_line.xml",
        "data/service_technology.xml",
        "security/ir.model.access.csv",
        "views/contract_views.xml",
        "views/product_views.xml",
        "views/crm_lead.xml",
        "views/crm_lead_line.xml",
        "wizards/crm_lead_add_multimedia_line/crm_lead_add_multimedia_line.xml",
    ],
    "demo": [
        "demo/service_supplier.xml",
        "demo/service_technology_service_supplier.xml",
    ],
}
