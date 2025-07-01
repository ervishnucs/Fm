frappe.ui.form.on('Member', {
    refresh: function(frm) {
        frm.add_custom_button('Renew Membership', () => {
            frappe.new_doc('Member Renewal', {
                name1: frm.doc.name  
            });
        });
    },

    onload: function(frm) {
        if (frm.is_new() && !frm.doc.start_date) {
            frm.set_value('start_date', frappe.datetime.get_today());
        }
    },

    email: function(frm) {
        const email = frm.doc.email || '';
        const $input = frm.fields_dict.email.$wrapper.find('input');

        if (email && !is_valid_email(email)) {
            // Apply red border if invalid
            $input.css({
                'border': '1px solid red'
            });

            frm.disable_save();
        } else {
            // Reset style if valid
            $input.css({
                'border': '',
                'background-color': ''
            });

            frm.enable_save();
        }
    },

    mode_of_payment: function(frm) {
        if (frm.doc.mode_of_payment === 'None') {
            frm.set_value('status', 'Pending');
        }
    }
});

// Helper function (define only once)
function is_valid_email(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}
