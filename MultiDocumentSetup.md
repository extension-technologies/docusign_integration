# Multiple Document Sign for you have to need some setup are required.

1. Go to Digital Signature Document.
2. Add Configuration like for any Doctype you can select Sales order.
3. If you search DSC Sales Order you got list view .
4. You need to add client sctip for this doctype :
```bash
    frappe.ui.form.on('DSC Sales Order', {
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
    })


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

```


5. Here you remove your Actual Doctype created from.

6. After this you add server script on doc event Before Validate.
```bash
	if doc.document_type and not frappe.db.exists("Custom Field",{'dt':doc.document_type,'fieldname':'dsc_status'}):
		status = frappe.new_doc("Custom Field")
		status.dt = doc.document_type
		status.label = 'DSC Status'
		status.fieldname = 'dsc_status'
		status.fieldtype = "Data"
		status.allow_on_submit = 1
		status.read_only = 1
		status.no_copy = 1 
		status.save()
	if doc.workflow_state:
		doc.previous_state = doc.workflow_state

```

<br>
save this document Your Document is ready for Sign.





