import frappe
import re
from frappe import _


# Gets the Company to set the Creditor or Debitor right
def manage_accounts(doc, method):
    company = getattr(doc, 'company', None)
    if not company:
        company = frappe.defaults.get_user_default("Company") or frappe.db.get_value("Company", {}, "name")
    
    if method == "after_insert":
        create_and_link_account(doc, company)
    elif method == "after_delete":
        delete_created_account(doc, company)
    


# To get the right most int from the Namingseries for creating the account nummber
def get_int_from_namingseries(value):
    match = re.search(r'(\d+)$', str(value))
    return int(match.group(1)) if match else None

# Links the created Acc to the right Supplier or Customer
def create_and_link_account(doc, company):
    if doc.doctype == "Supplier":
        create_credit_account = frappe.db.get_single_value("German Accounting Settings", "auto_creditor")

        if create_credit_account:
            credit_account = create_credit_account_for_supplier(doc, company)

            if not credit_account:
                return

            # Calculates the creditor number
            debtor_creditor_number = get_int_from_namingseries(doc.name) + 70000

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

    elif doc.doctype == "Customer":
        create_debit_account = frappe.db.get_single_value("German Accounting Settings", "auto_debitor")

        if create_debit_account:
            debit_account = create_debit_account_for_customer(doc, company)

            if not debit_account:
                return

            # Calculates the creditor number
            debtor_creditor_number = get_int_from_namingseries(doc.name) + 10000

            account_doc = frappe.new_doc("Party Account")
            account_doc.update({
                "parent": doc.name,
                "company": company,
                "account": debit_account,
                "debtor_creditor_number":debtor_creditor_number,
                "parenttype": "Customer",
                "parentfield": "accounts"
            })
            account_doc.insert(ignore_permissions=True)

# Creates Supplier account/checks existence
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
        frappe.log_error(
            _("Failed to create Credit Account for supplier no Namingseries with Integers set for Supplier")
        )
        frappe.throw(
            _("Failed to create Credit Account please deaktivate Function in {} and Contact your Advisor!!!.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        return None

    #Checks if Int is to big for Accounts Limit 29999
    if supplier_number > 29999:
        frappe.log_error(
            _("Contact your Tax Consultant and System Advisor Account Supplier Limit reached")
        )
        frappe.throw(
            _("Failed to create Credit Account please deaktivate Function in {} and Contact your Advisor!!!.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
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

# Creates Customer account/checks existence
def create_debit_account_for_customer(doc, company):
    #Checks if Parent Account is set else Error
    parent_account = frappe.db.get_single_value("German Accounting Settings", "debitor_parent_acc")

    if not parent_account:
        frappe.log_error(
            _("Failed to create Debit Account for Customer {} as no Debitor Parent Account is setup in the {}"
              .format(
                  frappe.utils.get_link_to_form("Customer", doc.name),
                  frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings")
              )),
            _("failed to create Customer debit account")
        )
        frappe.throw(
            _("Failed to create Debit Account for this customer, please set up Debitor Parent Account in {}.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        return None

    # Gets  Namingsereis as int
    customer_number =  get_int_from_namingseries(doc.name)

    #Checks if Int in Namingsereis else Error
    if customer_number is None:
        frappe.throw(
            _("Failed to create Debit Account please deaktivate Function in {} and Contact your Advisor!!!.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        frappe.log_error(
            _("Failed to create Debit Account for Cutomer no Namingseries with Integers set for Customer")
        )
        return None

    #Checks if Int is to big for Accounts Limit 29999
    if customer_number > 59999:
        frappe.throw(
            _("Failed to create Debit Account please deaktivate Function in {} and Contact your Advisor!!!.")
            .format(frappe.utils.get_link_to_form("German Accounting Settings", "German Accounting Settings"))
        )
        frappe.log_error(
            _("Contact your Tax Consultant and System Advisor Account Customer Limit reached")
        )
        return None
    
    # Calculates the Account Number und gets the Account Name
    account_account_number = customer_number + 10000
    account_account_name = doc.customer_name

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
            'account_type': "Receivable"
        })
        new_account_doc.insert()
        return new_account_doc.name

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            _("Something went wrong while creating debit account for {}"
              .format(frappe.utils.get_link_to_form("Customer", doc.name)))
        )
        return None
    
# Deletes the matching Accounts if possible
def delete_created_account (doc, company):
    if doc.doctype == "Supplier":
        delete_credit_account = frappe.db.get_single_value("German Accounting Settings", "auto_creditor")

        if not delete_credit_account:
            return None
            
        get_account = None
        for row in getattr(doc, "accounts", []):
                if row.company == company:
                    get_account = row.account
                    break
            
        
        if not get_account:
            return None
        
        try:
            frappe.delete_doc("Account",get_account,ignore_permissions=True)
        except Exception:
            frappe.log_error(
                _("Failed to delete Credit Account for Supplier check Bookings against it, if possible delete by Hand. If not jump Naming Series by +1")
                .format(get_account)
            )
            frappe.throw(
            _("<b>Serious error</b><br>"
              "Failed to delete Credit Account there are Links against it Booking errors can occur <u> Contact your Advisor!</u>.")
            )
            return None

    elif doc.doctype == "Customer":
        delete_debit_account = frappe.db.get_single_value("German Accounting Settings", "auto_debitor")

        if not delete_debit_account:
            return None
            
        get_account = None
        for row in getattr(doc, "accounts", []):
                if row.company == company:
                    get_account = row.account
                    break
            
        
        if not get_account:
            return None
        
        try:
            frappe.delete_doc("Account",get_account,ignore_permissions=True)
        except Exception:
            frappe.log_error(
                _("Failed to delete Credit Account for Supplier check Bookings against it, if possible delete by Hand. If not jump Naming Series by +1")
                .format(get_account)
            )
            frappe.throw(
            _("<b>Serious error</b><br>"
              "Failed to delete Credit Account there are Links against it Booking errors can occur <u> Contact your Advisor!</u>.")
            )
            return None  

