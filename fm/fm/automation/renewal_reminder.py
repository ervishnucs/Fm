# fm/automation/renewal_reminder.py

import frappe
from datetime import date, timedelta

def send_renewal_reminder():
    target_date = date.today() + timedelta(days=7)

    members = frappe.get_all("Member", 
        filters={"end_date": target_date, "status": "Active"},
        fields=["full_name", "email", "end_date"]
    )

    for member in members:
        if not member.email:
            continue

        subject = "⚠️ Membership Expiry Reminder - Action Required"
      
        message = f"""
        <div style="font-family:Arial, sans-serif; max-width:600px; margin:auto; border:1px solid #eee; padding:20px; border-radius:10px; background-color:#f9f9f9;">
            <h2 style="color:#003366;">Hello {member.full_name},</h2>
            <p style="font-size:16px;">We hope you’re enjoying your time with us at <strong>Fitness Club</strong>!</p>
            <p style="font-size:16px; color:#cc0000;"><strong>Your membership is expiring today ({member.end_date}).</strong></p>
            <p style="font-size:16px;">To continue enjoying our facilities without interruption, please renew your membership today.</p>
            
            <p style="font-size:14px; color:#666; margin-top:20px;">If you have already renewed, please ignore this message.</p>
            <hr style="margin-top:30px;">
           
        </div>
        """

        frappe.sendmail(
            recipients=[member.email],
            subject=subject,
            message=message,
            delayed=False
        )
