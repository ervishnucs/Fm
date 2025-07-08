import frappe
from frappe.utils import nowdate, add_days, format_date

def pending_renewal():
    reminder_days = 14  
    reminder_date = add_days(nowdate(), reminder_days)

    expiring_members = frappe.get_all(
        "Member",
        filters={"end_date": reminder_date, "status": "Pending"},
        fields=["name", "full_name", "email", "membership_plan", "end_date"]
    )

    for member in expiring_members:
        if member.email:
            subject = "Your Membership is still Pending!"
            message = f"""
                <p>Dear <strong>{member.full_name}</strong>,</p>
                <p>Please note that your membership plan <strong>{member.membership_plan}</strong> is still pending.</p>
                <p>We noticed that you have not completed your payment yet, and your membership is set to expire on <strong>{format_date(member.end_date)}</strong>. And The membership fees is <strong>{member.membership_fees}</strong>.</p>
                <p>Complete your pending dues to continue enjoying our services.</p>
                <p><a href="http://fit.local:8000/app/member-renewal/new?name1={member.name}" style="padding: 10px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Renew Now</a></p>
                <p>Thank you!</p>
            """

            frappe.sendmail(
                recipients=[member.email],
                subject=subject,
                message=message
            )


