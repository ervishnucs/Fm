import frappe
from frappe.utils import today

def mark_absent_for_missing_attendance():
    today_date = today()

    members = frappe.get_all("Member", 
        filters=[
            ["status", "=", "Active"],
            "or",
            [
                ["status", "=", "Pending"],
                ["end_date", ">", nowdate()]
            ]
        ],
    
    fields=["name"]
)

    for member in members:
        
        exists = frappe.db.exists("Attendance", {
            "member": member.name,
            "date": today_date
        })

        if not exists:
            
            doc = frappe.get_doc({
                "doctype": "Attendance",
                "member": member.name,
                "date": today_date,
                "status": "Absent" 
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
