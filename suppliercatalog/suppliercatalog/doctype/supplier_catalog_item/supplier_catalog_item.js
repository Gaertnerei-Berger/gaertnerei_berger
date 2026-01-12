// Copyright (c) 2025, Gärtnerei Berger and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Supplier Catalog Item", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Supplier Catalog Item', {
    refresh(frm) {

        if (frm.__import_button_added) return;

        frm.add_custom_button(__('Import Item in ERP'), function () {

            frappe.db.get_single_value(
                "Supplier Catalog Settings",
                "itemgroup_ask"
            ).then(itemgroup_ask => {

                if (itemgroup_ask) {
                    frappe.prompt(
                        [
                            {
                                fieldname: "item_group",
                                fieldtype: "Link",
                                label: "Artikelgruppe",
                                options: "Item Group",
                                reqd: 1
                            }
                        ],
                        values => {
                            start_import(frm, values.item_group);
                        },
                        __("Artikelgruppe auswählen"),
                        __("Import starten")
                    );
                } else {
                    frappe.db.get_single_value(
                        "Supplier Catalog Settings",
                        "itemgroup_select"
                    ).then(item_group => {
                        start_import(frm, item_group);
                    });
                }
            });
        });

        frm.__import_button_added = true;
    }
});

function start_import(frm, item_group) {
    frappe.show_alert(
        { message: __("Import started…"), indicator: "blue" },
        5
    );

    frappe.call({
        method: "suppliercatalog.utils.sup_item_import.import_sci",
        args: {
            supplier_catalog_item_names: JSON.stringify([frm.doc.name]),
            item_group: item_group
        },
        callback: function () {
            frappe.msgprint(__("Import finished."));
            frm.reload_doc();
        }
    });
}