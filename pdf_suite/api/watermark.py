"""PDF watermark APIs."""
import io
import frappe
import pikepdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def add_text_watermark(
    file_url,
    text="CONFIDENTIAL",
    font_size=60,
    opacity=0.15,
    rotation=45,
    color="#888888",
    output_filename=None,
):
    """Add a text watermark to all pages of a PDF."""
    try:
        path = get_file_path(file_url)
        output_filename = output_filename or "watermarked.pdf"

        # Create watermark PDF using reportlab
        watermark_buf = io.BytesIO()
        c = canvas.Canvas(watermark_buf, pagesize=A4)
        width, height = A4

        # Parse color
        r, g, b = _hex_to_rgb(color)
        c.setFillColor(Color(r, g, b, alpha=float(opacity)))
        c.setFont("Helvetica-Bold", int(font_size))

        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(int(rotation))
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.save()

        watermark_buf.seek(0)

        temp_path = get_temp_path()
        try:
            watermark_pdf = pikepdf.open(watermark_buf)
            watermark_page = watermark_pdf.pages[0]

            with pikepdf.open(path) as pdf:
                for page in pdf.pages:
                    page.add_underlay(watermark_page)

                pdf.save(temp_path)

            watermark_pdf.close()

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
        frappe.log_error(f"add_text_watermark error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def add_image_watermark(file_url, image_url, opacity=0.2, position="center", output_filename=None):
    """Add an image watermark to all pages of a PDF."""
    try:
        path = get_file_path(file_url)
        image_path = get_file_path(image_url)
        output_filename = output_filename or "watermarked.pdf"

        from PIL import Image as PILImage

        img = PILImage.open(image_path)
        img_width, img_height = img.size

        # Create watermark PDF with the image
        watermark_buf = io.BytesIO()
        c = canvas.Canvas(watermark_buf, pagesize=A4)
        page_width, page_height = A4

        c.setFillAlpha(float(opacity))

        # Position image
        if position == "center":
            x = (page_width - img_width / 2) / 2
            y = (page_height - img_height / 2) / 2
        elif position == "top-right":
            x = page_width - img_width / 2 - 40
            y = page_height - img_height / 2 - 40
        elif position == "bottom-left":
            x = 40
            y = 40
        else:
            x = (page_width - img_width / 2) / 2
            y = (page_height - img_height / 2) / 2

        c.drawImage(image_path, x, y, width=img_width / 2, height=img_height / 2, mask="auto")
        c.save()
        watermark_buf.seek(0)

        temp_path = get_temp_path()
        try:
            watermark_pdf = pikepdf.open(watermark_buf)
            watermark_page = watermark_pdf.pages[0]

            with pikepdf.open(path) as pdf:
                for page in pdf.pages:
                    page.add_underlay(watermark_page)
                pdf.save(temp_path)

            watermark_pdf.close()

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
        frappe.log_error(f"add_image_watermark error: {e}")
        return {"success": False, "error": str(e)}


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))
