import frappe
import requests
import json
import xmltodict
from frappe.utils.file_manager import save_file
from suppliercatalog.utils.german_to_english_countries import (
    GERMAN_TO_ENGLISH_COUNTRY
)

def fetch_security_token():
    settings = frappe.get_single("Supplier Catalog API Datanature")

    username = settings.username.strip()
    password = settings.get_password("password").strip()
    api_url = settings.api_url.rstrip("/")

    token_url = f"{api_url}/resources/security/accesstoken/"

    payload = {
        "userid": username,
        "password": password
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(token_url, data=json.dumps(payload), headers=headers)
    data = response.json()

    if data.get("status") == "SUCCESS" and data.get("token"):
        return data["token"]
    else:
        frappe.throw(
            "<b>Login fehlgeschlagen</b><br>❌ Benutzername oder Passwort ist falsch.<br>"
            "Bitte überprüfe deine Zugangsdaten in den Supplier Catalog API Datanature."
        )


def import_brand_abbreviations_from_api():
    """
    Fetch brand abbreviations from the Datanature API and
    insert/update records in the Supplier Catalog Brand doctype:

    - Updates existing if brand_id matches
    - Creates new if not found
    - Translates German country names to ERPNext English
    """

    settings = frappe.get_single("Supplier Catalog API Datanature")
    base_url = settings.api_url_pim.rstrip("/")
    token = fetch_security_token()

    # Export URL for brand abbreviations
    url = f"{base_url}/resources/pim/if/v2_3_0/export/brand/abbreviations"

    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/xml"
    }

    response = requests.get(url, headers=headers, timeout=60)
    if response.status_code != 200:
        frappe.throw(f"Failed to fetch brand abbreviations (HTTP {response.status_code})")

    try:
        xml_data = xmltodict.parse(response.text)
    except Exception as e:
        frappe.throw(f"XML parse error: {e}")

    # Extract list of brand entries
    brands = (
        xml_data
        .get("datanature", {})
        .get("brand-abbreviations", {})
        .get("brand-abbreviation", [])
    )

    if isinstance(brands, dict):
        brands = [brands]

    created = 0
    updated = 0
    skipped = 0

    for entry in brands:

        # brand id
        brand_id = entry.get("brand_id")
        if not brand_id:
            skipped += 1
            continue

        # Match existing via brand_id
        existing_name = frappe.db.get_value(
            "Supplier Catalog Brand",
            {"brand_id": brand_id},
            "name"
        )

        # Translate country (German → English) using helper map
        country_local = (entry.get("country") or "").strip()
        country_english = GERMAN_TO_ENGLISH_COUNTRY.get(country_local, country_local)

        if country_english and not frappe.db.exists("Country", country_english):
            country_english = None

        # Prepare mapped fields
        fields_to_map = {
            "abbreviation": entry.get("kuerzel"),
            "assigned_at": entry.get("assigned_at"),
            "brand_name": entry.get("brand_name"),
            "producer_name": entry.get("producer_name"),
            "producer_id": entry.get("producer_id"),
            "street": entry.get("street"),
            "city": entry.get("city"),
            "zip_code": entry.get("zip_code"),
            "country": country_english,
        }

        if existing_name:
            # Update existing
            doc = frappe.get_doc("Supplier Catalog Brand", existing_name)

            has_changed = False
            for key, value in fields_to_map.items():
                if value and doc.get(key) != value:
                    doc.set(key, value)
                    has_changed = True

            if has_changed:
                doc.save(ignore_permissions=True)
                updated += 1

        else:
            # Create new
            doc = frappe.new_doc("Supplier Catalog Brand")
            doc.brand_id = brand_id

            for key, value in fields_to_map.items():
                if value:
                    doc.set(key, value)

            doc.insert(ignore_permissions=True)
            created += 1

    frappe.db.commit()

    frappe.msgprint(
        f"Brand import finished.<br>"
        f"Created: {created}<br>"
        f"Updated: {updated}<br>"
        f"Skipped (no brand_id): {skipped}"
    )


def fetch_and_save_logo_for_brand(brand_id, picture_id, filename, docname):
    """
    Download the brand logo from the API and save it in ERPNext.
    Returns:
        file_url (str) if saved
        None if download failed
    """

    # Validate
    if not brand_id or not picture_id:
        return None

    # Get settings + token
    settings = frappe.get_single("Supplier Catalog API Datanature")
    base_url = settings.api_url_pim.rstrip("/")
    token = fetch_security_token()

    # Build URL
    logo_url = (
        f"{base_url}/resources/pim/if/v2_3_0/export/brand/"
        f"{brand_id}/binary/logo/{picture_id}"
    )

    # Curl‑like headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Expect": ""
    }

    try:
        response = requests.get(logo_url, headers=headers, timeout=30)
    except Exception as e:
        print(f"[fetch_and_save_logo_for_brand] Request failed: {e}")
        return None

    print("--------------------------------------------------")
    print(f"[fetch_and_save_logo_for_brand] Brand: {brand_id}")
    print(f"[fetch_and_save_logo_for_brand] Status: {response.status_code}")
    print(f"[fetch_and_save_logo_for_brand] Content Length: {len(response.content) if response.content else 0}")
    print("--------------------------------------------------")

    if response.status_code != 200 or not response.content:
        return None

    # Save file in ERPNext with the correct filename (includes extension!)
    file_doc = save_file(
        filename,
        response.content,
        "Supplier Catalog Brand",
        docname,
        decode=False,
        is_private=0
    )

    return file_doc.file_url



def import_approved_brands():
    """
    Fetch approved brands from the API and update Supplier Catalog Brand doctype:
    - Set 'freigabe' checkbox
    - Fetch and store logo only if changed
    """

    settings = frappe.get_single("Supplier Catalog API Datanature")
    base_url = settings.api_url_pim.rstrip("/")
    token = fetch_security_token()

    approved_url = f"{base_url}/resources/pim/if/v2_3_0/export/approved/brands"
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/xml"
    }

    response = requests.get(approved_url, headers=headers, timeout=30)
    if response.status_code != 200:
        frappe.throw(f"Failed to fetch approved brands (HTTP {response.status_code})")

    try:
        xml_data = xmltodict.parse(response.text)
    except Exception as e:
        frappe.throw(f"XML parse error: {e}")

    brands = xml_data.get("datanature", {}).get("brands", {}).get("brand", [])
    if isinstance(brands, dict):
        brands = [brands]

    updated = 0
    logos_updated = 0
    skipped = 0

    for entry in brands:

        brand_id = entry.get("id")
        if not brand_id:
            skipped += 1
            continue

        existing_name = frappe.db.get_value(
            "Supplier Catalog Brand",
            {"brand_id": brand_id},
            "name"
        )
        if not existing_name:
            skipped += 1
            continue

        doc = frappe.get_doc("Supplier Catalog Brand", existing_name)

        # Set checkbox
        if not doc.freigabe:
            doc.freigabe = 1

        # XML logo info
        logo_node = entry.get("logo") or {}
        picture_id = logo_node.get("id")
        xml_last_mod = logo_node.get("last_modified")
        filename = logo_node.get("name")

        # Only update logo if picture exists and last_modified changed
        if picture_id and filename:
            if not doc.logo_last_modified or (xml_last_mod and doc.logo_last_modified != xml_last_mod):

                file_url = fetch_and_save_logo_for_brand(brand_id, picture_id, filename, existing_name)

                if file_url:
                    doc.logo_color = file_url
                    doc.logo_last_modified = xml_last_mod
                    logos_updated += 1

        doc.save(ignore_permissions=True)
        updated += 1

    frappe.db.commit()

    frappe.msgprint(
        f"Approved brands import finished.<br>"
        f"Brands updated: {updated}<br>"
        f"Logos saved/updated: {logos_updated}<br>"
        f"Skipped: {skipped}"
    )


