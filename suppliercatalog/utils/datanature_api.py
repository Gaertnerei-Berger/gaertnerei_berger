import frappe
import requests
import json
import xmltodict
from datetime import datetime
from suppliercatalog.utils.german_to_english_countries import (
    GERMAN_TO_ENGLISH_COUNTRY
)
from suppliercatalog.utils.datanature_api_mapping import (
    get_country_of_origin,
    get_tradeclass,
    get_supplier_quality,
    get_content_uom,
    get_order_unit,
    get_shop_unit_uom,
    get_base_price_unit,
    get_tax_amount,
    get_pfand_type,
    get_pfand_amount,
    get_pfand_type_vpe1,
    get_pfand_amount_vpe1,
    get_ingredients_legend,
    get_content_uom_short,
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


def import_approved_brands():
    """
    Fetch approved brands from the API and update Supplier Catalog Brand doctype:
    - Set 'freigabe' checkbox if not already set
    - Count how many were updated and how many were already set
    """

    settings = frappe.get_single("Supplier Catalog API Datanature")
    base_url = settings.api_url_pim.rstrip("/")
    token = fetch_security_token()

    url = f"{base_url}/resources/pim/if/v2_3_0/export/approved/brands"
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/xml"
    }

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != 200:
        frappe.throw(f"Failed to fetch approved brands (HTTP {response.status_code})")

    try:
        xml = xmltodict.parse(response.text)
    except Exception as e:
        frappe.throw(f"XML parse error: {e}")

    brands = xml.get("datanature", {}).get("brands", {}).get("brand", [])
    if isinstance(brands, dict):
        brands = [brands]

    updated_count = 0
    skipped_count = 0

    for entry in brands:
        brand_id = entry.get("id")
        if not brand_id:
            continue

        docname = frappe.db.get_value("Supplier Catalog Brand", {"brand_id": brand_id}, "name")
        if not docname:
            continue

        doc = frappe.get_doc("Supplier Catalog Brand", docname)

        if doc.freigabe:
            skipped_count += 1
        else:
            doc.freigabe = 1
            doc.save(ignore_permissions=True)
            updated_count += 1

    frappe.db.commit()

    frappe.msgprint(
        f"{updated_count} Approved brands import completed.<br>"
        f"Already set (skipped): {skipped_count}"
    )


def import_products(brand_id=None, supplier_catalog=None):
    """
    Fetch products for a brand from the Datanature API and
    insert or update Supplier Catalog Item records.

    Identification logic:
    - item_bio_id (from XML)
    - supplier_catalog (current catalog)

    Behaviour:
    - Update existing items if found
    - Create new items if not found
    - Process ALL products in the XML
    """

    # ------------------------------------------------------------------
    # Basic validation
    # ------------------------------------------------------------------
    if not brand_id:
        frappe.throw("Brand ID is required.")

    if not supplier_catalog:
        frappe.throw("Supplier Catalog is required.")

    # ------------------------------------------------------------------
    # API setup
    # ------------------------------------------------------------------
    settings = frappe.get_single("Supplier Catalog API Datanature")
    base_url = settings.api_url_pim.rstrip("/")
    token = fetch_security_token()

    url = f"{base_url}/resources/pim/if/v2_3_0/export/brand/{brand_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/xml"
    }

    response = requests.get(url, headers=headers, timeout=60)
    if response.status_code != 200:
        frappe.throw(f"Failed to fetch products (HTTP {response.status_code})")

    # ------------------------------------------------------------------
    # Parse XML
    # ------------------------------------------------------------------
    try:
        xml_data = xmltodict.parse(response.text)
    except Exception as e:
        frappe.throw(f"XML parse error: {e}")

    products = (
        xml_data
        .get("datanature", {})
        .get("products", {})
        .get("product", [])
    )

    if isinstance(products, dict):
        products = [products]


 
    created = 0
    updated = 0
    skipped = 0

    # ------------------------------------------------------------------
    # Process each product
    # ------------------------------------------------------------------
    for product in products:

        bio_id = product.get("sys_bio_id")
        if not bio_id:
            continue

        # --------------------------------------------------------------
        # Check if item already exists (bio_id + supplier_catalog)
        # --------------------------------------------------------------
        existing_name = frappe.db.get_value(
            "Supplier Catalog Item",
            {
                "item_bio_id": bio_id,
                "supplier_catalog": supplier_catalog
            },
            "name"
        )

        if existing_name:
            doc = frappe.get_doc("Supplier Catalog Item", existing_name)
            is_new = False
            updated += 1
        else:
            doc = frappe.new_doc("Supplier Catalog Item")
            doc.item_bio_id = bio_id
            doc.supplier_catalog = supplier_catalog
            is_new = True
            created += 1

        # --------------------------------------------------------------
        # Check and write last modified timestamp
        # --------------------------------------------------------------
        
        last_modified = product.get("sys_last_modified")
        if last_modified:
            last_modified = last_modified.strip()
            try:
                dt = datetime.strptime(last_modified, "%d.%m.%Y %H:%M:%S")
                if doc.last_imported == dt.date():
                    skipped += 1
                    updated -= 1
                    continue
                doc.last_imported = dt.date()
                doc.last_imported_time = dt.time()
            except ValueError:
                # Fallback: nur Datum setzen, wenn das Format unerwartet ist
                doc.last_imported = last_modified





        # --------------------------------------------------------------
        # Apply field mappings (pure mapping logic, no assumptions)
        # --------------------------------------------------------------
        
        # assign supplier
        supplier_name = frappe.db.get_value("Supplier Catalog", supplier_catalog, "supplier")
        doc.supplier = supplier_name

        # assign supplier item number
        doc.supplier_itemnumber = product.get("idnr_artikelnr_inverkehrbringer")

        # assign brand
        brand_db = frappe.db.get_value(
        "Supplier Catalog Brand",
        {"brand_id": product.get("pbm_marke_id")},
        "name"
        )

        if brand_db:
            doc.brand = brand_db

        # names
        name1 = product.get("pbm_produktname_kurz")
        doc.name2 = product.get("pbm_produktname_mittel")

        # weight item checkbox
        doc.weight_item = 1 if product.get("ihf_wiegeartikel_eh") == "J" else 0

        # EAN
        doc.ean_shop = product.get("idnr_gtin")
        doc.ean_order = product.get("log_vpe1_gtin")

        
        # country of origin
        co_raw = product.get("urhk_ursprungsland_intrastat_id")
        co_code = int(co_raw.get("#text")) if isinstance(co_raw, dict) and co_raw.get("#text") else None
        if co_code:
            country = get_country_of_origin(co_code)
            if country:
                doc.country_of_origin = country

        # tradeclass
        tc = product.get("wgsa_klassenangabe_id")
        if tc:
            doc.tradeclass = get_tradeclass(int(tc))

        # supplier quality
        sq = product.get("bio_bnn_ik_id")
        if sq:
            supplier_quality_kurz = get_supplier_quality(int(sq))
            if supplier_quality_kurz:
                # lookup the actual Supplier Quality record
                quality_doc = frappe.db.get_value(
                    "Supplier Quality",
                    {"abbreviation_data": supplier_quality_kurz},
                    "name"
                )
                if quality_doc:
                    doc.supplierquality = quality_doc
                else:
                    doc.supplierquality = None

        # control agency
        doc.controlagency = product.get("bio_kontrollstelle")

        # dietary checkboxes
        doc.ernhinweis_vegan = 1 if product.get("ernhinweis_vegan") == "true" else 0
        doc.ernhinweis_vegetarisch = 1 if product.get("ernhinweis_vegetarisch") == "true" else 0
        doc.ernhinweis_glutenfrei = 1 if product.get("ernhinweis_glutenfrei") == "true" else 0
        doc.ernhinweis_laktosefrei = 1 if product.get("ernhinweis_laktosefrei") == "true" else 0

        # descriptions and ingredients
        doc.description = product.get("markinf_produktbeschreibung_lang")
               
        if product.get("zut_zutatenverzeichnis"):
            ingredients_list = product.get("zut_zutatenverzeichnis")
            legend_id = product.get("zut_zutatenlegende_id")
            if legend_id:
                ingredients_legend = get_ingredients_legend(int(legend_id))
                doc.list_of_ingredients = f"{ingredients_list} {ingredients_legend}"
            else:
                doc.list_of_ingredients = ingredients_list


        # weights and dimensions
        doc.weight_shop_unit = product.get("log_gewicht_vke_brutto")
        doc.weight_order_unit = product.get("log_gewicht_vpe1_brutto")
        doc.width = product.get("log_dim_vke_breite")
        doc.height = product.get("log_dim_vke_hoehe")
        doc.depth = product.get("log_dim_vke_tiefe")

        # order unit quantity
        doc.orderunit_quantity = product.get("log_vpe1_menge")

        # orderunit mapping
        if product.get("log_vpe1_art_id"):
            doc.orderunit = get_order_unit(int(product.get("log_vpe1_art_id")))

        # shop_unit_uom
        if product.get("ihf_verpackungsart_artikel_id"):
            doc.shop_unit_uom = get_shop_unit_uom(
                int(product.get("ihf_verpackungsart_artikel_id"))
            )

        # content weight + content uom
        doc.content_weight = product.get("ihf_nettofuellmenge_oder_mengenangabe")
        if product.get("ihf_nettofuellmenge_oder_mengenangabe_einheit_id"):
            doc.content_uom = get_content_uom(
                int(product.get("ihf_nettofuellmenge_oder_mengenangabe_einheit_id"))
            )

        # recommended price
        doc.recommended_sales_price = product.get("preis_empfohlener_verkaufspreis_deutschland")

        # base price unit
        if product.get("preis_grundpreiseinheit_endverbraucher_id"):
            doc.base_price_unit = get_base_price_unit(
                int(product.get("preis_grundpreiseinheit_endverbraucher_id"))
            )

        # tax_amount
        if product.get("preis_mwst_id"):
            doc.tax_amount = get_tax_amount(int(product.get("preis_mwst_id")))

        # pfand type
        if product.get("pack_pfandpflicht_artikel_de_id"):
            doc.pfand_typ = get_pfand_type(
                int(product.get("pack_pfandpflicht_artikel_de_id"))
            )

        # pfand amount (ID first, fallback to numeric value)

        pfand_id = product.get("pack_pfandwert_artikel_de_id")
        pfand_value = product.get("pack_pfandwert_artikel_de_zahl")

        if pfand_id:
            # primary mapping via autoserial ID
            doc.pfand_ammount = get_pfand_amount(int(pfand_id))

        elif pfand_value:
            # fallback mapping via numeric value
            doc.pfand_ammount = (float(pfand_value))



        # pfand type vpe1
        if product.get("pack_pfandpflicht_vpe1_de_id"):
            doc.pfand_typ_vpe1 = get_pfand_type_vpe1(
                int(product.get("pack_pfandpflicht_vpe1_de_id"))
            )

        # pfand amount vpe1 (ID first, fallback to numeric value)

        pfand_id_vpe1 = product.get("pack_pfandwert_vpe1_de_id")
        pfand_value_vpe1 = product.get("pack_pfandwert_vpe1_de_zahl")

        if pfand_id_vpe1:
            # primary mapping via autoserial ID
            doc.pfand_ammount_vpe1 = get_pfand_amount_vpe1(int(pfand_id_vpe1))

        elif pfand_value_vpe1:
            # fallback mapping via numeric value
            doc.pfand_ammount_vpe1 = (float(pfand_value_vpe1))




        if product.get("pack_pfandwert_vpe1_de_id"):
            doc.pfand_ammount_vpe1 = get_pfand_amount_vpe1(
                int(product.get("pack_pfandwert_vpe1_de_id"))
            )


      
        # calculate base_price_faktor
        content_uom = get_content_uom(int(product.get("ihf_nettofuellmenge_oder_mengenangabe_einheit_id", 0)))
        content_weight = float(product.get("ihf_nettofuellmenge_oder_mengenangabe"))

        if content_weight and content_uom:
            try:
                weight_value = content_weight
                if content_uom in ["Kilogramm", "Liter"]:
                    faktor_einheit = 1
                elif content_uom in ["Gramm", "Milliliter"]:
                    faktor_einheit = 1000
                else:
                    faktor_einheit = None

                if faktor_einheit:
                    doc.base_price_faktor = round(faktor_einheit / weight_value, 3)
            except:
                pass  # silently skip on bad input


        # Shop unit
        if content_weight and content_uom:
            shop_unit = f"{content_weight} {content_uom}"
            doc.shop_unit = shop_unit

        # Add the Shop unit to name1
        if name1 and content_weight:
            if content_weight.is_integer():
                content_weight_special = int(content_weight)
            else:
                content_weight_special= content_weight
            content_uom_short = get_content_uom_short(int(product.get("ihf_nettofuellmenge_oder_mengenangabe_einheit_id")))
            name_addition = f"{content_weight_special}{content_uom_short}"
            doc.name1 = f"{name1} {name_addition}"


        # --------------------------------------------------------------
        # Save document
        # --------------------------------------------------------------
        doc.save(ignore_permissions=True)

        if is_new:
            created += 1
        else:
            updated += 1

    frappe.db.commit()

    # ------------------------------------------------------------------
    # Final message
    # ------------------------------------------------------------------
    frappe.msgprint(
        f"Product import finished.<br>"
        f"Created: {created}<br>"
        f"Updated: {updated}<br>"
        f"Skipped: {skipped}"
    )
