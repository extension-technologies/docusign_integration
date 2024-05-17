import frappe
from frappe.utils import get_url_to_form, now_datetime, get_fullname, get_bench_path, get_site_path, get_request_site_address
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
from urllib.parse import parse_qs, urlparse
from docusign_esign import EnvelopesApi, EnvelopeDefinition,EventNotification, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients, ApiClient, RecipientViewRequest

import requests
import base64
import os
import json
from docusign_integration.docusign_integration.doctype.docusign_response_log.docusign_response_log import create_response_log
from docusign_integration.docusign_integration.doctype.docusign_request_log.docusign_request_log import create_request_log


@frappe.whitelist()
def get_access_code(doctype, docname):
	base_url =  "https://account-d.docusign.com/oauth/auth"
	client_id = frappe.db.get_single_value('Docusign Settings','integration_key')
	docusign_settings = frappe.get_single('Docusign Settings')
	serverUrl = docusign_settings.server_url
	method = '/api/method/docusign_integration.dsc_api.auth_login'
	redirect_uri = f"{serverUrl}{method}"
	auth_url = f"{base_url}?response_type=code&state={doctype+'|'+docname}&scope=signature&client_id={client_id}&redirect_uri={redirect_uri}"
	return auth_url

@frappe.whitelist()
def auth_login():
	data = get_access_token()
	if data:
		return ("{0}?token={1}".format(get_signing_url
		(data['doctype'],data['docname'],data['access_token'],data['code']),data['access_token']))


def get_access_token():
	try:
		base_url = "https://account-d.docusign.com/oauth/token"
		docusign_settings = frappe.get_single('Docusign Settings')
		client_id = docusign_settings.integration_key
		client_secret_key = docusign_settings.get_password('secret_key')
		auth_code_string = '{0}:{1}'.format(client_id,client_secret_key)
		auth_token = base64.b64encode(auth_code_string.encode())
		parsed_qs = parse_qs(urlparse(frappe.request.url).query)
		code = parsed_qs['code'][0]
		document = parsed_qs['state'][0]
		doctype = document.split('|')[0]
		docname = document.split('|')[1]
		req_headers = {"Authorization":"Basic {0}".format(auth_token.decode('utf-8'))}
		post_data = {'grant_type':'authorization_code','code': code}
		create_request_log(base_url,payload=str(post_data))
		r = requests.post(base_url, data=post_data, headers=req_headers)
		response = r.json()
		create_response_log(str(response),base_url)

		if not 'error' in response:
			return {'access_token': response['access_token'],'doctype': doctype,'docname': docname, 'code': code }
	except Exception as e:
		frappe.logger("docusign").exception(e)


def get_signing_url(doctype, docname, token, code):
    try:
        ds_doc = frappe.get_doc(doctype, docname)
        ds_doc.code = code

        args = {
            "signer_email": ds_doc.signer_email if ds_doc.signer_email else "sonu@extensioncrm.com.com",
            "signer_name": ds_doc.signer_name if ds_doc.signer_name else 'sonu kumar',
            "client_id": frappe.db.get_single_value('Docusign Settings', 'integration_key'),
            "account_id": frappe.db.get_single_value('Docusign Settings', 'account_id'),
            "base_path": frappe.db.get_single_value('Docusign Settings', 'base_path'),
            "access_token": token,
            "server_url" : frappe.db.get_single_value('Docusign Settings', 'server_url')
        }
        bench_path = get_bench_path()
        site_path = get_site_path().replace(".", "/sites", 1)
        base_path = bench_path + site_path
        output = ""
        # return args
        if ds_doc.documents:
            for i, document in enumerate(ds_doc.documents):
                if document.document and i + 1 == len(ds_doc.documents):
                    signed_doc = document.document
                    path = base_path + signed_doc
                    with open(path, 'rb') as file:
                        output = file.read()
                else:
                    html = frappe.get_print(ds_doc.document_type, ds_doc.document, ds_doc.print_format)
                    output = get_pdf(html)
        else:
            html = frappe.get_print(ds_doc.document_type, ds_doc.document, ds_doc.print_format)
            output = get_pdf(html)
        base64_file_content = base64.b64encode(output).decode('ascii')

        if not base64_file_content:
            return "Failed to generate document content"

        res = send_document(args, base64_file_content)
        envelope_id = res["envelopeId"]
        # return res["uri"]
        ds_doc.append("documents", {
            'docusign_envelope_id': envelope_id,
        })
        ds_doc.save()
        frappe.db.set_value(ds_doc.document_type, ds_doc.document, 'dsc_status', ds_doc.workflow_state)
        pathValue = doctype.lower().replace(" ", "-")
        location_url = f"/app/{pathValue}"
        frappe.local.response['type'] = 'redirect'
        frappe.local.response['location'] = location_url
        frappe.db.commit()
    except Exception as e:
        frappe.logger("docusign").exception(e)
        return f"Error: {e}"


def send_document(args, document):
    base_url = "https://demo.docusign.net/restapi"
    api_version = "v2.1"
    url = f"{base_url}/{api_version}/accounts/{args['account_id']}/envelopes"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {args['access_token']}"
    }
    server_url = args["server_url"]
    emailSubject = f"Please sign this document sent {server_url}"
    # Create the request body
    payload = {
        "documents": [
            {
                "documentBase64": document,
                "documentId": 1,
                "fileExtension": "pdf",
                "name": "document ready for sign"
            }
        ],
        "emailSubject": emailSubject,
        "recipients": {
            "signers": [
                {
                    "email": args["signer_email"],
                    "name": args["signer_name"],
                    "recipientId": "2"
                }
            ]
        },
        "status": "sent"
    }

    # Convert payload to JSON
    payload_json = json.dumps(payload)

    # Send the request
    response = requests.post(url, headers=headers, data=payload_json)

    if response.status_code == 201:
        envelope_details = response.json()
        return envelope_details
    else:
        return f"Failed to send document. Status code: {response.status_code}, Error: {response.text}"


# This Method set as a webhook on Docusign Connect section in Configurations
# <Domain name>/api/method/docusign_integration.dsc_api.sign_document
@frappe.whitelist(allow_guest=True)
def sign_document(**kwargs):
	data = kwargs
	envelope_data = data["data"]

	# Get the bench paths
	bench_path = get_bench_path()
	site_path = get_site_path().replace(".", "/sites",1)
	base_path_ = bench_path + site_path
	file_name = frappe.generate_hash("",5) + ".pdf"
	cert_file_name = "cert_" + file_name

	# Extract PDF bytes and certificate from envelope data
	frappe.log_error(title="sign envelopid", message=str(envelope_data.get("envelopeId")))
	envelopeSummary = envelope_data.get("envelopeSummary")
	envelopeDocuments = envelopeSummary["envelopeDocuments"]
	pdfbytes = envelopeDocuments[0].get("PDFBytes")
	certificate = envelopeDocuments[1].get("PDFBytes")
	frappe.log_error("certificate sign", str(certificate))
	frappe.log_error(title="sign pdfbytes", message=str(pdfbytes))

	# Get Doctype where Document insert
	docusign_envelope_id = envelope_data.get("envelopeId")
	signChild = frappe.get_all("Digital Signature Signed Document", filters={"docusign_envelope_id" : docusign_envelope_id})
	childValue = frappe.db.get_value("Digital Signature Signed Document", {"name" : signChild[0].name}, ["parenttype", "parent"], as_dict=1)
	frappe.log_error("child value", str(childValue))

	# Encode pdfbtyes for upload File
	# Sign Document Encode
	encoded_string = base64.b64decode(pdfbytes.encode("utf-8"))
	with open(base_path_ + "/public/files/" + file_name, "wb") as f:
		f.write(encoded_string)
	res = save_file(fname=file_name, content=encoded_string, dt=childValue.parenttype,
				dn=childValue.parent, decode=False, is_private=0)
	frappe.log_error("RES", str(res))

	# Certificate encode
	certificate_string = base64.b64decode(certificate.encode("utf-8"))
	with open(base_path_ + "/public/files/" + cert_file_name, "wb") as f:
		f.write(certificate_string)
	res = save_file(fname=cert_file_name, content=certificate_string, dt=childValue.parenttype,
				dn=childValue.parent, decode=False, is_private=0)
	
	frappe.log_error("RES", str(res))

	# Insert Sign Document & certificate
	ds_doc = frappe.get_doc(childValue.parenttype ,childValue.parent)
	if ds_doc.documents:
		for document in ds_doc.documents:
			if not document.document and document.docusign_envelope_id:
				cert_file_path = "/files/" + cert_file_name
				private_file_path = "/files/" + file_name
				document.db_set('document',private_file_path)
				document.db_set('certificate',cert_file_path)
				document.db_set('user', frappe.session.user)
				document.db_set('timestamp',now_datetime())
				ds_doc.db_set('workflow_state',ds_doc.workflow_state.replace('Signing','Completed'))
				ds_doc.db_set('previous_state',ds_doc.workflow_state.replace('Signing','Completed'))
				frappe.db.set_value(ds_doc.document_type,ds_doc.document,'dsc_status',ds_doc.workflow_state)
		frappe.db.commit()


def dsc_change_status():
	data = frappe.get_all("Digital Signature","name") 
	for row in data:
		doc = frappe.get_doc("Digital Signature",row['name'])
		if "Signing" in doc.workflow_state and doc.workflow_state != doc.previous_state:
			doc.db_set("workflow_state",doc.previous_state)
			frappe.db.set_value(doc.document_type,doc.document,'dsc_status',doc.previous_state)
	frappe.db.commit()

	data = frappe.get_all("DSC Sales Invoice","name") 
	for row in data:
		doc = frappe.get_doc("DSC Sales Invoice",row['name'])
		if "Signing" in doc.workflow_state and doc.workflow_state != doc.previous_state:
			doc.db_set("workflow_state",doc.previous_state)
			frappe.db.set_value(doc.document_type,doc.document,'dsc_status',doc.previous_state)
	frappe.db.commit()

	data = frappe.get_all("DSC Purchase Order","name") 
	for row in data:
		doc = frappe.get_doc("DSC Purchase Order",row['name'])
		if "Signing" in doc.workflow_state and doc.workflow_state != doc.previous_state:
			doc.db_set("workflow_state",doc.previous_state)
			frappe.db.set_value(doc.document_type,doc.document,'dsc_status',doc.previous_state)
	frappe.db.commit()


def validate(self,event):
	if self.document_type and not frappe.db.exists("Custom Field",{'dt':self.document_type,'fieldname':'dsc_status'}):
		status = frappe.new_doc("Custom Field")
		status.dt = self.document_type
		status.label = 'DSC Status'
		status.fieldname = 'dsc_status'
		status.fieldtype = "Data"
		status.allow_on_submit = 1
		status.read_only = 1
		status.no_copy = 1 
		status.save()
	if self.workflow_state:
		self.previous_state = self.workflow_state


