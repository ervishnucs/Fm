import frappe
from frappe.utils import nowdate, add_days

def send_weekly_expiry_summary():
    today = nowdate()
    last_week = add_days(today, -7)

    # Fetch expired memberships
    expired = frappe.db.get_all('Member',
        filters={
            'end_date': ['between', [last_week, today]],
            'status': 'Expired'
        },
        fields=['full_name', 'membership_plan', 'end_date'],
        order_by='end_date desc'
    )

    if not expired:
        summary = "<p>No memberships expired in the last 7 days.</p>"
    else:
        # Build HTML table with S.No.
        summary = """
            <h3>Weekly Expired Memberships Summary</h3>
            <table style="border-collapse: collapse; width: 100%;" border="1" cellpadding="6">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th>S.No.</th>
                        <th>Full Name</th>
                        <th>Membership Plan</th>
                        <th>End Date</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx, m in enumerate(expired, start=1):
            summary += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{m.full_name}</td>
                    <td>{m.membership_plan}</td>
                    <td>{m.end_date}</td>
                </tr>
            """

        summary += f"""
                </tbody>
                <tfoot>
                    <tr style="font-weight: bold;">
                        <td colspan="3">Total Expired</td>
                        <td>{len(expired)}</td>
                    </tr>
                </tfoot>
            </table>
        """

    # Send the email
    frappe.sendmail(
        recipients=["ervishnucs369@gmail.com"],  # Update to your recipient
        subject="Weekly Expired Memberships Summary",
        message=summary
    )

    frappe.msgprint(" Weekly summary email sent with S.No.")
