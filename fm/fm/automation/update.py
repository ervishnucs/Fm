import frappe
from frappe.utils import nowdate, format_date

def expire_members_and_notify():
    today = nowdate()

    members_to_expire = frappe.get_all(
        "Member",
        filters={"end_date": today, "status": ["!=", "Expired"]},
        fields=["name", "full_name", "email", "membership_plan", "end_date"]
    )

    for member in members_to_expire:
        # Load full doc (optional, if you need to use it later)
        member_doc = frappe.get_doc("Member", member.name)

        # ✅ Update DB and memory
        frappe.db.set_value("Member", member.name, "status", "Expired")
        member_doc.status = "Expired"

        # ✅ Send email
        if member.email:
            subject = "Your Membership Has Expired"
            message = f"""
                <p>Dear <strong>{member.full_name}</strong>,</p>
                <p>Your membership plan <strong>{member.membership_plan}</strong> has expired today ({format_date(today)}).</p>
                <p>Please renew your plan to continue enjoying our services.</p>
                <p><a href="http://fit.local:8000/app/member-renwal/new-member" style="padding: 10px 15px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;">Renew Now</a></p>
                <p>Thank you!</p>
            """
            frappe.sendmail(
                recipients=[member.email],
                subject=subject,
                message=message
            )

# Run the function
expire_members_and_notify()
