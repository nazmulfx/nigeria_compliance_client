import frappe
from frappe.tests.utils import FrappeTestCase


class TestNRSBridgeSettings(FrappeTestCase):
	def test_settings_exists(self):
		settings = frappe.get_single("NRS Bridge Settings")
		self.assertIsNotNone(settings)
