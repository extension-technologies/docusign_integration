// Copyright (c) 2024, Extension and contributors
// For license information, please see license.txt

frappe.ui.form.on('DSC Sales Invoice', {
	setup: function (frm) {
		frm.set_query("document", function () {
			return {
				"filters": {
					'docstatus': 1
				}
			};
		});
	},
	before_workflow_action: function (frm) {
		console.log('before')
		console.log(frm.doc.workflow_action)
	},
	after_workflow_action: function (frm) {
		if (frm.doc.workflow_action != "Cancel") {
			trigger_docusign_authorization(frm);
		}
	}
});

function trigger_docusign_authorization(frm) {
	frappe.call({
		'method': "docusign_integration.dsc_api.get_access_code",
		'args': {
			'doctype': frm.doc.doctype,
			'docname': frm.doc.name
		},
		freeze: true,
		freeze_message: __("Sending to Docusign"),
		'callback': function (r) {
			if (r.message) {
				window.location.href = r.message;
			} else {
				// Handle error -  provide informative message to user
				frappe.throw({ title: "Docusign Error", message: "Error initiating Docusign signing." });
			}
		},
		'error': function () {
			frappe.throw({ title: "Docusign Error", message: "Error communicating with Docusign." });
		},
	});
}



// let url = https://account-d.docusign.com/oauth/auth?response_type=code&state=DSC%20Sales%20Invoice|DSCSI-0010&scope=signature&client_id=006117e2-d681-4bb0-ba12-06aabfa911d9&redirect_uri=http://0.0.0.0:8001/api/method/docusign_integration.dsc_api.auth_login