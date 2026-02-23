"""PDF OCR APIs using pytesseract."""
import os
import io
import frappe
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def ocr_pdf(file_url, language="eng", output_filename=None):
    """OCR a scanned PDF and create a searchable PDF.

    Args:
        file_url: Source PDF file URL
        language: Tesseract language code (eng, ara, eng+ara)
        output_filename: Optional output filename
    """
    try:
        import pytesseract
        from PIL import Image
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        import pikepdf
        import subprocess

        path = get_file_path(file_url)
        output_filename = output_filename or "ocr_output.pdf"

        # Convert PDF pages to images using poppler (pdftoppm)
        temp_dir = get_temp_path(suffix="")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Use pdftoppm to convert PDF to images
            subprocess.run(
                ["pdftoppm", "-png", "-r", "300", path, os.path.join(temp_dir, "page")],
                check=True,
                capture_output=True,
            )

            # Find all generated page images
            images = sorted(
                [f for f in os.listdir(temp_dir) if f.startswith("page") and f.endswith(".png")]
            )

            if not images:
                return {"success": False, "error": "Failed to convert PDF to images"}

            # OCR each page and create searchable PDF
            all_text = []
            pdf_pages = []

            for img_file in images:
                img_path = os.path.join(temp_dir, img_file)
                img = Image.open(img_path)

                # Extract text
                text = pytesseract.image_to_string(img, lang=language)
                all_text.append(text)

                # Create searchable PDF page
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=language, extension="pdf")
                pdf_pages.append(pdf_bytes)

            # Merge all OCR'd pages
            merged = pikepdf.Pdf.new()
            for page_bytes in pdf_pages:
                page_pdf = pikepdf.open(io.BytesIO(page_bytes))
                merged.pages.extend(page_pdf.pages)

            temp_output = get_temp_path()
            merged.save(temp_output)
            merged.close()

            with open(temp_output, "rb") as f:
                content = f.read()

            url = save_file_to_frappe(content, output_filename)
            cleanup_temp(temp_output)

            return {
                "success": True,
                "data": {
                    "file_url": url,
                    "filename": output_filename,
                    "pages_processed": len(images),
                    "text_preview": all_text[0][:500] if all_text else "",
                },
            }
        finally:
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        frappe.log_error(f"ocr_pdf error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def ocr_image_to_text(file_url, language="eng"):
    """OCR an image file and return extracted text.

    Args:
        file_url: Image file URL (PNG, JPG, TIFF)
        language: Tesseract language code
    """
    try:
        import pytesseract
        from PIL import Image

        path = get_file_path(file_url)
        img = Image.open(path)
        text = pytesseract.image_to_string(img, lang=language)

        return {
            "success": True,
            "data": {"text": text, "language": language},
        }
    except Exception as e:
        frappe.log_error(f"ocr_image_to_text error: {e}")
        return {"success": False, "error": str(e)}
