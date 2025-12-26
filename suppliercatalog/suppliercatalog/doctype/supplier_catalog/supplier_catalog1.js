// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier Catalog", {
  refresh(frm) {
    // 🎯 Button nur bei gespeicherten Docs
    if (!frm.is_new()) {
      frm.add_custom_button(__("Start Import"), () => {
        frm.trigger("start_import");
      });
    }

    // 🔁 Initial Anzeige der richtigen Sektion
    frm.trigger("import_methode");
  },

  import_methode(frm) {
    const methode = frm.doc.import_methode;

    frm.toggle_display("api_import_section", methode === "API");
    frm.toggle_display("file_import_section", methode === "File");
  },

  start_import(frm) {
    frappe.call({
      method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog.supplier_catalog.import_data",
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
