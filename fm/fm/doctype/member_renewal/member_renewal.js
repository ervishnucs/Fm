frappe.ui.form.on('Member Renewal', {
    onload: function (frm) {
        // Set renewal_date to today if it's empty
        if (!frm.doc.renewal_date) {
            const today = frappe.datetime.get_today();
            frm.set_value('renewal_date', today);
        }
    },

    name1: function(frm) {
        if (!frm.doc.name1) return;

        // Fetch Member doc from server
        frappe.db.get_doc('Member', frm.doc.name1)
            .then(member => {
                // If member exists, filter out "Trial" from new_plan options
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
    }
});
