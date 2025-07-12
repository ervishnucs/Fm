import frappe
import traceback
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class MemberRenewal(Document):
    def after_insert(self):
       

        try:
            member = frappe.get_doc("Member", self.name1)

            if member.status not in ["Pending", "Expired"]:
                frappe.msgprint("Member status is not eligible for renewal. Only Pending or Expired members can renew.")
                return
            if self.renew_paid == 1 and  self.custom_mode_of_payment == "None" :
                self.renew_paid = 0
                self.save(ignore_permissions=True)
                frappe.msgprint("Please select a valid mode of payment for renewal.")   
                return 
            if self.now_paid == 1 and self.mode_of_payment == "None":
                self.now_paid = 0
                self.save(ignore_permissions=True)
                frappe.msgprint("Please select a valid mode of payment to clear pending dues.")
                return

                 
            # CASE 1: Renewing an expired member
            if self.renew_paid ==1 and self.custom_mode_of_payment!="None" and member.status == "Expired":
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

                payment = frappe.new_doc("Membership Payment")
                payment.update({
                    "name1": member.full_name,
                    "amount": self.currency_myrw,
                    "mode_of_payment": self.custom_mode_of_payment,
                    "date": self.renewal_date or nowdate(),
                    "paid": 1
                })
                payment.insert(ignore_permissions=True)

                frappe.msgprint(f"Membership renewed successfully with plan: {self.new_plan}.")

                if member.email and not frappe.flags.in_test:
                    self.send_confirmation_email(member)

            # CASE 2: Clearing pending dues
            elif self.now_paid and self.mode_of_payment and member.status == "Pending":
                if self.validity and getdate(self.validity) <= getdate(nowdate()):
                    member.update({
                        "paid": 1,
                        "mode_of_payment": self.mode_of_payment,
                        "status": "Expired"
                    })
                    self.db_set("paid", 1, update_modified=True)
                    self.save(ignore_permissions=True)
                else:
                    member.update({
                        "paid": 1,
                        "mode_of_payment": self.mode_of_payment,
                        "status": "Active"
                    })
                    self.db_set("paid", 1, update_modified=True)
                    self.save(ignore_permissions=True)
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

                frappe.msgprint("Pending dues cleared successfully.")
            else:
                frappe.msgprint("Invalid Payment !!!")
                return

        except Exception:
            if frappe.flags.in_test:
                frappe.db.rollback(savepoint="before_member_renewal")
            frappe.log_error(traceback.format_exc(), "Membership Renewal Critical Failure")
            frappe.msgprint("An unexpected error occurred during membership renewal.")
            return
        

    def send_confirmation_email(self, member):
        if frappe.flags.in_test:
             return 
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
