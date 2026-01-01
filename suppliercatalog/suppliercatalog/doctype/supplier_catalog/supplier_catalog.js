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
