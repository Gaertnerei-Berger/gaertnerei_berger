frappe.ui.form.on('Purchase Receipt', {
  refresh(frm) {
    frappe.db.get_single_value(
      'German Accounting Settings',
      'check_invoice_helper'
    ).then(v => {
      frm.toggle_display('custom_invoice_helper', !!v);
    });
  }
});