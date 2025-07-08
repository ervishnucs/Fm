import frappe
from frappe.utils import nowdate, format_date

def create_membership_payment(doc, method):
    if doc.paid:
        try:
            frappe.get_doc({
                "doctype": "Membership Payment",
                "name1": doc.full_name,
                "amount": doc.fee,
                "mode_of_payment": doc.mode_of_payment,
                "date": nowdate(),
                "paid": 1,
                
            }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Insert Error: {e}", "Membership Payment Insertion Failed")
            frappe.msgprint(f"Error creating membership payment: {e}")

    elif doc.status == "Pending" and not doc.paid:
        try:
            member = frappe.get_doc("Member", doc.full_name)
            
            if member.email:
                subject = "Your Membership is still Pending!"
                message = f"""
                    <p>Dear <strong>{member.full_name}</strong>,</p>
                    <p>Please note that your membership plan <strong>{member.membership_plan}</strong> is still pending.</p>
                    <p>We noticed that you have not completed your payment yet, and your membership is valid till <strong>{format_date(member.end_date)}</strong>. The membership fees is <strong>{member.fee}</strong>.</p>
                    <p>Complete your pending dues to continue enjoying our services.</p>
                    <p><a href="http://fit.local:8000/app/member-renewal/new?name1={member.name}" style="padding: 10px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Renew Now</a></p>
                    <p>Thank you!</p>
                """
                frappe.sendmail(
                    recipients=[member.email],
                    subject=subject,
                    message=message
                )
                frappe.msgprint("Your membership is still pending! Please complete your payment to activate your membership.")
        except Exception as e:
            frappe.log_error(f"Email Error: {e}", "Membership Payment Reminder Failed")
            frappe.msgprint(f"Failed to send reminder email: {e}")
