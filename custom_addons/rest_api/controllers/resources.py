# -*- coding: utf-8 -*-
from . import auth

from . import model__account_invoice       # need install 'account' module
from . import model__account_invoice_line  # need install 'account' module
from . import model__product_template      # need install 'product' module
from . import model__report
from . import model__res_partner
from . import model__sale_order            # need install 'sale' module
from . import model__sale_order_line       # need install 'sale' module
from . import model__stock_picking
from  .import model__res_users
from  .import model__sales_sales
from .import model__knowledge_knowledge
from .import model__project_issue
from .import model__feedback_feedback
from .import model__slide_slide
from .import model__about_about
from .import model__stock_production_lot
from .import model__project_defect
from .import model__motor_motor
from .import model__product_type
from .import model__model_type
from .import model__product_product
from .import model__account_journal
from .import model__producttypes_producttypes
from .import model__productsale_productsale
from .import model__productvarient_productvarient
from .import model__productname_productname
from .import model__dealer_sale
from .import model__dealer_feedback
from .import model__spo
from .import model__partorder
from .import model__model
from .import model__management
from .import model__revenue_3
from .import model__top_selling_agent
from .import model__general_ledger
from .import model__move_line
from .import model__trial_balance_report_wizard
from .import model__trial_balance
from .import model__api1
from .import model__lastyear
from .import model__lastmonth
from .import model__product_dashboard
from .import model__dashboard1
from .import model__vendor_exp
from .import model__customerexpense
from .import model__trial_quatar
from .import model__project_issue_new
from .import model__project_task_new
from .import model__project_drop
from .import model__project_dashboard_count
from .import model__project_partner
from .import model__product_stage
from .import model__account_account
from .import model__mp3get
from .import model__company_name
from .import model__res_company
from .import model__res_user_role
from .import model__project_issue_goutam
from .import model__global_crm
from .import model__global_partner
from .import model__global_task
from .import model__global_issue
from .import model__resuser
from .import model__external_upload_chartofaccount
from .import model__contact_count
from .import model__ticket_count
from .import model__pipeline_count
from .import model__crm_stage
from .import model__crm_team
from .import model__source
from .import model__campaigns
# from .import model__address_address
from .import model__crm_activity
from .import model__project_tags
from .import model__res_users1
from .import model__res_country1
from .import model__res_country_state1
from .import model__complain
from .import model_trial_balance_api
from .import model__slide_category
from .import model__slide_tag
from .import model__category_crm
from .import model__subcategory_crm
from .import model__slide_channel
from .import model__teamleader
from .import model__group_contact
from .import model__apis
from .import model__meeting
from .import model__mail_channel  #get channel details
from .import model__mail_message
from .import model__chatmessage   #send message to channel
from .import model__call_log
from .import model__channel_channel
from .import model__api_notification
from .import model__mail_message_log
from .import model__api_log_sowtex
from .import module__ticket_dashboard85
from .import model__slide_count
from .import model__stage_count
from .import model__Faq__api
from .import message_get_api_view
from .import model__featured_api_bimabachat
from .import model__partner ###res.partner2 ye count wali
from .import model__crm_lead_new
from .import model__designation
from .import model__nature
from .import model__country
from .import model__state
from .import model__city
from .import model__claim_bimabachat
from .import model__version
from .import sowtex_corn_jobs_overdue
from .import sowtex_next_activity_cron_job
from .import bimabachat_crm_lead #bimabachat
from .import bimabachat_project_project  #bimabachat
from .import bimabachat_utm_medium  #bimabachat
from .import bimabachat_utm_source  #bimabachat
from .import bimbachat_utm_campaign  #bimabachat
from .import bimabachat_project_issue  #bimabachat
from .import bimabachat_crm_team  #bimabachat
from .import bimabachat_crm_tags  #bimabachat
from .import bimabachat_res_partner  #bimabachat
from .import bimabachat_res_tags  #bimabachat
from .import bimabachat_res_title  #bimabachat
from .import bimabachat_team_wise_api_query  #bimabachat
from .import model__bimabachat_chat #bimabachat
from .import log_api_sowtex_sowtex_web_sanket
from .import model__ikinaki_product_template #ikinaki
from .import sowtex_res_partner #sowtex partner count wali hai ye
from .import model__faq_bimabachat
from .import model__feature_bimabachat
from .import model__bimabachat_claim
from .import elsedecor_product #elshomedecor
from .import elshome__expense_account #elshomedecor
from .import elshome_account_tax #elshomedecor
from .import elshome_assets_type #elshomedecor
from .import elshome_gsthsn #elshomedecor
from .import elshome_income_account #elshomedecor
from .import elshome_internalcat #elshomedecor
from .import elshome_procurement_location #elshomedecor
from .import elshome_productdrop #elshomedecor
from .import elshome_public_categ #elshomedecor
from .import elshome_route #elshomedecor
from .import elshome_uom #elshomedecor
from .import elshome_website_style #elshomedecor
from .import model__gst_r2_books #gst r2 to akshay
from .import model__gstr2_books
from .import product_elsdecor_internal #els prouct detail
from .import bimabachat__stage_count
from .import bimabachat_slide_count_by_channel
from .import bimabachat_slide_slide_count
from .import bimabachat_slide_api_aman
from .import bimabachat_corn_brithday #cronjobapi
from .import bimabachat_next_activity  #cronjobapi
from .import bimabachat_overdues  #cronjobapi
from .import moashk_next_activity
from .import moashk_overdues
from .import moashk_birthday_cron
from .import bimabachat_sales_manager #cron_dales_manager
from .import bimabachat_next_activity_manager #cron_dales_manager
from .import moashk_sales_manager #cron_dales_manager
from .import bimabacht_warning_activity
from .import bimabacht_danger_activity
from .import bimabachat_customer_res_partner
from .import bimabachat_category_count
from .import model__url
from .import jcc_slides_slides #jcc slides
from .import authcontroller #jcc signup
from .import bimabachat_today_activities #jcc signup
from .import bimabachat_md_report
from .import model__customer_filter
from .import bimabachat_attachment #attachment_uploaded
from .import bimabachat_crm_lead_post