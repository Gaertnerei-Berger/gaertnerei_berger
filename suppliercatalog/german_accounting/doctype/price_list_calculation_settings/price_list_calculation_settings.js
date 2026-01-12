// Copyright (c) 2026, Gärtnerei Berger and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Price List Calculation Settings", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Price List Calculation Settings', {
    start_now(frm) {
        frappe.call({
            method: "suppliercatalog.german_accounting.doctype.price_list_calculation_settings.price_list_calculation_settings.run_price_list_calculation",
            freeze: true,
            freeze_message: __("Calculating price list…"),
        }).then(r => {
            const res = r.message || {};
            const errors = res.errors || [];

            let msg = `
                <b>Processed:</b> ${res.processed || 0}<br>
                <b>Created:</b> ${res.created || 0}<br>
                <b>Updated:</b> ${res.updated || 0}<br>
                <b>Skipped:</b> ${res.skipped || 0}<br>
            `;

            if (errors.length) {
                msg += `<br><br><b>Errors (VAT not determinable / mapping invalid):</b><br>`;
                msg += errors
                    .map(e => `${frappe.utils.escape_html(e.item_code)} (${frappe.utils.escape_html(e.uom)}): ${frappe.utils.escape_html(e.reason)}`)
                    .join("<br>");
            }

            frappe.msgprint({
                title: __("Price List Calculation Result"),
                message: msg,
                indicator: errors.length ? "orange" : "green"
            });

            frm.reload_doc();
        });
    }
});