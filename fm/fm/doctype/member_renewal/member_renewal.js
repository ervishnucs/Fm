frappe.ui.form.on('Member Renewal', {
    onload: function (frm) {
       
        if (!frm.doc.renewal_date) {
            const today = frappe.datetime.get_today();
            frm.set_value('renewal_date', today);
        }
    },
    new_plan: function(frm) {
        let renewed_date = frappe.datetime.add_months(frm.doc.renewal_date, frm.doc.durationin_months);
            let final_date = frappe.datetime.add_days(renewed_date, 1);
            frm.set_value('new_validity', final_date)
        },
    
     
    name1: function(frm) {
        if (!frm.doc.name1) return;

        frappe.db.get_doc('Member', frm.doc.name1).then(member => {
            if (member.status === 'Pending' && !member.paid) {
                frm.set_df_property('new_plan', 'hidden', 1);
                frm.set_df_property('currency_myrw', 'hidden', 1);
                frm.set_df_property('new_validity', 'hidden', 1);
                frm.set_df_property('custom_mode_of_payment', 'hidden', 1);
                frm.set_df_property('durationin_months', 'hidden', 1);
                 frm.set_df_property('renew_paid', 'hidden',1);

                frappe.msgprint(`Previous membership is unpaid. Please clear dues (₹${member.fee}) before renewal.`);
            } else {
                // Show fields again if user changes to a paid member
                frm.set_df_property('new_plan', 'hidden', 0);
                frm.set_df_property('currency_myrw', 'hidden', 0);
                frm.set_df_property('new_validity', 'hidden', 0);
                frm.set_df_property('custom_mode_of_payment', 'hidden', 0);
                frm.set_df_property('durationin_months', 'hidden', 0);
                frm.set_df_property('renew_paid', 'hidden', 0);

            }
            if( member.status === 'Expired' && member.paid ) {
                frm.set_df_property('paid', 'hidden', 1);
                frm.set_df_property('now_paid', 'hidden', 1);
                frm.set_df_property('mode_of_payment', 'hidden', 1);
            }else{
                frm.set_df_property('paid', 'hidden', 0);
                frm.set_df_property('now_paid', 'hidden', 0);
                frm.set_df_property('mode_of_payment', 'hidden', 0);
            }
            if (member.name) {
                    let field = frm.fields_dict.new_plan;

                    if (field.df.fieldtype === 'Select') {
                        // If it's a Select field with options
                        let options = field.df.options.split('\n');
                        let filtered = options.filter(opt => opt !== 'Trial');
                        field.df.options = filtered.join('\n');
                        frm.refresh_field('new_plan');
                    } else {
                        // If it's a Link field pointing to Membership Plan
                        frm.set_query('new_plan', function() {
                            return {
                                filters: [
                                    ['Membership Plan', 'name', '!=', 'Trial']
                                ]
                            };
                        });
                    }
                }
        });
    },

    refresh: function(frm) {
        // Run same logic on refresh
        if (frm.doc.name1) {
            frappe.db.get_doc('Member', frm.doc.name1).then(member => {
                const unpaid = member.status === 'Pending' && !member.paid;
                frm.set_df_property('new_plan', 'hidden', unpaid ? 1 : 0);
                frm.set_df_property('currency_myrw', 'hidden', unpaid ? 1 : 0);
                frm.set_df_property('new_validity', 'hidden', unpaid ? 1 : 0);
                frm.set_df_property('custom_mode_of_payment', 'hidden', unpaid ? 1 : 0);
                frm.set_df_property('durationin_months', 'hidden', unpaid ? 1 : 0);
                frm.set_df_property('renew_paid', 'hidden', unpaid ? 1 : 0);
                const expiredPaid = member.status === 'Expired' && member.paid;
                frm.set_df_property('paid', 'hidden', expiredPaid ? 1 : 0);
                frm.set_df_property('new_paid', 'hidden', expiredPaid ? 1 : 0);
                frm.set_df_property('mode_of_payment', 'hidden', expiredPaid ? 1 : 0);  
            });
        }
    },
      new_validity: function(frm) {
        const renewal_date = frm.doc.renewal_date;
        const duration = parseInt(frm.doc.durationin_months || 0);
        const selected_new_validity = frm.doc.new_validity;

        if (!renewal_date || !duration || !selected_new_validity) return;

        const renewal_date_obj = frappe.datetime.str_to_obj(renewal_date);
        const base_date = frappe.datetime.add_days(renewal_date, 1);  // start from next day after renewal

        const expected_new_validity = frappe.datetime.add_months(base_date, duration);
        const selected_validity_obj = frappe.datetime.str_to_obj(selected_new_validity);
        const expected_validity_obj = frappe.datetime.str_to_obj(expected_new_validity);

        // if (selected_validity_obj.getTime() !== expected_validity_obj.getTime()) {
            // frappe.msgprint(`Invalid New Validity: It should be exactly ${duration} month(s) after ${frappe.datetime.str_to_user(base_date)} → ${frappe.datetime.str_to_user(expected_new_validity)}.`);
            // frm.set_value('new_validity', null);
        // } else {
            // frappe.msgprint(`Validity OK: Your new plan is set from ${frappe.datetime.str_to_user(base_date)} to ${frappe.datetime.str_to_user(expected_new_validity)}.`);
        // }
    },
    paid: function(frm) {
        if (frm.doc.paid) {
            frm.set_value('now_paid', 1);
            
        }
    }
});



