import frappe
import csv
import io
from frappe.utils import now_datetime


def _get_raw(row, idx):
    """Gibt CSV-Wert als String zurück oder '' wenn Index fehlt / None."""
    if idx < 0 or idx >= len(row):
        return ""
    v = row[idx]
    if v is None:
        return ""
    return str(v).strip()


def _set_if_value(payload, fieldname, value):
    """Setzt payload[fieldname] nur, wenn value nicht leer ist."""
    if value != "":
        payload[fieldname] = value


def import_bnn_items_from_csv(doc):
    """
    Minimaler Import:
    - Encoding: cp850 (bei dir bestätigt)
    - delimiter ';', quotechar '"'
    - Zeile 0: Infozeile (nicht importieren)
    - letzte Zeile: Abschluss (z.B. ;;99) (nicht importieren)
    - 0-based Mapping
    - Es werden NUR Felder gesetzt, wenn in der CSV ein Wert vorhanden ist.
    - KEINE Skip-/Pflichtfeldlogik, keine Fehlersuche/Logs.
    """

    # Pflichtfelder im Supplier Catalog
    if not doc.import_datei:
        frappe.throw("Bitte lade zuerst eine Import-Datei hoch.")
    if not doc.supplier:
        frappe.throw("Bitte fülle das Feld 'supplier' aus.")
    if not doc.linked_pricelist:
        frappe.throw("Bitte fülle das Feld 'linked_pricelist' aus.")

    # Dateipfad holen
    file_doc = frappe.get_doc("File", {"file_url": doc.import_datei})
    file_path = file_doc.get_full_path()

    # Datei lesen (cp850 für korrekte Umlaute)
    with open(file_path, "rb") as f:
        raw = f.read()
    text = raw.decode("cp850")

    # CSV parsen
    reader = csv.reader(io.StringIO(text), delimiter=";", quotechar='"')
    lines = list(reader)

    if len(lines) < 3:
        frappe.throw("Die Datei enthält zu wenige Zeilen (Kopf + Daten + Abschluss erwartet).")

    # file_age: Zeile 0, Spalte 10 => Index 9 (nur setzen wenn Wert vorhanden)
    file_age_val = _get_raw(lines[0], 9)
    if file_age_val:
        try:
            doc.db_set("file_age", file_age_val)
        except Exception:
            pass

    imported = 0

    # Datenzeilen: Zeile 1 bis vorletzte
    for row in lines[1:-1]:
        payload = {"doctype": "Item BNN"}

        # 0-based Mapping (nur setzen, wenn Wert vorhanden)
        _set_if_value(payload, "lieferant_artikelnummer", _get_raw(row, 0))
        _set_if_value(payload, "aenderungskennung",       _get_raw(row, 1))
        _set_if_value(payload, "ean_laden",               _get_raw(row, 4))
        _set_if_value(payload, "ean_bestell",             _get_raw(row, 5))
        _set_if_value(payload, "bezeichnung_1",           _get_raw(row, 6))
        _set_if_value(payload, "bezeichnung_2",           _get_raw(row, 7))
        _set_if_value(payload, "bezeichnung_3",           _get_raw(row, 8))
        _set_if_value(payload, "handelsklasse",           _get_raw(row, 9))
        _set_if_value(payload, "marke",                   _get_raw(row, 10))
        _set_if_value(payload, "marke_alt",               _get_raw(row, 11))
        _set_if_value(payload, "herkunft",                _get_raw(row, 12))
        _set_if_value(payload, "qualitaet",               _get_raw(row, 13))

        # Werte vom Supplier Catalog übernehmen (falls Fieldnames im Item BNN so heißen)
        payload["lieferant"] = doc.supplier
        payload["preisliste"] = doc.linked_pricelist

        # Insert (wenn Pflichtfelder fehlen, wirft Frappe hier einen Fehler)
        frappe.get_doc(payload).insert(ignore_permissions=True)
        imported += 1

    # In bench console wichtig: commit
    frappe.db.commit()

    # Statusfelder setzen
    doc.db_set("import_status", "Erfolgreich")
    doc.db_set("import_menge", imported)
    doc.db_set("last_imported", now_datetime())

    return f"{imported} Einträge importiert."
