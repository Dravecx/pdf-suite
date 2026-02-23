"""Context for /pdf-studio page — auth check and asset injection."""
import frappe


def get_context(context):
    # Require login
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access PDF Studio", frappe.AuthenticationError)

    context.no_cache = 1
    context.no_breadcrumbs = True

    # Inject built Vue assets
    context.web_include_css = ["/assets/pdf_suite/dist/pdf-studio.css"]
    context.web_include_js = ["/assets/pdf_suite/dist/pdf-studio.js"]

    return context
