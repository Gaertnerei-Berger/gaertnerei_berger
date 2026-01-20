// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt

// Listen for background job errors

frappe.ui.form.on("Supplier Catalog", {
  refresh(frm) {
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
    start_import_api(frm) {

        if (!frm.doc.brand_datanature) {
            frappe.msgprint("Please select a brand for the import.");
            return;
        }

        let progress = 0;

        frappe.show_progress(
            "Product Import",
            progress,
            100,
            "Import started. This may take a moment."
        );

        const progress_interval = setInterval(() => {
            if (progress < 90) {
                progress += 5;
                frappe.show_progress(
                    "Product Import",
                    progress,
                    100,
                    "Import running..."
                );
            }
        }, 500);

        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Supplier Catalog Brand",
                filters: { brand_name: frm.doc.brand_datanature },
                fieldname: "brand_id"
            },
            callback(r) {
                if (!r.message || !r.message.brand_id) {
                    clearInterval(progress_interval);
                    frappe.hide_progress();
                    frappe.msgprint("Brand ID could not be resolved.");
                    return;
                }

                frappe.call({
                    method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog.supplier_catalog.run_import_products",
                    args: {
                        brand_id: r.message.brand_id,
                        supplier_catalog: frm.doc.name
                    },
                    callback() {
                        clearInterval(progress_interval);

                        frappe.show_progress(
                            "Product Import",
                            100,
                            100,
                            "Import started."
                        );

                        setTimeout(() => {
                            frappe.hide_progress();
                        }, 800);

                        frappe.msgprint("Import started. This may take a moment.");
                    },
                    error(err) {
                        clearInterval(progress_interval);
                        frappe.hide_progress();

                        frappe.msgprint({
                            title: "Import failed",
                            message: err.message || "Unknown error",
                            indicator: "red"
                        });
                    }
                });
            },
            error(err) {
                clearInterval(progress_interval);
                frappe.hide_progress();

                frappe.msgprint({
                    title: "Brand lookup failed",
                    message: err.message || "Unknown error",
                    indicator: "red"
                });
            }
        });
    }
});



frappe.ui.form.on("Supplier Catalog", {
  delete_items(frm) {
    frappe.confirm(
      __("Are you sure you want to delete ALL items of this supplier catalog? This cannot be undone."),
      function () {
        frappe.call({
          method: "suppliercatalog.suppliercatalog.doctype.supplier_catalog.supplier_catalog.enqueue_delete_all_catalog_items",
          args: {
            docname: frm.doc.name
          },
          callback: function (r) {
            frappe.msgprint(
              r.message || __("Deletion started in background.")
            );
            frm.reload_doc();
          }
        });
      }
    );
  }
});