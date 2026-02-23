"""PDF Template CRUD + generation APIs."""
import json
import frappe


@frappe.whitelist()
def save_template(name, schema, base_pdf=None, description=None):
    """Save a pdfme template schema.

    Args:
        name: Template name
        schema: JSON string of pdfme template schema
        base_pdf: Optional base PDF file URL
        description: Optional description
    """
    try:
        if isinstance(schema, str):
            schema = json.loads(schema)

        # Check if template exists
        existing = frappe.db.exists("PDF Template", {"template_name": name})

        if existing:
            doc = frappe.get_doc("PDF Template", existing)
            doc.schema = json.dumps(schema)
            if base_pdf:
                doc.base_pdf = base_pdf
            if description:
                doc.description = description
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "PDF Template",
                "template_name": name,
                "schema": json.dumps(schema),
                "base_pdf": base_pdf or "",
                "description": description or "",
            })
            doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "success": True,
            "data": {"template_name": doc.name, "message": "Template saved"},
        }
    except Exception as e:
        frappe.log_error(f"save_template error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_template(template_name):
    """Get a template by name."""
    try:
        doc = frappe.get_doc("PDF Template", template_name)
        return {
            "success": True,
            "data": {
                "name": doc.name,
                "template_name": doc.template_name,
                "schema": json.loads(doc.schema or "{}"),
                "base_pdf": doc.base_pdf,
                "description": doc.description,
            },
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Template not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def list_templates():
    """List all PDF templates."""
    try:
        templates = frappe.get_all(
            "PDF Template",
            fields=["name", "template_name", "description", "modified", "creation"],
            order_by="modified desc",
        )
        return {"success": True, "data": {"templates": templates}}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def delete_template(template_name):
    """Delete a PDF template."""
    try:
        frappe.delete_doc("PDF Template", template_name)
        frappe.db.commit()
        return {"success": True, "data": {"message": "Template deleted"}}
    except Exception as e:
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def generate_from_template(template_name, input_data, output_filename=None):
    """Generate a PDF from a pdfme template with input data.

    Note: Full pdfme generation is client-side. This endpoint provides
    server-side template data resolution for batch generation.
    """
    try:
        doc = frappe.get_doc("PDF Template", template_name)
        schema = json.loads(doc.schema or "{}")

        if isinstance(input_data, str):
            input_data = json.loads(input_data)

        return {
            "success": True,
            "data": {
                "schema": schema,
                "input_data": input_data,
                "base_pdf": doc.base_pdf,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
