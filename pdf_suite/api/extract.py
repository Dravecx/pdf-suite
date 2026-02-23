"""PDF extraction APIs — text, tables, images, metadata."""
import frappe
from pdf_suite.utils.file_utils import get_file_path
from pdf_suite.utils.pdf_utils import get_pdf_metadata


@frappe.whitelist()
def get_pdf_info(file_url):
    """Get PDF metadata (pages, size, title, author, dimensions)."""
    try:
        metadata = get_pdf_metadata(file_url)
        return {"success": True, "data": metadata}
    except Exception as e:
        frappe.log_error(f"get_pdf_info error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def extract_text(file_url, page_numbers=None):
    """Extract text from PDF pages using pdfplumber."""
    try:
        import pdfplumber

        path = get_file_path(file_url)
        result = []

        with pdfplumber.open(path) as pdf:
            pages = _parse_page_numbers(page_numbers, len(pdf.pages))

            for page_num in pages:
                if 0 <= page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""
                    result.append({
                        "page": page_num + 1,
                        "text": text,
                    })

        return {"success": True, "data": {"pages": result}}
    except Exception as e:
        frappe.log_error(f"extract_text error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def extract_tables(file_url, page_numbers=None):
    """Extract tables from PDF pages using pdfplumber."""
    try:
        import pdfplumber

        path = get_file_path(file_url)
        result = []

        with pdfplumber.open(path) as pdf:
            pages = _parse_page_numbers(page_numbers, len(pdf.pages))

            for page_num in pages:
                if 0 <= page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    tables = page.extract_tables() or []
                    for i, table in enumerate(tables):
                        result.append({
                            "page": page_num + 1,
                            "table_index": i,
                            "rows": table,
                        })

        return {"success": True, "data": {"tables": result, "count": len(result)}}
    except Exception as e:
        frappe.log_error(f"extract_tables error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def extract_images(file_url, page_numbers=None):
    """Extract image metadata from PDF pages."""
    try:
        import pikepdf

        path = get_file_path(file_url)
        result = []

        with pikepdf.open(path) as pdf:
            pages = _parse_page_numbers(page_numbers, len(pdf.pages))

            for page_num in pages:
                if 0 <= page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    resources = page.get("/Resources", {})
                    xobjects = resources.get("/XObject", {})

                    for name, obj in xobjects.items():
                        if obj.get("/Subtype") == "/Image":
                            result.append({
                                "page": page_num + 1,
                                "name": str(name),
                                "width": int(obj.get("/Width", 0)),
                                "height": int(obj.get("/Height", 0)),
                                "color_space": str(obj.get("/ColorSpace", "")),
                            })

        return {"success": True, "data": {"images": result, "count": len(result)}}
    except Exception as e:
        frappe.log_error(f"extract_images error: {e}")
        return {"success": False, "error": str(e)}


def _parse_page_numbers(page_numbers, total_pages):
    """Parse page numbers string into list of 0-indexed page numbers."""
    if not page_numbers:
        return list(range(total_pages))

    if isinstance(page_numbers, list):
        return [int(p) - 1 for p in page_numbers]

    pages = []
    for part in str(page_numbers).split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.extend(range(int(start) - 1, int(end)))
        else:
            pages.append(int(part) - 1)

    return sorted(set(pages))
