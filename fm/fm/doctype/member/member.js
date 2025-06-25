frappe.ui.form.on('Member', {
    refresh: function(frm) {
        frm.add_custom_button('Renew Membership', () => {
            frappe.new_doc('MEMBER RENWAL', {
                name1: frm.doc.name  
            });
        });
    },

    email: function(frm) {
        if (frm.doc.email && !is_valid_email(frm.doc.email)) {
            frappe.msgprint(__('Please enter a valid email address.'));
            
        }
    },

    // Auto-set start_date on new member creation
    onload: function(frm) {
        if (frm.is_new() && !frm.doc.start_date) {
            frm.set_value('start_date', frappe.datetime.get_today());
        }
    }
});

// ✅ Helper function to validate email
function is_valid_email(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}


 