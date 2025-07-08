# Copyright (c) 2025, V and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate ,


class TestMemberRenewal(FrappeTestCase):
	def setUp(self):
        # Create a test Member with status "Expired"
        self.member = frappe.get_doc({
            "doctype": "Member",
            "full_name": "Test Expired Member",            
            "status": "Expired",
            "email": "expired@example.com",
            "paid": 1,
            "mode_of_payment": "Cash",
            "membership_plan": "Trial",
			"fee": 1000,
            "start_date": nowdate(),

            "end_date": nowdate()
        }).insert(ignore_permissions=True)

       

    def test_expired_member_renewal(self):
        renewal_doc = frappe.get_doc({
            "doctype": "Member Renewal",
            "name1": self.member.name,
            "new_plan": "Beginner",           
            "renewal_date": nowdate(),            
            "renew_paid": 1,
            "custom_mode_of_payment": "Cash"
        })
        renewal_doc.insert(ignore_permissions=True)

        # Trigger the renewal logic
        renewal_doc.run_method("after_insert")

        # Reload documents
        updated_member = frappe.get_doc("Member", self.member.name)
        updated_renewal = frappe.get_doc("Member Renewal", renewal_doc.name)

        # Check if member is activated
        self.assertEqual(updated_member.status, "Active")
        self.assertEqual(updated_member.paid, 1)
        self.assertEqual(updated_member.mode_of_payment, "Cash")
        self.assertEqual(updated_member.membership_plan, "Beginner")

        # Check now_paid is marked on renewal
        self.assertEqual(updated_renewal.now_paid, 1)

        # Check payment entry exists
        payment = frappe.get_all("Membership Payment", filters={
            "name1": self.member.full_name,
            "amount": 1000,
            "mode_of_payment": "Cash",
			"paid": 1,
			"date": nowdate(),
			"time": nowtime()
        })
        self.assertTrue(payment, "Membership Payment  created.")

    #def tearDown(self):
        # frappe.delete_doc("Member", self.member.name, force=1)
        # frappe.db.sql("DELETE FROM `tabMember Renewal` WHERE name1 = %s", (self.member.name,))
        # frappe.db.sql("DELETE FROM `tabMembership Payment` WHERE name1 = %s", (self.member.full_name,))

