"""PDF split APIs."""
import frappe
import pikepdf
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def split_pdf(file_url, page_ranges):
    """Split a PDF into multiple files by page ranges.

    Args:
        file_url: Source PDF file URL
        page_ranges: JSON list of range strings, e.g. ["1-3", "4-6", "7"]
    """
    try:
        if isinstance(page_ranges, str):
            import json
            page_ranges = json.loads(page_ranges)

        if not page_ranges:
            return {"success": False, "error": "Page ranges required"}

        path = get_file_path(file_url)
        results = []

        with pikepdf.open(path) as src:
            total_pages = len(src.pages)

            for i, range_str in enumerate(page_ranges):
                pages = _parse_range(range_str, total_pages)
                if not pages:
                    continue

                temp_path = get_temp_path()
                try:
                    dst = pikepdf.Pdf.new()
                    for page_num in pages:
                        if 0 <= page_num < total_pages:
                            dst.pages.append(src.pages[page_num])

                    page_count = len(dst.pages)
                    dst.save(temp_path)
                    dst.close()

                    with open(temp_path, "rb") as f:
                        content = f.read()

                    filename = f"split_part_{i + 1}.pdf"
                    url = save_file_to_frappe(content, filename)
                    results.append({
                        "file_url": url,
                        "filename": filename,
                        "pages": page_count,
                        "range": range_str,
                    })
                finally:
                    cleanup_temp(temp_path)

        return {
            "success": True,
            "data": {"files": results, "count": len(results)},
        }
    except Exception as e:
        frappe.log_error(f"split_pdf error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def split_pdf_every_n(file_url, n=1):
    """Split a PDF into chunks of N pages each."""
    try:
        n = int(n)
        if n < 1:
            return {"success": False, "error": "N must be at least 1"}

        path = get_file_path(file_url)
        results = []

        with pikepdf.open(path) as src:
            total = len(src.pages)

            for start in range(0, total, n):
                end = min(start + n, total)
                temp_path = get_temp_path()
                try:
                    dst = pikepdf.Pdf.new()
                    for page_num in range(start, end):
                        dst.pages.append(src.pages[page_num])

                    page_count = len(dst.pages)
                    dst.save(temp_path)
                    dst.close()

                    with open(temp_path, "rb") as f:
                        content = f.read()

                    part = (start // n) + 1
                    filename = f"split_pages_{start + 1}-{end}.pdf"
                    url = save_file_to_frappe(content, filename)
                    results.append({
                        "file_url": url,
                        "filename": filename,
                        "pages": page_count,
                        "range": f"{start + 1}-{end}",
                    })
                finally:
                    cleanup_temp(temp_path)

        return {
            "success": True,
            "data": {"files": results, "count": len(results)},
        }
    except Exception as e:
        frappe.log_error(f"split_pdf_every_n error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def extract_pages(file_url, page_numbers, output_filename=None):
    """Extract specific pages from a PDF into a new file."""
    try:
        from pdf_suite.api.extract import _parse_page_numbers

        path = get_file_path(file_url)
        output_filename = output_filename or "extracted.pdf"

        with pikepdf.open(path) as src:
            pages = _parse_page_numbers(page_numbers, len(src.pages))

            temp_path = get_temp_path()
            try:
                dst = pikepdf.Pdf.new()
                for page_num in pages:
                    if 0 <= page_num < len(src.pages):
                        dst.pages.append(src.pages[page_num])

                page_count = len(dst.pages)
                dst.save(temp_path)
                dst.close()

                with open(temp_path, "rb") as f:
                    content = f.read()

                url = save_file_to_frappe(content, output_filename)
                return {
                    "success": True,
                    "data": {
                        "file_url": url,
                        "filename": output_filename,
                        "pages": page_count,
                    },
                }
            finally:
                cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"extract_pages error: {e}")
        return {"success": False, "error": str(e)}


def _parse_range(range_str, total_pages):
    """Parse a range string like '1-3' or '5' into 0-indexed page numbers."""
    pages = []
    range_str = str(range_str).strip()
    if "-" in range_str:
        start, end = range_str.split("-", 1)
        start = max(1, int(start))
        end = min(total_pages, int(end))
        pages = list(range(start - 1, end))
    else:
        page = int(range_str)
        if 1 <= page <= total_pages:
            pages = [page - 1]
    return pages
