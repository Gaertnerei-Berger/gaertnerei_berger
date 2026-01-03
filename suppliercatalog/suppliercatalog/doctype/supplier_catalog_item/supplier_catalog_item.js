// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supplier Catalog Item", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Supplier Catalog Item', {
    refresh(frm) {
        frm.add_custom_button(__('Import Item in ERP'), function () {
            frappe.show_alert(
                { message: "Import started…", indicator: "blue" },
                5
            );

            frappe.call({
                method: "suppliercatalog.utils.sup_item_import.import_sci",
                args: {
                    supplier_catalog_item_names: JSON.stringify([frm.doc.name])
                },
                callback: function () {
                    frappe.msgprint("Import finished.");
                    frm.reload_doc();
                }
            });
        });
    }
});