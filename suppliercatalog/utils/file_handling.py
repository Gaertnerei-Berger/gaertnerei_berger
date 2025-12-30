import frappe

def move_file_to_custom_folder(doc, method):
    """Move file attachments to specific folders based on the attached DocType."""

    # Skip if not attached to any DocType
    if not doc.attached_to_doctype or not doc.attached_to_name:
        return

    # Map of Doctypes to target folder paths
    folder_map = {
        "Supplier Catalog Brand": "Home/Attachments/Supplier Catalog Brand",
        "Supplier Catalog Item": "Home/Attachments/Supplier Catalog Item",
        "Supplier Quality": "Home/Attachments/Supplier Quality"
    }

    doctype = doc.attached_to_doctype
    target_folder = folder_map.get(doctype)

    if not target_folder:
        return  # No folder mapping defined

    # Ensure the target folder exists
    parts = target_folder.split("/")
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else part
        if not frappe.db.exists("File", {"file_name": part, "is_folder": 1, "folder": "/".join(current.split('/')[:-1]) or "Home"}):
            frappe.get_doc({
                "doctype": "File",
                "file_name": part,
                "is_folder": 1,
                "folder": "/".join(current.split("/")[:-1]) or "Home"
            }).insert(ignore_permissions=True)

    # Move file
    doc.folder = target_folder
    doc.save(ignore_permissions=True)
