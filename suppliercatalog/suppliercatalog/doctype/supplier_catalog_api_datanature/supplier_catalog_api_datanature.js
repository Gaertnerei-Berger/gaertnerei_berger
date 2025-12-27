// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supplier Catalog API Datanature", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Supplier Catalog API Datanature', {
    test_login: function(frm) {
        frappe.call({
            method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog_api_datanature.supplier_catalog_api_datanature.test_login",
            callback: function(r) {
                if (!r.exc) {
                    frappe.msgprint("Security-Token erfolgreich gespeichert ✅");
                    frm.reload_doc();
                }
            }
        });
    }
});
