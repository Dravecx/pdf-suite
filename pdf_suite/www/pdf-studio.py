import frappe

no_cache = 1

def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	context.csrf_token = csrf_token
	if frappe.session.user == "Guest":
		frappe.throw("Please login to access PDF Studio", frappe.AuthenticationError)
