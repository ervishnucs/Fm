frappe.ui.form.on('Member', {
    refresh: function(frm) {
        const today = frappe.datetime.get_today();

        // Show 'Renew Membership' if expired
        if (frm.doc.end_date && frm.doc.end_date <= today) {
            frm.add_custom_button('Renew Membership', () => {
                frappe.new_doc('Member Renewal', {
                    name1: frm.doc.name
                });
            });
        }

        // Show 'Clear Dues' if status is Pending and not paid
        if (frm.doc.status === 'Pending' && !frm.doc.paid) {
            frm.add_custom_button('Make Payment', () => {
                frappe.new_doc('Member Renewal', {
                    name1: frm.doc.name
                });
            });
        }
        
    },

    onload: function(frm) {
        if (frm.is_new()) {
            // Set start_date to today if not already set
            if (!frm.doc.start_date) {
                frm.set_value('start_date', frappe.datetime.get_today());
            }
            frm.set_value('status', 'Pending');

            
        
        }
    },
    
    mode_of_payment: function(frm) {
        const mode = frm.doc.mode_of_payment;

        if (mode === 'None') {
            frm.set_value('status', 'Pending');
            frm.set_value('paid', 0);
            frappe.msgprint('Choose a valid Mode of Payment.');
        } else {
            frm.set_value('paid', 1);
            if (frm.doc.status !== 'Active') {
                frm.set_value('status', 'Active');
            }
        }
    },

    status: function(frm) {
        if (frm.doc.status === 'Pending') {
            frm.set_value('paid', 0);
        } else if (frm.doc.status === 'Active') {
            frm.set_value('paid', 1);
        }
    },

    end_date: function(frm) {
        const today = frappe.datetime.get_today();

        if (frm.doc.end_date) {
            if (frm.doc.end_date <= today) {
                if (frm.doc.paid === 1) {
                    frm.set_value('status', 'Expired');
                } else {
                    frm.set_value('status', 'Pending');
                }
            } 
        }
    },

   
});

// ✅ Email validation helper (currently unused)
function is_valid_email(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email);
}
