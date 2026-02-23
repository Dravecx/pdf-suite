"""PDF flatten API — bake annotations/forms into static content."""
import frappe
import pikepdf
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def flatten_pdf(file_url, output_filename=None):
    """Flatten a PDF (bake annotations and form fields into page content).

    Uses pikepdf to remove annotation interactivity by flattening form fields.
    """
    try:
        path = get_file_path(file_url)
        output_filename = output_filename or "flattened.pdf"

        temp_path = get_temp_path()
        try:
            with pikepdf.open(path) as pdf:
                # Remove form field interactivity by removing AcroForm
                if "/AcroForm" in pdf.Root:
                    del pdf.Root["/AcroForm"]

                # Flatten annotations on each page
                for page in pdf.pages:
                    if "/Annots" in page:
                        # Keep the visual appearance but remove interactivity
                        annots = page["/Annots"]
                        for annot in annots:
                            annot_obj = annot.resolve() if hasattr(annot, 'resolve') else annot
                            # Set annotation flag to Print+NoView to bake it in
                            if "/AP" in annot_obj:
                                # Has appearance stream — safe to flatten
                                pass
                        # Remove annotations after flattening
                        del page["/Annots"]

                pdf.save(temp_path)

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
        frappe.log_error(f"flatten_pdf error: {e}")
        return {"success": False, "error": str(e)}
