import frappe
import csv
from decimal import Decimal
from frappe.utils import now_datetime

def import_bnn_items_from_csv(doc):
    if not doc.import_datei:
        frappe.throw("Bitte lade zuerst eine Import-Datei hoch.")
    if not doc.supplier:
        frappe.throw("Feld 'Supplier' ist leer.")
    if not doc.linked_pricelist:
        frappe.throw("Feld 'Linked Pricelist' ist leer.")

    file_doc = frappe.get_doc("File", {"file_url": doc.import_datei})
    file_path = file_doc.get_full_path()

    imported_count = 0

    try:
        with open(file_path, mode='r', encoding='windows-1252', errors='replace') as file:
            reader = csv.reader(file, delimiter=';', quotechar='"')
            lines = list(reader)

            if len(lines) < 3:
                frappe.throw("CSV-Datei hat zu wenige Zeilen (mind. 3 inkl. Kopf und Abschluss).")

            # 📅 Datei-Alter aus Zeile 0, Spalte 10 (Index 9)
            if len(lines[0]) >= 10:
                doc.db_set("file_age", lines[0][9].strip())

            # 🔁 Zeilen 1 bis -2 (Datenzeilen)
            data_lines = lines[1:-1]

            for i, row in enumerate(data_lines, start=2):
                if not row or len(row) < 15:
                    frappe.log_error(f"Zeile {i} zu kurz oder leer: {row}", "BNN CSV Import")
                    continue

                try:
                    frappe.get_doc({
                        "doctype": "BNN Item",
                        "lieferant_artikelnummer": row[1].strip(),
                        "aenderungskennung": row[2].strip(),
                        "ean_laden": row[5].strip(),
                        "ean_bestell": row[6].strip(),
                        "bezeichnung_1": row[7].strip(),
                        "bezeichnung_2": row[8].strip(),
                        "bezeichnung_3": row[9].strip(),
                        "handelsklasse": row[10].strip(),
                        "marke": row[11].strip(),
                        "marke_alt": row[12].strip(),
                        "herkunft": row[13].strip(),
                        "qualitaet": row[14].strip(),
                        # Beispiel: falls z. B. row[15] Preis wäre:
                        # "preis": Decimal(row[15].strip().replace(',', '.'))
                    }).insert(ignore_permissions=True)

                    frappe.db.commit()
                    imported_count += 1

                except Exception as e:
                    frappe.log_error(f"Fehler in Zeile {i}: {str(e)}", "BNN Import Fehler")

        doc.db_set("import_status", "Erfolgreich")
        doc.db_set("import_menge", imported_count)
        doc.db_set("last_imported", now_datetime())

        return f"{imported_count} Einträge importiert."

    except Exception as e:
        doc.db_set("import_status", f"Fehlgeschlagen: {str(e)}")
        doc.db_set("import_menge", 0)
        return f"Import fehlgeschlagen: {str(e)}"
