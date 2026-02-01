import frappe
import re
from frappe import _


# Gets the Company to set the Creditor or Debitor right
def after_insert(doc, method):
    company = getattr(doc, 'company', None)
    if not company:
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    create_and_link_credit_account(doc, company)

# To get the right most int from the Namingseries for creating the account nummber
def get_int_from_namingseries(value):
    match = re.search(r'(\d+)$', str(value))
    return int(match.group(1)) if match else None

# Links the created Acc to the right Supplier
def create_and_link_credit_account(doc, company):
    create_credit_account = frappe.db.get_single_value("German Accounting Settings", "auto_creditor")

    if create_credit_account:
        credit_account = create_credit_account_for_supplier(doc, company)

        if not credit_account:
            return

        # Calculates the creditor number
        debtor_creditor_number = get_int_from_namingseries(doc.name) + 7000

        account_doc = frappe.new_doc("Party Account")
        account_doc.update({
            "parent": doc.name,
            "company": company,
            "account": credit_account,
            "debtor_creditor_number":debtor_creditor_number,
            "parenttype": "Supplier",
            "parentfield": "accounts"
        })
        account_doc.insert(ignore_permissions=True)



def create_credit_account_for_supplier(doc, company):
    #Checks if Parent Account is set else Error
    parent_account = frappe.db.get_single_value("German Accounting Settings", "creditor_parent_acc")

    if not parent_account:
        frappe.log_error(
            _("Failed to create Credit Account for supplier {} as no Creditors Parent Account is setup in the {}"
              .format(
                  frappe.utils.get_link_to_form("Supplier", doc.name),
                  frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings")
              )),
            _("failed to create supplier credit account")
        )
        frappe.throw(
            _("Failed to create Credit Account for this supplier, please set up Creditors Parent Account in {}.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        return None

    # Gets  Namingsereis as int
    supplier_number =  get_int_from_namingseries(doc.name)

    #Checks if Int in Namingsereis else Error
    if supplier_number is None:
        frappe.throw(
            _("Failed to create Credit Account please deaktivate Function in {} and Contact your Advisor!!!.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        frappe.log_error(
            _("Failed to create Credit Account for supplier no Namingseries with Integers set for Supplier")
        )
        return None

    #Checks if Int is to big for Accounts Limit 29999
    if supplier_number > 29999:
        frappe.throw(
            _("Failed to create Credit Account please deaktivate Function in {} and Contact your Advisor!!!.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        frappe.log_error(
            _("Contact your Tax Consultant and System Advisor Account Supplier Limit reached")
        )
        return None
    
    # Calculates the Account Number und gets the Account Name
    account_account_number = supplier_number + 70000
    account_account_name = doc.supplier_name

    # Checks if the Account exists and if not it gets created, after that its retuned to get matched to the right doc
    try:
        existing_account = frappe.db.exists("Account", {
            "account_number": account_account_number,
            "company": company
        })
        if existing_account:
            return existing_account

        new_account_doc = frappe.get_doc({
            'doctype': 'Account',
            'account_name': account_account_name,
            'account_number': account_account_number,
            'parent_account': parent_account,
            'company': company,
            'account_type': "Payable"
        })
        new_account_doc.insert()
        return new_account_doc.name

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            _("Something went wrong while creating credit account for {}"
              .format(frappe.utils.get_link_to_form("Supplier", doc.name)))
        )
        return None
    