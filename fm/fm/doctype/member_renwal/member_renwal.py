import frappe
import traceback
from frappe.model.document import Document

class MEMBERRENWAL(Document):
    def on_submit(self):
        if self.name1 and self.new_plan and self.new_validity:
            try:
                # Update Member info
                member = frappe.get_doc("Member", self.name1)
                member.membership_plan = self.new_plan
                member.end_date = self.new_validity
                member.status = "Active"
                member.save(ignore_permissions=True)

                # Prepare HTML email
                if member.email:
                    html_message = f"""
                        <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8f8f8;">
                            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <h2 style="color: #007bff;">Membership Renewal Confirmation</h2>
                                <p>Dear <strong>{member.full_name}</strong>,</p>
                                <p>Your membership has been successfully renewed. Below are your updated details:</p>

                                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                                    <tr>
                                        <td style="padding: 8px; border: 1px solid #ccc;"><strong>Membership Plan</strong></td>
                                        <td style="padding: 8px; border: 1px solid #ccc;">{self.new_plan}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border: 1px solid #ccc;"><strong>New Validity</strong></td>
                                        <td style="padding: 8px; border: 1px solid #ccc;">{self.new_validity}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px; border: 1px solid #ccc;"><strong>Mode of Payment</strong></td>
                                        <td style="padding: 8px; border: 1px solid #ccc;">{self.custom_mode_of_payment or 'N/A'}</td>
                                    </tr>
                                </table>

                                <p>If you have any questions, feel free to contact us.</p>
                                <p>Thank you for choosing our services!</p>

                                <hr style="margin-top: 30px;">
                                <p style="font-size: 12px; color: #999;">This is an automated message. Please do not reply.</p>
                            </div>
                        </div>
                    """

                    # Generate PDF for the Member Renewal document
                    pdf_data = frappe.get_print(
                        doctype=self.doctype,
                        name=self.name,
                        print_format="Standard",  # Change if using a custom format
                        as_pdf=True
                    )

                    # Send email with HTML + PDF
                    frappe.sendmail(
                        recipients=[member.email],
                        subject="Membership Renewal Confirmation",
                        message=html_message,
                        attachments=[{
                            "fname": f"Membership Renewal - {self.name}.pdf",
                            "fcontent": pdf_data,
                            "encoding": "base64"
                        }],
                        reference_doctype=self.doctype,
                        reference_name=self.name
                    )

            except Exception:
                frappe.log_error(traceback.format_exc(), "Member Update or Email Failed")
                frappe.throw("An error occurred during membership update.")
        else:
            frappe.throw("Missing required details: Member, New Plan, or New Validity.")
