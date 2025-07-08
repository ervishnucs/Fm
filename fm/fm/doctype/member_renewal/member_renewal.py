import frappe
import traceback
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from frappe.utils import nowdate

class MemberRenewal(Document):
   

    
    def after_insert(self):
        try:
            member = frappe.get_doc("Member", self.name1)

            if member.status not in ["Pending", "Expired"]:
                frappe.msgprint("Member status is not eligible for renewal. Only Pending or Expired members can renew.")
                return

            if self.renew_paid and self.custom_mode_of_payment and member.status == 'Expired':
                try:
                    member.update({
                        "paid": 1,
                        "mode_of_payment": self.custom_mode_of_payment,
                        "membership_plan": self.new_plan,
                        "fee": self.currency_myrw,
                        "start_date": self.renewal_date,
                        "end_date": self.new_validity,
                        "status": "Active"
                    })
                    member.save(ignore_permissions=True)
                    self.now_paid = 1
                    self.save(ignore_permissions=True)

                    payment_name = frappe.db.get_value(
                        "Membership Payment",
                        {"name1": member.name, "date": self.renewal_date or nowdate()},
                        "name"
                    )
                    payment = frappe.get_doc("Membership Payment", payment_name) if payment_name else frappe.new_doc("Membership Payment")
                    payment.update({
                        "name1": member.full_name,  # Or member.name if it's ID-based
                        "amount": self.currency_myrw,
                        "mode_of_payment": self.custom_mode_of_payment,
                        "date": self.renewal_date or nowdate(),
                        "paid": 1,
                    })
                    payment.save(ignore_permissions=True)

                    frappe.msgprint(f"Membership renewed successfully with plan: {self.new_plan}.")
                    if member.email:
                        self.send_confirmation_email(member)

                except Exception as e:
                    frappe.log_error(traceback.format_exc(), "Renewal Failed")
                    frappe.msgprint(f"An error occurred during membership renewal: {e}")
                return

            #  CASE 2: Clearing pending dues
            elif self.now_paid and self.mode_of_payment and member.status == 'Pending':
                try:
                    if self.validity and getdate(self.validity) <= getdate(nowdate()):
                        member.update({
                        "paid": 1,
                        "mode_of_payment": self.mode_of_payment,
                        "status": "Expired"
                    })
                        member.save(ignore_permissions=True)
                        payment = frappe.new_doc("Membership Payment")
                        payment.update({
                        "name1": member.name,
                        "amount": member.fee,
                        "mode_of_payment": self.mode_of_payment,
                        "date": self.renewal_date or nowdate(),
                        "paid": 1,
                        "status": "Paid"
                    })
                        payment.insert(ignore_permissions=True)

                        frappe.msgprint(" Pending dues cleared successfully.")
                        return
                    else:
                        member.update({
                        "paid": 1,
                        "mode_of_payment": self.mode_of_payment,
                        "status": "Active"
                    })
                        member.save(ignore_permissions=True)
                        payment = frappe.new_doc("Membership Payment")
                        payment.update({
                        "name1": member.name,
                        "amount": member.fee,
                        "mode_of_payment": self.mode_of_payment,
                        "date": self.renewal_date or nowdate(),
                        "paid": 1,
                        "status": "Paid"
                    })
                        payment.insert(ignore_permissions=True)

                        frappe.msgprint(" Pending dues cleared successfully.")
                        return


                except Exception as e:
                    frappe.log_error(traceback.format_exc(), "Pending Payment Failed")
                    frappe.msgprint(f"An error occurred while clearing pending dues: {e}")
                return

        except Exception as e:
            frappe.log_error(traceback.format_exc(), "Membership Renewal Critical Failure")
            frappe.msgprint(f"An unexpected error occurred: {e}")

    def send_confirmation_email(self, member):
        message = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #e8f5e9;">
                <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9;">
                    <h2 style="color: #388e3c;">Membership Renewal Confirmed</h2>
                    <p>Dear <strong>{member.full_name}</strong>,</p>
                    <p>Your membership has been renewed. Here are the details:</p>
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr><td style="padding: 8px; border: 1px solid #ccc;"><strong>Plan</strong></td><td style="padding: 8px; border: 1px solid #ccc;">{self.new_plan}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ccc;"><strong>Validity</strong></td><td style="padding: 8px; border: 1px solid #ccc;">{self.new_validity}</td></tr>
                        <tr><td style="padding: 8px; border: 1px solid #ccc;"><strong>Payment Mode</strong></td><td style="padding: 8px; border: 1px solid #ccc;">{self.custom_mode_of_payment}</td></tr>
                    </table>
                    <p>Thank you for renewing your membership!</p>
                    <p style="font-size: 12px; color: #999;">This is an automated message. Please do not reply.</p>
                </div>
            </div>
        """
        try:
            if member.email:
                frappe.sendmail(
                    recipients=[member.email],
                    subject="Membership Renewal Confirmation",
                    message=message,
                    attachments=[
                        frappe.attach_print(
                            doctype=self.doctype,
                            name=self.name,
                            print_format="Membership Renewal",
                            file_name=f"Membership_Renewal_{self.name1}.pdf"
                        )
                    ]
                )
                
        except Exception as e:
            frappe.log_error(f"Email Sending Error: {e}", "Membership Renewal Email Failed")
            frappe.msgprint(f"Error sending confirmation email: {e}")
