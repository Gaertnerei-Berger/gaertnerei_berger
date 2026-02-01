app_name = "suppliercatalog"
app_title = "Suppliercatalog"
app_publisher = "Gärtnerei Berger"
app_description = "All Items from a Supplier"
app_email = "info@gaertnerei-berger.de"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "suppliercatalog",
# 		"logo": "/assets/suppliercatalog/logo.png",
# 		"title": "Suppliercatalog",
# 		"route": "/suppliercatalog",
# 		"has_permission": "suppliercatalog.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/suppliercatalog/css/custom.css"
# app_include_js = "/assets/suppliercatalog/js/custom.js"

# include js, css files in header of web template
# web_include_css = "/assets/suppliercatalog/css/suppliercatalog.css"
# web_include_js = "/assets/suppliercatalog/js/suppliercatalog.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "suppliercatalog/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {
	"Supplier Catalog Item" : "public/js/supplier_catalog_item_list.js"
}
doctype_js = {
    "Purchase Receipt": "public/js/purchase_receipt.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "suppliercatalog/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "suppliercatalog.utils.jinja_methods",
# 	"filters": "suppliercatalog.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "suppliercatalog.install.before_install"
# after_install = "suppliercatalog.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "suppliercatalog.uninstall.before_uninstall"
# after_uninstall = "suppliercatalog.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "suppliercatalog.utils.before_app_install"
# after_app_install = "suppliercatalog.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "suppliercatalog.utils.before_app_uninstall"
# after_app_uninstall = "suppliercatalog.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "suppliercatalog.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

#doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_trash": "method"
# 		"on_cancel": "methode"
#
#	}
# }

doc_events = {
    "Item Price": {
        "validate": "suppliercatalog.utils.item_price_cal.custom_validate"
    },

    "Item Price": {
        "on_update": "suppliercatalog.german_accounting.utils.price_list_calculation.on_update",
    },

    "Item": {
        "validate": "suppliercatalog.utils.item_price_cal.update_item_prices_on_factor_change"
    },

    "Supplier": {
        "after_insert": "suppliercatalog.german_accounting.utils.creditor_debitor.after_insert",
        "after_delete": "suppliercatalog.german_accounting.utils.creditor_debitor.after_delete"
    },

    "Customer": {
        "after_insert": "suppliercatalog.german_accounting.utils.creditor_debitor.after_insert",
        "after_delete": "suppliercatalog.german_accounting.utils.creditor_debitor.after_delete"
    },
    
}

#    "Item Price": {
#        "on_update": "suppliercatalog.price_calculation.hooks.price_list_calculation.on_item_price_update"
#    },

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"suppliercatalog.tasks.all"
# 	],
# 	"daily": [
# 		"suppliercatalog.tasks.daily"
# 	],
# 	"hourly": [
# 		"suppliercatalog.tasks.hourly"
# 	],
# 	"weekly": [
# 		"suppliercatalog.tasks.weekly"
# 	],
# 	"monthly": [
# 		"suppliercatalog.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "suppliercatalog.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "suppliercatalog.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "suppliercatalog.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["suppliercatalog.utils.before_request"]
# after_request = ["suppliercatalog.utils.after_request"]

# Job Events
# ----------
# before_job = ["suppliercatalog.utils.before_job"]
# after_job = ["suppliercatalog.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"suppliercatalog.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures = [
    # Master Data (unverändert)
    {"dt": "Supplier Quality"},
    {"dt": "Trade Class"},
    {"dt": "Pfand Typen"},
    {"dt": "UOM"},

    # Custom Fields – vollständiges, explizites Superset
    {
        "dt": "Custom Field",
        "filters": [
            [
                "dt",
                "in",
                [
                    # Suppliercatalog / bisher exportiert
                    "Supplier Catalog Item",
                    "Supplier Catalog Settings",
                    "Item",
                    "Item Price",
                    "Purchase Receipt",

                    # German Accounting
                    "Price List Calculation Settings",
                    "German Accounting Settings",
                    "Sales Invoice",
                ]
            ]
        ]
    },

    # Property Setters – identisches Superset
    {
        "dt": "Property Setter",
        "filters": [
            [
                "doc_type",
                "in",
                [
                    # Suppliercatalog / bisher exportiert
                    "Supplier Catalog Item",
                    "Supplier Catalog Settings",
                    "Item",
                    "Item Price",
                    "Purchase Receipt",

                    # German Accounting
                    "Price List Calculation Settings",
                    "German Accounting Settings",
                    "Sales Invoice",
                ]
            ]
        ]
    },
]
