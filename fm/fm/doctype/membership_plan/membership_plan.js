
frappe.ui.form.on('Membership Plan', {
    monthly_fee: function(frm) {
        calculate_total_fee(frm);
    },
    duration: function(frm) {
        calculate_total_fee(frm);
    }
});

function calculate_total_fee(frm) {
    if (frm.doc.monthly_fee && frm.doc.duration) {
        frm.set_value('total_fee', frm.doc.monthly_fee * frm.doc.duration);
    }
}
