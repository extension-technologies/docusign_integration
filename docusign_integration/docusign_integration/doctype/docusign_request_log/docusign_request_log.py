# Copyright (c) 2024, Extension and contributors
# For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document

# class DocusignRequestLog(Document):
# 	pass


import frappe
from frappe.model.document import Document

class DocusignRequestLog(Document):
	pass

def create_request_log(api,document_type=None,document_name=None,payload=None):
	doc = frappe.new_doc("Docusign Request Log")
	doc.document_type = document_type
	doc.document_name = document_name
	doc.payload = payload
	doc.api = api
	doc.save(ignore_permissions=True)
	return