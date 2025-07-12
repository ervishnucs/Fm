# Copyright (c) 2025, V and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestMembershipPlan(FrappeTestCase):
	def test_membership_plan_creation(self):
		# Create a new membership plan
		membership_plan = frappe.get_doc({
			"doctype": "Membership Plan",
			"plan": "Test Plan",
			"monthly_fee": 500,
			"duration": 12,
			
		})
		membership_plan.insert()

		self.assertEqual(membership_plan.total_fee, 6000.00)
