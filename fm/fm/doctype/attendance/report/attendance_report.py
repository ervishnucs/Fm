# fm/fm/your_module/report/attendance_report/attendance_report.py

import frappe
from frappe.utils import getdate, get_time

def execute(filters=None):
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Checkin", "fieldname": "checkin", "fieldtype": "Time", "width": 100},
        {"label": "Checkout", "fieldname": "checkout", "fieldtype": "Time", "width": 100},
    ]

    data = frappe.db.get_all("Attendance", fields=["employee", "attendance_date as date", "checkin", "checkout"])

    return columns, data
