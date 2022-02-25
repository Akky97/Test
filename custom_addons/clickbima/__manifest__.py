# -*- coding: utf-8 -*-
{
    'name': "clickbima",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','infotype','date_range','product','crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/infosubdataname.xml',
        'views/templates.xml',
        'views/insur.xml',
        # 'views/contact_creation.xml',
        'views/info_data.xml',
        'views/infodata1.xml',
        'views/info_sub_data.xml',
        'views/insurer_tem_master.xml',
        'views/registry_data.xml',
        'views/template_master.xml',
        'report/bussiness_template.xml',
        'report/generalreport.xml',
        'wizard/create_report.xml',
        'wizard/business_summary.xml',
        'wizard/register_detail.xml',
        'wizard/business_detail.xml',
        'wizard/idra_non_lifetop10_client.xml',
        'wizard/idra_general_business.xml',
        'wizard/compare_business_report.xml',
        'wizard/idra_non_lifeinsurer_wise.xml',
        'wizard/irda_claims_summary.xml',
        'wizard/idra_claim_detail_report.xml',
        'wizard/irda_claims_settled_ageing.xml',
        'wizard/irda_claims_pending_ageing.xml',
        'wizard/renewal_report.xml',
        'wizard/message.xml',
        'wizard/policy_detail_report.xml',
        # 'wizard/business_detail_comparison.xml',
        'wizard/business_comparison_detail.xml',
        'wizard/brokerage_report.xml',
        'wizard/client_portfolio_view.xml',
        'views/country_code.xml',
        'views/terr_premium.xml',
        'views/tp_preimum.xml',
        # 'views/sale_country_code.xml',
        # 'views/policy_country_code.xml',
        # 'views/res_country_code.xml',
        # 'wizard/create_pdf_report.xml',

        # 'views/mapping.xml',
        # 'views/mappingsm.xml',
        # 'views/mappingpos.xml',
        # 'views/mappingclient.xml',
        # 'views/poscreation.xml',
        # 'views/empcreation.xml',
        # 'views/clientcreation.xml',
        # 'views/clientgroupcreation.xml',
        # 'views/mappingclientgroup.xml',
        'views/policy_transaction.xml',
        'views/insurerbranch.xml',
        # 'views/policy.xml',
        'views/idra.xml',
        'views/orc.xml',
        'views/fyyear.xml',
        # 'views/cobroker.xml',
        'views/declaration.xml',
        'views/endur.xml',
        'views/coinsurance.xml',
        'views/cdacc.xml',
        'views/decal.xml',
        # 'views/claim.xml',
        # 'views/lortem.xml',
        # 'views/tpamaster.xml',
        # 'views/survemaster.xml',
        # 'views/disstatus.xml',
        # 'views/policystats.xml',
        # 'views/detailregis.xml',
        # 'views/uploaddata.xml',
        # 'views/renewal.xml',
        # 'views/filemanage.xml',
        'views/poliseg.xml',
        # 'views/subdata_drop_down.xml',
        # 'views/schememaster.xml',
        'views/header_mark.xml',
        'views/gsttax.xml',
        'views/claim_view.xml',
        'views/reconcile.xml',



    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}