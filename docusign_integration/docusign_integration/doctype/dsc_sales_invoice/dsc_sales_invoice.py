# Copyright (c) 2024, Extension and contributors
# For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document

# class DSCSalesInvoice(Document):
# 	pass


# import frappe
from frappe.model.document import Document

class DSCSalesInvoice(Document):
	def validate(self):
		if self.workflow_state:
			self.previous_state = self.workflow_state
