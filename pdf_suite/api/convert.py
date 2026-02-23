"""PDF conversion APIs — PDF to DOCX, DOCX to PDF, HTML to PDF."""
import os
import frappe
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def pdf_to_docx(file_url, output_filename=None):
    """Convert PDF to DOCX using pdf2docx."""
    try:
        from pdf2docx import Converter

        path = get_file_path(file_url)
        output_filename = output_filename or "converted.docx"
        if not output_filename.endswith(".docx"):
            output_filename += ".docx"

        temp_path = get_temp_path(suffix=".docx")
        try:
            cv = Converter(path)
            cv.convert(temp_path)
            cv.close()

            with open(temp_path, "rb") as f:
                content = f.read()

            url = save_file_to_frappe(content, output_filename)
            return {
                "success": True,
                "data": {"file_url": url, "filename": output_filename},
            }
        finally:
            cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"pdf_to_docx error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def docx_to_pdf(file_url, output_filename=None):
    """Convert DOCX to PDF using LibreOffice."""
    try:
        import subprocess

        path = get_file_path(file_url)
        output_filename = output_filename or "converted.pdf"

        temp_dir = get_temp_path(suffix="")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            result = subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    temp_dir,
                    path,
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )

            # Find the output PDF
            pdf_files = [f for f in os.listdir(temp_dir) if f.endswith(".pdf")]
            if not pdf_files:
                return {"success": False, "error": "Conversion failed — no output PDF generated"}

            output_path = os.path.join(temp_dir, pdf_files[0])
            with open(output_path, "rb") as f:
                content = f.read()

            url = save_file_to_frappe(content, output_filename)
            return {
                "success": True,
                "data": {"file_url": url, "filename": output_filename},
            }
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Conversion timed out (120s limit)"}
    except Exception as e:
        frappe.log_error(f"docx_to_pdf error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def html_to_pdf(html_content, output_filename=None):
    """Convert HTML string to PDF using reportlab/fpdf2."""
    try:
        from fpdf import FPDF

        output_filename = output_filename or "generated.pdf"

        # Simple HTML to PDF using fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)

        # fpdf2 supports basic HTML
        pdf.write_html(html_content)

        temp_path = get_temp_path()
        try:
            pdf.output(temp_path)

            with open(temp_path, "rb") as f:
                content = f.read()

            url = save_file_to_frappe(content, output_filename)
            return {
                "success": True,
                "data": {"file_url": url, "filename": output_filename},
            }
        finally:
            cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"html_to_pdf error: {e}")
        return {"success": False, "error": str(e)}
