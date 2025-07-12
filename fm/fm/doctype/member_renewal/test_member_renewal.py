import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days

class TestMemberRenewal(FrappeTestCase):
    def setUp(self):
        self.cleanup_docs()
        self.create_test_plan_and_member()

    def cleanup_docs(self):
        for doctype, name in [("Membership Plan", "Beginner"), ("Member", "Arjun")]:
            if frappe.db.exists(doctype, name):
                frappe.delete_doc(doctype, name, force=1)

        frappe.db.delete("Member Renewal", {"name1": "Arjun"})
        frappe.db.delete("Membership Payment", {"name1": "Arjun"})

    def create_test_plan_and_member(self):
        self.plan = frappe.get_doc({
            "doctype": "Membership Plan",
            "plan": "Beginner",
            "duration": 3,
            "monthly_fee": 1500
        }).insert(ignore_permissions=True)

        self.member = frappe.get_doc({
            "doctype": "Member",
            "full_name": "Arjun",
            "status": "Expired",
            "email": "arjun@example.com",
            "paid": 1,
            "mode_of_payment": "Cash",
            "membership_plan": "Trial",
            "fee": 1000,
            "start_date": '2023-01-01',
            "end_date": '2023-01-31'
        }).insert(ignore_permissions=True)

    def create_renewal(self, **kwargs):
        renewal = frappe.get_doc({
            "doctype": "Member Renewal",
            "name1": self.member.name,
            "renewal_date": nowdate(),
            **kwargs
        }).insert(ignore_permissions=True)

        renewal.run_method("after_insert")
        return renewal

    def assert_member_state(self, status, paid, plan, fee):
        member = frappe.get_doc("Member", self.member.name)
        self.assertEqual(member.status, status)
        self.assertEqual(member.paid, paid)
        self.assertEqual(member.membership_plan, plan)
        self.assertEqual(member.fee, fee)

    def assert_payment_exists(self, amount, mode, should_exist=True):
        payments = frappe.get_all("Membership Payment", filters={
            "name1": self.member.full_name,
            "amount": amount,
            "mode_of_payment": mode,
            "paid": 1,
            "date": nowdate()
        })
        self.assertEqual(bool(payments), should_exist)

    def test_expired_member_renewal_paid(self):
        renewal = self.create_renewal(
            new_plan=self.plan.name,
            currency_myrw=self.plan.monthly_fee * self.plan.duration,
            new_validity=add_days(nowdate(), self.plan.duration * 30),
            renew_paid=1,
            custom_mode_of_payment="Cash"
        )
        self.assert_member_state("Active", 1, "Beginner", 4500.00)
        self.assertEqual(frappe.get_doc("Member Renewal", renewal.name).now_paid, 1)
        self.assert_payment_exists(4500.00, "Cash", True)

    def test_expired_member_renewal_not_paid(self):
        self.create_renewal(
            new_plan=self.plan.name,
            new_validity=add_days(nowdate(), self.plan.duration * 30),
            renew_paid=0,
            custom_mode_of_payment="Cash"
        )
        self.assert_member_state("Expired", 1, "Trial", 1000.00)
        self.assert_payment_exists(4500.00, "Cash", False)

    def test_expired_member_renewal_mode_of_payment_none(self):
        self.create_renewal(
            new_plan=self.plan.name,
            new_validity=add_days(nowdate(), self.plan.duration * 30),
            renew_paid=1,
            custom_mode_of_payment="None"
        )
        self.assert_member_state("Expired", 1, "Trial", 1000.00)
        self.assert_payment_exists(4500.00, "Cash", False)

    def test_expired_member_renewal_not_paid_mode_of_payment_none(self):
        self.create_renewal(
            new_plan=self.plan.name,
            new_validity=add_days(nowdate(), self.plan.duration * 30),
            renew_paid=0,
            custom_mode_of_payment="None"
        )
        self.assert_member_state("Expired", 1, "Trial", 1000.00)
        self.assert_payment_exists(4500.00, "Cash", False)

    def test_expired_member_renewal_without_plan(self):
        self.create_renewal(
            renew_paid=0,
            custom_mode_of_payment="None"
        )
        self.assert_member_state("Expired", 1, "Trial", 1000.00)
        self.assert_payment_exists(4500.00, "Cash", False)

    def test_pending_member_with_payment_without_mode(self):
        self.member.update({
            "status": "Pending",
            "paid": 0,
            "mode_of_payment": "None",
            "start_date": nowdate(),
            "end_date": add_days(nowdate(), 30)
        })
        self.member.save(ignore_permissions=True)

        renewal = self.create_renewal(now_paid=1, mode_of_payment="None")
        self.assert_member_state("Pending", 0, "Trial", 1000.00)
        self.assertEqual(frappe.get_doc("Member Renewal", renewal.name).now_paid, 0)
        self.assert_payment_exists(4500.00, "Cash", False)

    def test_pending_member_with_payment_with_mode(self):
        self.member.update({
            "status": "Pending",
            "paid": 0,
            "mode_of_payment": "None"
        })
        self.member.save(ignore_permissions=True)

        renewal = self.create_renewal(now_paid=1, paid=0, mode_of_payment="UPI")
        self.assert_member_state("Expired", 1, "Trial", 1000.00)
        renewal_doc = frappe.get_doc("Member Renewal", renewal.name)
        self.assertEqual(renewal_doc.now_paid, 1)
        self.assertEqual(renewal_doc.mode_of_payment, "UPI")
        self.assertEqual(renewal_doc.paid, 1)
        self.assert_payment_exists(1000.00, "UPI", True)

    def tearDown(self):
        self.cleanup_docs()
