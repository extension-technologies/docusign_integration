# Copyright (c) 2024, Extension and contributors
# For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document

# class DigitalSignatureDocument(Document):
# 	pass


import frappe
from frappe.model.document import Document
from docusign_integration.api import create_doctype

class DigitalSignatureDocument(Document):
    def validate(self):
        if not self.workflow and not self.do_not_create_workflow:
            self.create_workflow()
    
    def create_workflow(self):
        try:
            if not frappe.db.exists("DocType",f"DSC {self.document_type}"):
                create_doctype(self.document_type)
            workflow_state_list = ["DSC 1 Completed","DSC 2 Completed","DSC 3 Completed","DSC Completed"]
            workflow_internal_list = ["DSC 1 Signing","DSC 2 Signing","DSC 3 Signing","DSC Signing"]
            workflow_action_list = ["DSC 1","DSC 2","DSC 3","DSC 4"]
            default_workflow_state = ["DSC Signing","DSC Completed","Submitted","Cancelled"]
            
            for state in default_workflow_state:
                if not frappe.db.exists("Workflow State",state):
                    state_doc = frappe.new_doc("Workflow State")
                    state_doc.workflow_state_name = state
                    state_doc.save()

            if not frappe.db.exists("Workflow Action Master","Cancel"):
                action_doc = frappe.new_doc("Workflow Action Master")
                action_doc.workflow_action_name = "Cancel"
                action_doc.save()
            
            if not self.workflow and frappe.db.exists("Workflow",f"DSC {self.document_type}"):
                self.workflow= f"DSC {self.document_type}"

            if not self.role_1 and not self.role_2 and not self.role_3 and not self.role_4:
                frappe.throw(f"Row {self.idx} : Please select role to create workflow")

            if self.document_type and not frappe.db.exists("Workflow",f"DSC {self.document_type}"):	
                workflow = frappe.new_doc("Workflow")
                workflow.workflow_name = f"DSC {self.document_type}"
                # workflow.document_type = "Digital Signature"
                workflow.document_type = f"DSC {self.document_type}"
                workflow.sent_email_alert = 0
                workflow.is_active = 1
            
                if self.role_1:
                    next_state = next_internal_state = workflow_internal_list[0]
                    
                    if not frappe.db.exists("Workflow State",workflow_state_list[0]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_state_list[0]
                        state_doc.save()
                    if not frappe.db.exists("Workflow State",workflow_internal_list[0]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_internal_list[0]
                        state_doc.save()
                    if not frappe.db.exists("Workflow Action Master",workflow_action_list[0]):
                        action_doc = frappe.new_doc("Workflow Action Master")
                        action_doc.workflow_action_name = workflow_action_list[0]
                        action_doc.save()

                    workflow.append("states",{
                        "state": "Submitted",
                        "doc_status": 1,
                        "allow_edit": self.role_1
                    })
                    workflow.append("transitions",{
                        "state": "Submitted",
                        "action": workflow_action_list[0],
                        "next_state": next_internal_state,
                        "allowed": self.role_1
                    }) 
                    workflow.append("transitions",{
                        "state": "Submitted",
                        "action": "Cancel",
                        "next_state": "Cancelled",
                        "allowed": self.role_1
                    })
                    if not self.role_2 and not self.role_3 and not self.role_4:
                        next_state = "DSC Completed"
                        next_internal_state = "DSC Signing"
                        
                        workflow.append("states",{
                            "state": "DSC Signing",
                            "doc_status": 1,
                            "allow_edit": self.role_1
                        })
                        workflow.append("states",{
                            "state": "DSC Completed",
                            "doc_status": 1,
                            "allow_edit": self.role_1
                        })
                        workflow.append("transitions",{
                            "state": next_state,
                            "action": "Cancel",
                            "next_state": 'Cancelled',
                            "allowed": self.role_1
                        })
                    else:
                        workflow.append("states",{
                            "state": workflow_internal_list[0],
                            "doc_status": 1,
                            "allow_edit": self.role_1
                        })
                        workflow.append("states",{
                            "state": workflow_state_list[0],
                            "doc_status": 1,
                            "allow_edit": self.role_1
                        })
                        workflow.append("states",{
                            "state": "Cancelled",
                            "doc_status": 2,
                            "allow_edit": self.role_1
                        })

                if self.role_2:
                    next_state = next_internal_state = workflow_internal_list[1]
                    if not self.role_3 and not self.role_4:
                        next_state = "DSC Completed"
                        next_internal_state = "DSC Signing"
                        
                        workflow.append("states",{
                            "state": "DSC Signing",
                            "doc_status": 1,
                            "allow_edit": self.role_2
                        })
                        workflow.append("states",{
                            "state": "DSC Completed",
                            "doc_status": 1,
                            "allow_edit": self.role_2
                        })
                        workflow.append("transitions",{
                            "state": next_state,
                            "action": "Cancel",
                            "next_state": 'Cancelled',
                            "allowed": self.role_2
                        })
                    else:
                        workflow.append("states",{
                            "state": workflow_internal_list[1],
                            "doc_status": 1,
                            "allow_edit": self.role_2
                        })
                        workflow.append("states",{
                            "state": workflow_state_list[1],
                            "doc_status": 1,
                            "allow_edit": self.role_2
                        })
                        workflow.append("states",{
                            "state": "Cancelled",
                            "doc_status": 2,
                            "allow_edit": self.role_2
                        })

                    if not frappe.db.exists("Workflow State",workflow_state_list[1]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_state_list[1]
                        state_doc.save()
                    if not frappe.db.exists("Workflow State",workflow_internal_list[1]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_internal_list[1]
                        state_doc.save()
                    if not frappe.db.exists("Workflow Action Master",workflow_action_list[1]):
                        action_doc = frappe.new_doc("Workflow Action Master")
                        action_doc.workflow_action_name = workflow_action_list[1]
                        action_doc.save()
                
                    workflow.append("transitions",{
                        "state": workflow_state_list[0],
                        "action": workflow_action_list[1],
                        "next_state": next_internal_state,
                        "allowed": self.role_2
                    })
                    workflow.append("transitions",{
                        "state": workflow_state_list[0],
                        "action": "Cancel",
                        "next_state": "Cancelled",
                        "allowed": self.role_2
                    })

                if self.role_3:
                    next_state = next_internal_state = workflow_internal_list[2]
                    if not self.role_4:
                        next_state = "DSC Completed"
                        next_internal_state = "DSC Signing"
                        
                        workflow.append("states",{
                            "state": "DSC Signing",
                            "doc_status": 1,
                            "allow_edit": self.role_3
                        })
                        workflow.append("states",{
                            "state": "DSC Completed",
                            "doc_status": 1,
                            "allow_edit": self.role_3
                        })
                        workflow.append("transitions",{
                            "state": next_state,
                            "action": "Cancel",
                            "next_state": 'Cancelled',
                            "allowed": self.role_3
                        })
                    else:
                        workflow.append("states",{
                            "state": workflow_internal_list[2],
                            "doc_status": 1,
                            "allow_edit": self.role_3
                        })
                        workflow.append("states",{
                            "state": workflow_state_list[2],
                            "doc_status": 1,
                            "allow_edit": self.role_3
                        })
                        workflow.append("states",{
                            "state": "Cancelled",
                            "doc_status": 2,
                            "allow_edit": self.role_3
                        })

                    if not frappe.db.exists("Workflow State",workflow_state_list[2]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_state_list[2]
                        state_doc.save()
                    if not frappe.db.exists("Workflow State",workflow_internal_list[2]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_internal_list[2]
                        state_doc.save()
                    if not frappe.db.exists("Workflow Action Master",workflow_action_list[2]):
                        action_doc = frappe.new_doc("Workflow Action Master")
                        action_doc.workflow_action_name = workflow_action_list[2]
                        action_doc.save()

                    workflow.append("transitions",{
                        "state": workflow_state_list[1],
                        "action": workflow_action_list[2],
                        "next_state":next_internal_state,
                        "allowed": self.role_3
                    })
                    workflow.append("transitions",{
                        "state": workflow_state_list[1],
                        "action": "Cancel",
                        "next_state": "Cancelled",
                        "allowed": self.role_3
                    })

                if self.role_4:
                    next_state = next_internal_state = workflow_internal_list[3]
                    
                    workflow.append("states",{
                        "state": "DSC Signing",
                        "doc_status": 1,
                        "allow_edit": self.role_4
                    })
                    workflow.append("states",{
                        "state": "DSC Completed",
                        "doc_status": 1,
                        "allow_edit": self.role_4
                    })
                    workflow.append("transitions",{
                        "state": next_state,
                        "action": "Cancel",
                        "next_state": 'Cancelled',
                        "allowed": self.role_4
                    })
                    if not frappe.db.exists("Workflow State",workflow_state_list[3]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_state_list[3]
                        state_doc.save()
                    if not frappe.db.exists("Workflow State",workflow_internal_list[3]):
                        state_doc = frappe.new_doc("Workflow State")
                        state_doc.workflow_state_name = workflow_internal_list[3]
                        state_doc.save()
                    if not frappe.db.exists("Workflow Action Master",workflow_action_list[3]):
                        action_doc = frappe.new_doc("Workflow Action Master")
                        action_doc.workflow_action_name = workflow_action_list[3]
                        action_doc.save()

                    workflow.append("states",{
                        "state": "Cancelled",
                        "doc_status": 2,
                        "allow_edit": self.role_4
                    })
                    workflow.append("transitions",{
                        "state": workflow_state_list[2],
                        "action": workflow_action_list[3],
                        "next_state": next_internal_state,
                        "allowed": self.role_4
                    })
                    workflow.append("transitions",{
                        "state": workflow_state_list[2],
                        "action": "Cancel",
                        "next_state": "Cancelled",
                        "allowed": self.role_4
                    })
                
                workflow.save(ignore_permissions=True)
                self.workflow = workflow.name
                    
        except Exception as e:
            frappe.logger("docusign").exception(e)
