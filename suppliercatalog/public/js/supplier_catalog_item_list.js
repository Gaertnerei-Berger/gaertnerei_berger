frappe.listview_settings['Supplier Catalog Item'] = {
    onload(listview) {
        listview.page.add_action_item(
            __('Import Items in ERP'),
            function () {
                const selected = listview.get_checked_items();

                if (!selected.length) {
                    frappe.msgprint("Please select at least one item.");
                    return;
                }

                const names = selected.map(row => row.name);

                frappe.show_alert(
                    { message: "Import started…", indicator: "blue" },
                    5
                );

                frappe.call({
                    method: "suppliercatalog.utils.sup_item_import.import_sci",
                    args: {
                        supplier_catalog_item_names: JSON.stringify(names)
                    },
                    callback: function () {
                        frappe.msgprint("Import finished.");
                        listview.clear_checked_items();
                        listview.refresh();
                        }
                });
            }
        );
    }
};