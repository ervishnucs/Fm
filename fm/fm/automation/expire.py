import frappe
from frappe.utils import nowdate, add_days, format_date

def send_renewal_reminders():
    reminder_days = 7  
    reminder_date = add_days(nowdate(), reminder_days)

    expiring_members = frappe.get_all(
        "Member",
        filters={"end_date": reminder_date, "status": "Active"},
        fields=["name", "full_name", "email", "membership_plan", "end_date"]
    )

    for member in expiring_members:
        if member.email:
            subject = "Your Membership is Expiring Soon!"
            message = f"""
                <p>Dear <strong>{member.full_name}</strong>,</p>
                <p>This is a gentle reminder that your membership plan <strong>{member.membership_plan}</strong> is expiring on <strong>{format_date(member.end_date)}</strong>.</p>
                <p>Please renew your plan to continue enjoying our services.</p>
                <p><a href="http://fit.local:8000/app/member-renwal/new-member" style="padding: 10px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Renew Now</a></p>
                <p>Thank you!</p>
            """

            frappe.sendmail(
                recipients=[member.email],
                subject=subject,
                message=message
            )


