import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def add_property(doctype, fieldname, fetch_from, fieldtype):
    make_property_setter(
        doctype,
        fieldname,
        "fetch_from",
        fetch_from,
        fieldtype,
        validate_fields_for_doctype=False
    )
    frappe.db.commit()

def add_field_properties():
    add_property("Sales Invoice", "export_type", "Select Doctype", "Text")
    add_property("Sales Invoice", "gst_category", "Select Doctype", "Text")
    add_property("Sales Invoice Item", "gst_hsn_code", "Select Doctype", "Text")
    add_property("Sales Invoice Item", "is_nil_exempt", "Select Doctype", "Text")
    add_property("Sales Invoice Item", "is_non_gst", "Select Doctype", "Text")
    add_property("Purchase Order Item", "gst_hsn_code", "Select Doctype", "Text")
    add_property("Purchase Order Item", "is_nil_exempt", "Select Doctype", "Text")
    add_property("Purchase Order Item", "is_non_gst", "Select Doctype", "Text")

