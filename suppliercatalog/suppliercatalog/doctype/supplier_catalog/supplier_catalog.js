// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt
frappe.ui.form.on("Supplier Catalog", {
  refresh(frm) {
    // Button nur bei gespeicherten Docs (optional)
    if (!frm.is_new()) {
      frm.add_custom_button(__("Start Import"), () => {
        frm.trigger("start_import");
      });
    }
  },

  start_import(frm) {
    frappe.call({
      method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog.supplier_catalog.import_bnn_items_from_file",
      args: { docname: frm.doc.name },
      freeze: true,
      callback(r) {
        if (r.message) frappe.msgprint(r.message);
      }
    });
  }
});
