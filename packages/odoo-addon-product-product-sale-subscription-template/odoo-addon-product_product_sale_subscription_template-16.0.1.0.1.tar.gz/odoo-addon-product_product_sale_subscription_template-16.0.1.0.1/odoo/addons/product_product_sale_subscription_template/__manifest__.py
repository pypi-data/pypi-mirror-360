{
    "name": "product_product_sale_subscription_template",
    "version": "16.0.1.0.1",
    "depends": ["somconnexio", "subscription_oca"],
    "summary": """
        Sets a basic structure for multimedia subscriptions within the SomConnexio ERP
    """,
    "author": "Coopdevs Treball SCCL, " "Som Connexió SCCL",
    "website": "https://coopdevs.org",
    "license": "AGPL-3",
    "category": "Cooperative management",
    "data": [
        "views/product_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
