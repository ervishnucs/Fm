frappe.ui.form.on('MEMBER RENWAL', {
    onload: function (frm) {
        // Set renewal_date to today if it's empty
        if (!frm.doc.renewal_date) {
            const today = frappe.datetime.get_today();
            frm.set_value('renewal_date', today);
        }
    }
});
