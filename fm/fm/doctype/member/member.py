import frappe
from frappe.model.document import Document

class Member(Document):
    def after_insert(self):
        if not self.email:
            return  # Skip if no email provided

        # Email content
        message = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="background: #fff; padding: 30px; border-radius: 8px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
                <h2 style="color: #28a745;">Welcome to Your Fitness Journey, {self.full_name}!</h2>
                <p>We’re excited to have you onboard at <strong>Fitness Center</strong>.</p>
                <p>Your fitness journey officially begins on <strong>{self.start_date}</strong>.</p>
                <p>Let’s get moving towards your goals together. 💪</p>
                <p>If you have any questions or need support, don’t hesitate to reach out.</p>
                <br>
                <p>Cheers,<br><strong>Fitness Center Team</strong></p>
                <hr>
                <p style="font-size: 12px; color: #888;">This is an automated email. Please do not reply.</p>
            </div>
        </div>
        """

        try:
            frappe.sendmail(
                recipients=[self.email],
                subject="🎉 Welcome to Your Fitness Journey!",
                message=message
            )
            frappe.msgprint(f"Welcome email sent to {self.email}")
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Failed to send welcome email")
