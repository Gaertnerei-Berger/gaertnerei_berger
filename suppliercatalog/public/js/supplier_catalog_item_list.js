
function add_import_button(page_obj) {
    page_obj.page.add_action_item("Import Items in ERP", () => {
        frappe.call({
            method: "your_app.your_module.doctype.import_script.import_items",
            callback: () => frappe.msgprint("Import started!")
        });
    });
}


frappe.listview_settings['Supplier Catalog Item'] = {
  onload(listview) {
        listview.page.add_action_item("Import Items in ERP", () => {
            frappe.call({
                method: "your_app.your_module.doctype.supplier_catalog_item.supplier_catalog_item.import_items",
                callback: function () {
                    frappe.msgprint("Import started...");
                }
            });
        });
    }
};




frappe.pages['supplier-catalog-report'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Supplier Catalog Report',
        single_column: true
    });

    add_import_button({ page });
};
