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
def generate_html_pdf(template_name, variable_data, output_filename=None):
    """Generate a PDF from a TipTap HTML template with variable substitution using WeasyPrint.

    Args:
        template_name: Name of the PDF Template document
        variable_data: JSON string of {variable_name: value} pairs
        output_filename: Optional filename (without .pdf)
    """
    import re
    try:
        from weasyprint import HTML
    except ImportError:
        return {"success": False, "error": "WeasyPrint is not installed on this server"}

    try:
        doc = frappe.get_doc("PDF Template", template_name)
        schema = json.loads(doc.schema or "{}")

        if schema.get("type") != "tiptap":
            return {"success": False, "error": "Template is not a TipTap template"}

        html_content = schema.get("html", "")
        if isinstance(variable_data, str):
            variable_data = json.loads(variable_data)

        # Replace <span data-variable="name" ...>{{name}}</span> with actual values
        def replace_chip(match):
            var_name = match.group(1)
            return str(variable_data.get(var_name, ""))

        html_content = re.sub(
            r'<span[^>]+data-variable="([^"]+)"[^>]*>.*?</span>',
            replace_chip,
            html_content,
            flags=re.DOTALL,
        )

        # Background image inline style
        bg_style = ""
        if schema.get("background_image"):
            bg_url = schema["background_image"]
            if not bg_url.startswith("data:"):
                bg_url = frappe.utils.get_url() + bg_url
            bg_style = 'background-image: url("' + bg_url + '"); background-size: cover; background-position: center;'

        full_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page { size: A4; margin: 0; }
body { margin: 0; font-family: Arial, sans-serif; font-size: 12pt; color: #111827; }
.page { width: 210mm; min-height: 297mm; padding: 25mm; box-sizing: border-box; """ + bg_style + """ }
.variable-chip { display: inline; }
h1 { font-size: 24pt; font-weight: 700; margin: 12pt 0 6pt; }
h2 { font-size: 18pt; font-weight: 700; margin: 10pt 0 5pt; }
h3 { font-size: 14pt; font-weight: 600; margin: 8pt 0 4pt; }
p { margin: 0 0 6pt; line-height: 1.6; }
ul { list-style: disc; padding-left: 18pt; margin: 6pt 0; }
ol { list-style: decimal; padding-left: 18pt; margin: 6pt 0; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; }
th, td { border: 1px solid #d1d5db; padding: 5pt 8pt; text-align: left; }
th { background: #f9fafb; font-weight: 600; }
strong { font-weight: 700; }
em { font-style: italic; }
u { text-decoration: underline; }
s { text-decoration: line-through; }
</style>
</head>
<body>
<div class="page">""" + html_content + """</div>
</body>
</html>"""

        pdf_bytes = HTML(string=full_html).write_pdf()

        ts = frappe.utils.now_datetime().strftime("%Y%m%d_%H%M%S")
        base_name = (output_filename or template_name).replace(" ", "_").lower()
        filename = base_name + "_" + ts + ".pdf"

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": pdf_bytes,
            "is_private": 0,
        })
        file_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True, "data": {"file_url": file_doc.file_url, "filename": filename}}

    except Exception as e:
        frappe.log_error("generate_html_pdf error: " + str(e))
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
