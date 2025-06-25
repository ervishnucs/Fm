

frappe.ui.form.on("Attendance", {
    onload: function(frm) {
        
        frm.set_query("member", function() {
            return {
                filters: {
                    status: "Active"
                }
            };
        });
    }
});
