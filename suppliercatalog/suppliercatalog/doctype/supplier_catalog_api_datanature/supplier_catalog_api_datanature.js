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
                    frappe.show_alert("Security-Token erfolgreich gespeichert ✅",7);
                    frm.reload_doc();
                }
            }
        });
    }
});

frappe.ui.form.on('Supplier Catalog API Datanature', {
    load_brands: function(frm) {
	frappe.show_alert("Import der Datanature Brands gestartet!",20);
	frappe.show_alert("Bitte warten sie bis die Meldung Erfolgreich importiert erscheint!",20);
        frappe.call({
            method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog_api_datanature.supplier_catalog_api_datanature.load_brands",
            callback: function(r) {
                    frappe.msgprint(r.message);
                    frm.reload_doc();
            }
        });
    }
});

frappe.ui.form.on('Supplier Catalog API Datanature', {
    load_authorised_brands: function(frm) {
        frappe.show_alert("Import der freigegebenen Brands gestartet!",20);
        frappe.show_alert("Bitte warten sie bis die Meldung Erfolgreich importiert erscheint!",20);
        frappe.call({
            method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog_api_datanature.supplier_catalog_api_datanature.load_authorised_brands",
            callback: function(r) {
                    frappe.msgprint(r.message);
                    frm.reload_doc();
            }
        });
    }
});

