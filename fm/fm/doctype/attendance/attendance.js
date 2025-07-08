

frappe.ui.form.on("Attendance", {
       refresh: function(frm) {
        set_member_filter(frm);
    },

    onload: function(frm) {
        set_member_filter(frm);
    }
});

function set_member_filter(frm) {
    frm.set_query("member", function() {
        return {
            filters: [
                ["Member", [
                    ["status", "=", "Active"],
                    "or",
                    [
                        ["status", "=", "Pending"],
                        ["end_date", ">", frappe.datetime.get_today()]
                    ]
                ]]
            ]
        };
    });

}
