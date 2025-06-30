import frappe
from frappe.model.document import Document

class MembershipPlan(Document):
    def after_insert(self):
        self.send_plan_notification(is_new=True)

    def on_update(self):
        # Check if this is NOT a new insert to avoid duplicate emails
        if not self.flags.in_insert:
            self.send_plan_notification(is_new=False)

    def send_plan_notification(self, is_new=False):
        # Get all active members with emails
        members = frappe.get_all("Member",
            filters={"status": "Active"},
            fields=["full_name", "email"]
        )

        if not members:
            return

        # Prepare common plan details
        plan_name = self.plan
        membership_fee = f"₹{self.total_fee}"
        duration = f"{self.duration} months" if self.duration else "Not specified"

        # Email subject and body
        if is_new:
            subject = f"New Membership Plan Launched: {plan_name}"
            message = f"""
            <p>Dear Member,</p>
            <p>We’re excited to announce a <strong>new membership plan</strong>:</p>
            <ul>
                <li><strong>Plan Name:</strong> {plan_name}</li>
                <li><strong>Membership Fee:</strong> {membership_fee}</li>
                <li><strong>Duration:</strong> {duration}</li>
            </ul>
            <p>You can now choose this plan from your member portal.</p>
            <p>Thank you,<br>The Membership Team</p>
            """
        else:
            subject = f"Membership Plan Updated: {plan_name}"
            message = f"""
            <p>Dear Member,</p>
            <p>The following membership plan has been <strong>updated</strong>:</p>
            <ul>
                <li><strong>Plan Name:</strong> {plan_name}</li>
                <li><strong>Updated Membership Fee:</strong> {membership_fee}</li>
                <li><strong>Duration:</strong> {duration}</li>
            </ul>
            <p>Please review your current plan or explore new options in your portal.</p>
            <p>Thank you,<br>The Membership Team</p>
            """

       
        for member in members:
            if member.email:
                frappe.sendmail(
                    recipients=[member.email],
                    subject=subject,
                    message=message
                )
