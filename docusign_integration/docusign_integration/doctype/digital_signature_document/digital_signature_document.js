// Copyright (c) 2024, Extension and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Digital Signature Document', {
// 	// refresh: function(frm) {

// 	// }
// });

frappe.ui.form.on('Digital Signature Document', {
	setup: function(frm) {
		frm.set_query("entity_type", function() {
			return {"filters": {
				'is_submittable': 1
			}};
		});
		frm.set_query("print_format", function(doc) {
			return {"filters": {
				'doc_type': doc.entity_type
			}};
		});
		frm.set_query("workflow", function(doc) {
			return {"filters": {
				'document_type': "Digital Signature"
			}};
		});
	},
});