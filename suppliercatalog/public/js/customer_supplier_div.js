// Toggle visibility of the custom address section
function toggle_custom_address_section(frm) {

    // Determine party field and settings field based on doctype
    let party_field = null;
    let settings_field = null;

    if (frm.doctype === "Purchase Invoice") {
        party_field = "supplier";
        settings_field = "supplier_divers";
    } else if (frm.doctype === "Sales Invoice") {
        party_field = "customer";
        settings_field = "customer_divers";
    } else {
        return;
    }

    // No party selected, nothing to do
    if (!frm.doc[party_field]) return;

    // Load German Accounting Settings
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "German Accounting Settings"
        },
        callback: function (r) {
            if (!r.message) return;

            const settings = r.message;

            // Feature not enabled
            if (!settings.cust_sup_div) return;

            // Party does not match configured party
            if (settings[settings_field] !== frm.doc[party_field]) return;

            // All conditions met, show section
            frm.toggle_display("custom_custom_address", true);
            frm.set_df_property("custom_addressfield", "reqd", 1);
        }
    });
}

// Purchase Invoice hooks
frappe.ui.form.on("Purchase Invoice", {
    refresh: function (frm) {
        toggle_custom_address_section(frm);
    },
    supplier: function (frm) {
        toggle_custom_address_section(frm);
    }
});

// Sales Invoice hooks
frappe.ui.form.on("Sales Invoice", {
    refresh: function (frm) {
        toggle_custom_address_section(frm);
    },
    customer: function (frm) {
        toggle_custom_address_section(frm);
    }
});