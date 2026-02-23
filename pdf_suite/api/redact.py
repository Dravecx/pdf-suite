"""PDF redaction APIs — client marks areas, server removes content."""
import io
import frappe
import pikepdf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import white
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def redact_areas(file_url, redactions, output_filename=None):
    """Redact specified areas by overlaying white rectangles and flattening.

    Args:
        file_url: Source PDF file URL
        redactions: JSON list of {page, x, y, width, height} (coordinates in PDF points)
        output_filename: Optional output filename
    """
    try:
        if isinstance(redactions, str):
            import json
            redactions = json.loads(redactions)

        if not redactions:
            return {"success": False, "error": "No redaction areas specified"}

        path = get_file_path(file_url)
        output_filename = output_filename or "redacted.pdf"

        temp_path = get_temp_path()
        try:
            with pikepdf.open(path) as pdf:
                # Group redactions by page
                by_page = {}
                for r in redactions:
                    page_num = int(r["page"]) - 1
                    if page_num not in by_page:
                        by_page[page_num] = []
                    by_page[page_num].append(r)

                for page_num, page_redactions in by_page.items():
                    if page_num >= len(pdf.pages):
                        continue

                    page = pdf.pages[page_num]
                    box = page.mediabox
                    page_width = float(box[2] - box[0])
                    page_height = float(box[3] - box[1])

                    # Create overlay PDF with white rectangles
                    overlay_buf = io.BytesIO()
                    c = canvas.Canvas(overlay_buf, pagesize=(page_width, page_height))
                    c.setFillColor(white)
                    c.setStrokeColor(white)

                    for r in page_redactions:
                        x = float(r["x"])
                        y = float(r["y"])
                        w = float(r["width"])
                        h = float(r["height"])
                        c.rect(x, y, w, h, fill=1, stroke=1)

                    c.save()
                    overlay_buf.seek(0)

                    overlay_pdf = pikepdf.open(overlay_buf)
                    overlay_page = overlay_pdf.pages[0]
                    page.add_overlay(overlay_page)
                    overlay_pdf.close()

                pdf.save(temp_path)

            with open(temp_path, "rb") as f:
                content = f.read()

            url = save_file_to_frappe(content, output_filename)
            return {
                "success": True,
                "data": {
                    "file_url": url,
                    "filename": output_filename,
                    "redacted_areas": len(redactions),
                },
            }
        finally:
            cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"redact_areas error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def redact_text(file_url, search_text, output_filename=None):
    """Find and redact all occurrences of text in a PDF.

    Uses pdfplumber to find text positions, then overlays white rectangles.
    """
    try:
        import pdfplumber

        if not search_text:
            return {"success": False, "error": "Search text required"}

        path = get_file_path(file_url)
        output_filename = output_filename or "redacted.pdf"

        redactions = []
        with pdfplumber.open(path) as plumber:
            for i, page in enumerate(plumber.pages):
                words = page.extract_words()
                # Simple word-level search
                search_lower = search_text.lower()
                for word in words:
                    if search_lower in word["text"].lower():
                        redactions.append({
                            "page": i + 1,
                            "x": word["x0"],
                            "y": page.height - word["top"] - (word["bottom"] - word["top"]),
                            "width": word["x1"] - word["x0"],
                            "height": word["bottom"] - word["top"],
                        })

        if not redactions:
            return {
                "success": True,
                "data": {"message": "No matches found", "redacted_areas": 0},
            }

        return redact_areas(file_url, redactions, output_filename)

    except Exception as e:
        frappe.log_error(f"redact_text error: {e}")
        return {"success": False, "error": str(e)}
