# Copyright (c) 2024, Extension and contributors
# For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document

# class DocusignResponseLog(Document):
# 	pass

import frappe
from frappe.model.document import Document

class DocusignResponseLog(Document):
	pass


def create_response_log(response,api,document_type=None,document_name=None):
	doc = frappe.new_doc("Docusign Response Log")
	doc.document_type = document_type
	doc.document_name = document_name
	doc.response = response
	doc.api = api
	doc.save(ignore_permissions=True)
	return