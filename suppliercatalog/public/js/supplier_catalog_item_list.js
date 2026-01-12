frappe.listview_settings['Supplier Catalog Item'] = {
    onload(listview) {

        // --------------------------------------------------
        //  ACTION: Import selected items
        // --------------------------------------------------
        listview.page.add_action_item(
            __('Import Items in ERP'),
            function () {

                const selected = listview.get_checked_items();

                if (!selected.length) {
                    frappe.msgprint(__("Please select at least one item."));
                    return;
                }

                const names = selected.map(row => row.name);

                frappe.db.get_single_value(
                    "Supplier Catalog Settings",
                    "itemgroup_ask"
                ).then(itemgroup_ask => {

                    if (itemgroup_ask) {
                        frappe.prompt(
                            [{
                                fieldname: "item_group",
                                fieldtype: "Link",
                                label: __("Artikelgruppe"),
                                options: "Item Group",
                                reqd: 1
                            }],
                            values => {
                                start_import(listview, names, values.item_group);
                            },
                            __("Artikelgruppe auswählen"),
                            __("Import starten")
                        );
                    } else {
                        frappe.db.get_single_value(
                            "Supplier Catalog Settings",
                            "itemgroup_select"
                        ).then(item_group => {
                            start_import(listview, names, item_group);
                        });
                    }
                });
            }
        );

        // --------------------------------------------------
        //  ACTION: Bulk Import
        // --------------------------------------------------
        listview.page.add_inner_button(
            __('Bulk Import'),
            function () {
                open_bulk_import_dialog(listview);
            }
        );
    }
};

// --------------------------------------------------
//  Helper: normal Import
// --------------------------------------------------
function start_import(listview, names, item_group) {

    frappe.show_alert(
        { message: __("Import started…"), indicator: "blue" },
        5
    );

    frappe.call({
        method: "suppliercatalog.utils.sup_item_import.import_sci",
        args: {
            supplier_catalog_item_names: JSON.stringify(names),
            item_group: item_group
        },
        freeze: true,
        freeze_message: __("Import läuft...")
    }).then(() => {
        frappe.msgprint(__("Import finished."));
        listview.clear_checked_items();
        listview.refresh();
    });
}

// --------------------------------------------------
//  Bulk Import Dialog
// --------------------------------------------------
function open_bulk_import_dialog(listview) {

    frappe.db.get_single_value(
        "Supplier Catalog Settings",
        "itemgroup_ask"
    ).then(itemgroup_ask => {

        const dialog = new frappe.ui.Dialog({
            title: __("Bulk Import Items"),
            fields: [
                {
                    fieldname: "item_group",
                    fieldtype: "Link",
                    label: __("Artikelgruppe"),
                    options: "Item Group",
                    hidden: !itemgroup_ask,
                    reqd: itemgroup_ask
                },
                {
                    fieldname: "lookup_type",
                    fieldtype: "Select",
                    label: __("Identifikation über"),
                    options: [
                        "EAN Shop",
                        "Name",
                        "BIO-ID",
                        "Supplier Itemnumber"
                    ],
                    reqd: 1
                },
                {
                    fieldname: "lookup_values",
                    fieldtype: "Text",
                    label: __("Zu importierende Werte"),
                    description: __("Zeilen- oder Semikolon-getrennt"),
                    reqd: 1
                }
            ],
            primary_action_label: __("Import starten"),
            primary_action(values) {

                const parsed_values = values.lookup_values
                    .split(/[\n;]+/)
                    .map(v => v.trim())
                    .filter(v => v);

                if (!parsed_values.length) {
                    frappe.msgprint(__("Keine gültigen Werte gefunden."));
                    return;
                }

                if (itemgroup_ask && !values.item_group) {
                    frappe.msgprint(__("Bitte eine Artikelgruppe auswählen."));
                    return;
                }

                if (itemgroup_ask) {
                    start_bulk_import(
                        listview,
                        values.lookup_type,
                        parsed_values,
                        values.item_group
                    );
                } else {
                    frappe.db.get_single_value(
                        "Supplier Catalog Settings",
                        "itemgroup_select"
                    ).then(item_group => {
                        start_bulk_import(
                            listview,
                            values.lookup_type,
                            parsed_values,
                            item_group
                        );
                    });
                }

                dialog.hide();
            }
        });

        dialog.show();
    });
}

// --------------------------------------------------
//  Bulk Import Call + Ergebnisanzeige
// --------------------------------------------------
function start_bulk_import(listview, lookup_type, lookup_values, item_group) {

    frappe.show_alert(
        { message: __("Bulk Import gestartet…"), indicator: "blue" },
        5
    );

    frappe.call({
        method: "suppliercatalog.utils.sup_item_import.import_sci_bulk",
        args: {
            lookup_type: lookup_type,
            lookup_values: lookup_values,
            item_group: item_group
        },
        freeze: true,
        freeze_message: __("Import läuft...")
    }).then(r => {

        const data = r.message || {};

        let msg = `
            <b>Gefunden:</b> ${data.found?.length || 0}<br>
            <b>Importiert:</b> ${data.created?.length || 0}<br>
            <b>Übersprungen:</b> ${data.skipped?.length || 0}
        `;

        if (data.not_found && data.not_found.length) {
            msg += `<br><br><b>Nicht gefunden:</b><br>${data.not_found.join("<br>")}`;
        }

        frappe.msgprint({
            title: __("Bulk Import Ergebnis"),
            message: msg,
            indicator: data.not_found?.length ? "orange" : "green"
        });

        listview.refresh();
    });
}