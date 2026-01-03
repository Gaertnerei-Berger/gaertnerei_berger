// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt


frappe.ui.form.on("Supplier Catalog", {
  refresh(frm) {
    // Beim Laden direkt prüfen, welche Sektion angezeigt werden soll
    frm.trigger("import_methode");
  },

  import_methode(frm) {
    const methode = frm.doc.import_methode;

    frm.toggle_display("api_import_section", methode === "API");
    frm.toggle_display("file_import_section", methode === "File");
  },

  start_import(frm) {
    frappe.call({
      method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog.supplier_catalog.import_supplier_catalog_items_from_file",
      args: { docname: frm.doc.name },
      freeze: true,
      callback(r) {
        if (r.message) {
          frappe.msgprint(r.message);
        }
      }
    });
  }
});


frappe.ui.form.on('Supplier Catalog', {
    onload: function(frm) {
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Supplier Catalog Brand",
                filters: {
                    freigabe: 1
                },
                fields: ["brand_name"],
                limit_page_length: 1000
            },
            callback: function(r) {
                if (r.message) {
                    const options = r.message.map(row => row.brand_name).filter(Boolean);
                    frm.set_df_property("brand_datanature", "options", ["", ...options]);
                    frm.refresh_field("brand_datanature");
                }
            }
        });
    }
});

frappe.ui.form.on('Supplier Catalog', {
    start_import_api: function(frm) {
        if (!frm.doc.brand_datanature) {
            frappe.msgprint("Bitte wählen Sie eine Marke für den Import aus.");
            return;
        }

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Supplier Catalog Brand",
                filters: { brand_name: frm.doc.brand_datanature },
                fieldname: "brand_id"
            },
            callback: function(r) {
                if (!r.message || !r.message.brand_id) {
                    frappe.msgprint("Die ausgewählte Marke wurde nicht gefunden.");
                    return;
                }

                // Alerts can be shown immediately
                frappe.show_alert(
                    { message: "Import der Produkte gestartet!", indicator: "blue" },
                    20
                );

                frappe.show_alert(
                    { message: "Bitte warten bis die Meldung 'Erfolgreich importiert' erscheint!", indicator: "blue" },
                    20
                );

                // Save must happen right before the server import call (only if dirty)
                const save_if_needed = frm.is_dirty()
                    ? frm.save()
                    : Promise.resolve();

                save_if_needed.then(() => {
                    // Server import call happens only after save completed (or not needed)
                    frappe.call({
                        method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog.supplier_catalog.run_import_products",
                        args: {
                            brand_id: r.message.brand_id,
                            supplier_catalog: frm.doc.name
                        },
                        callback: function() {
                            frappe.msgprint("Erfolgreich importiert.");
                        }
                    });
                });
            }
        });
    }
});