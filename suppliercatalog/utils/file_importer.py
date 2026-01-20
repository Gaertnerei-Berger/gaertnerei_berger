import frappe
import csv
import io
import re
from frappe.utils import now_datetime

UNIT_MAPPING = {
    "1 kg": "kg",
    "1 l": "Liter",
}

def normalize_unit(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip()

    return UNIT_MAPPING.get(value, value)



def _get_raw(row, idx):
    """
    Return a stripped string value from a CSV row by index.
    If index is out of bounds or value is None => empty string.
    """
    if idx < 0 or idx >= len(row):
        return ""
    value = row[idx]
    return str(value).strip() if value is not None else ""


def _clean_number_db(value):
    """
    Clean numeric values for database insertion.

    - Replace comma with dot for decimal
    - Remove leading zeros
    - '01,5' -> '1.5'
    - '00,05' -> '0.05'
    - '' / '0' / '000' / '0,00' -> ''
    """
    if not value:
        return ""

    # Replace comma with dot for ERPNext float/currency
    value = value.strip().replace(",", ".")

    try:
        number = float(value)
        # Treat zero as empty
        return "" if number == 0 else number
    except ValueError:
        return ""


def _set_if_value(payload, fieldname, value, clean_number_db=False):
    """
    Set payload[fieldname] if value is not empty.
    Optionally apply float cleanup for DB (price/number fields).
    """
    if clean_number_db:
        value = _clean_number_db(value)
    if value != "":
        payload[fieldname] = value


def _set_checkbox(payload, fieldname, value):
    """
    Convert J/N values to ERPNext checkbox (1/0).
    J => 1
    N => 0
    Otherwise skip
    """
    v = value.upper()
    if v == "J":
        payload[fieldname] = 1
    elif v == "N":
        payload[fieldname] = 0


def import_supplier_catalog_items_from_csv(doc):
    """
    Synchronous import with a single GUI progress bar.
    Will trigger a Request Timed Out popup if it runs too long (accepted).
    """

    try:
        frappe.publish_progress(
            0,
            title="Supplier Catalog Import",
            description="Starting import…"
        )

        # -------------------------------------------------
        # Load CSV
        # -------------------------------------------------
        file_doc = frappe.get_doc("File", {"file_url": doc.import_file})
        file_path = file_doc.get_full_path()

        with open(file_path, "rb") as f:
            raw = f.read()

        text = raw.decode("cp850")
        reader = csv.reader(io.StringIO(text), delimiter=";", quotechar='"')
        lines = list(reader)

        if len(lines) < 2:
            raise Exception("File must contain at least one data row.")

        # -------------------------------------------------
        # BNN header check
        # -------------------------------------------------
        header_value = lines[0][0].replace("\ufeff", "").strip().upper()
        if not header_value.startswith("BNN"):
            raise Exception(f"No BNN file detected: {header_value}")

        # -------------------------------------------------
        # Preload mappings
        # -------------------------------------------------
        country_map = {
            c.code.lower(): c.name
            for c in frappe.get_all("Country", fields=["name", "code"])
            if c.code
        }

        brand_map = {
            b.abbreviation.upper(): b.name
            for b in frappe.get_all("Supplier Catalog Brand", fields=["name", "abbreviation"])
            if b.abbreviation
        }

        quality_map = {
            q.abbreviation_data.upper(): q.name
            for q in frappe.get_all("Supplier Quality", fields=["name", "abbreviation_data"])
            if q.abbreviation_data
        }

        tradeclass_names = {
            t.name for t in frappe.get_all("Trade Class", fields=["name"])
        }

        total_rows = len(lines) - 2
        imported = 0
        now_dt = now_datetime()

        # -------------------------------------------------
        # Import rows
        # -------------------------------------------------
        for index, row in enumerate(lines[1:-1], start=1):

            def get(idx):
                return row[idx].strip() if idx < len(row) and row[idx] else ""

            payload = {
                "doctype": "Supplier Catalog Item",
                "supplier_catalog": doc.name,
                "supplier": doc.supplier,
                "supplier_itemnumber": get(0),
                "name1": get(6),
                "name2": get(7),
                "ean_shop": get(4),
                "ean_order": get(5),
                "last_imported": now_dt.date(),
                "last_imported_time": now_dt.time(),
            }

            tradeclass = get(9)
            if tradeclass in tradeclass_names:
                payload["tradeclass"] = tradeclass

            brand_code = get(10).upper()
            if brand_code in brand_map:
                payload["brand"] = brand_map[brand_code]

            iso2 = get(12).lower()
            if iso2 in country_map:
                payload["country_of_origin"] = country_map[iso2]

            quality_code = get(13).upper()
            if quality_code in quality_map:
                payload["supplierquality"] = quality_map[quality_code]

            tax_code = get(33)
            if tax_code == "1":
                payload["tax_amount"] = 7
            elif tax_code == "2":
                payload["tax_amount"] = 19
            elif tax_code == "3":
                payload["tax_amount"] = 9

            if payload.get("supplier_itemnumber") and payload.get("name1"):
                try:
                    doc_item = frappe.get_doc(payload)
                    doc_item.flags.ignore_mandatory = True
                    doc_item.insert(ignore_permissions=True)
                    imported += 1
                except Exception:
                    frappe.log_error(
                        title="Supplier Catalog Import Row Error",
                        message=frappe.get_traceback()
                    )

            progress = int((index / total_rows) * 100)
            frappe.publish_progress(
                progress,
                title="Supplier Catalog Import",
                description=f"Imported {index} of {total_rows}"
            )

        # -------------------------------------------------
        # Finish
        # -------------------------------------------------
        frappe.db.commit()

        doc.db_set("import_status", "Success")
        doc.db_set("import_amount", imported)
        doc.db_set("last_imported", now_datetime())

        frappe.publish_progress(
            100,
            title="Supplier Catalog Import",
            description=f"Finished. Imported {imported} items."
        )

    except Exception as e:
        frappe.log_error(
            title="Supplier Catalog Import Failed",
            message=frappe.get_traceback()
        )

        doc.db_set("import_status", "Failed")
        doc.db_set("import_error", str(e))

        frappe.publish_progress(
            100,
            title="Supplier Catalog Import",
            description=f"Import failed: {str(e)}"
        )

        raise