frappe.listview_settings['Supplier Catalog Item'] = {
    add_fields: [
        "imported",
        "price_manual_changed",
        "supplier",
        "ean_shop",
        "name1"
    ],

    order_by: "supplier asc, name1 asc",

    refresh: function (listview) {
        setTimeout(() => {
            listview.data.forEach(function (rowData, index) {
                const $row = $(listview.$result.find('.list-row-container').get(index));

                // Only apply styling if one of the flags is set
                if (rowData.price_manual_changed == 1) {
                    // 🔶 Orange has priority
                    $row.css({
                        'background-color': '#e67300',
                        'color': '#ffffff'
                    });
                } else if (rowData.imported == 1) {
                    // ✅ Green if only imported
                    $row.css({
                        'background-color': '#267326',
                        'color': '#ffffff'
                    });
                }
                // ❌ Else: do not touch the row styling
            });
        }, 300);
    }
};
