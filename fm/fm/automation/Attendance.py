import frappe
from frappe.utils import today

def mark_absent_for_missing_attendance():
    today_date = today()

    # Get all active members (customize filter if needed)
    members = frappe.get_all("Member", filters={"status": "Active"}, fields=["name"])

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
