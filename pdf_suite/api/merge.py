"""PDF merge APIs."""
import frappe
import pikepdf
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def merge_pdfs(file_urls, output_filename=None):
    """Merge multiple PDFs into one.

    Args:
        file_urls: JSON list of file URLs to merge (in order)
        output_filename: Optional output filename
    """
    try:
        if isinstance(file_urls, str):
            import json
            file_urls = json.loads(file_urls)

        if not file_urls or len(file_urls) < 2:
            return {"success": False, "error": "At least 2 files required for merge"}

        output_filename = output_filename or "merged.pdf"
        if not output_filename.endswith(".pdf"):
            output_filename += ".pdf"

        temp_path = get_temp_path()
        try:
            merged = pikepdf.Pdf.new()

            for url in file_urls:
                path = get_file_path(url)
                src = pikepdf.open(path)
                merged.pages.extend(src.pages)

            merged.save(temp_path)
            merged.close()

            with open(temp_path, "rb") as f:
                content = f.read()

            file_url = save_file_to_frappe(content, output_filename)

            return {
                "success": True,
                "data": {
                    "file_url": file_url,
                    "filename": output_filename,
                    "pages": len(merged.pages) if hasattr(merged, 'pages') else None,
                },
            }
        finally:
            cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"merge_pdfs error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def merge_pdfs_with_options(file_configs, output_filename=None):
    """Merge PDFs with per-file options (page ranges, rotation).

    Args:
        file_configs: JSON list of {file_url, pages?, rotate?}
        output_filename: Optional output filename
    """
    try:
        if isinstance(file_configs, str):
            import json
            file_configs = json.loads(file_configs)

        if not file_configs or len(file_configs) < 1:
            return {"success": False, "error": "At least 1 file config required"}

        output_filename = output_filename or "merged.pdf"
        if not output_filename.endswith(".pdf"):
            output_filename += ".pdf"

        temp_path = get_temp_path()
        try:
            merged = pikepdf.Pdf.new()

            for config in file_configs:
                url = config.get("file_url")
                page_range = config.get("pages")
                rotation = config.get("rotate", 0)

                path = get_file_path(url)
                src = pikepdf.open(path)

                if page_range:
                    from pdf_suite.api.extract import _parse_page_numbers
                    page_nums = _parse_page_numbers(page_range, len(src.pages))
                    pages = [src.pages[i] for i in page_nums if i < len(src.pages)]
                else:
                    pages = list(src.pages)

                for page in pages:
                    if rotation:
                        page.rotate(rotation, relative=True)
                    merged.pages.append(page)

            total_pages = len(merged.pages)
            merged.save(temp_path)
            merged.close()

            with open(temp_path, "rb") as f:
                content = f.read()

            file_url = save_file_to_frappe(content, output_filename)

            return {
                "success": True,
                "data": {
                    "file_url": file_url,
                    "filename": output_filename,
                    "pages": total_pages,
                },
            }
        finally:
            cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"merge_pdfs_with_options error: {e}")
        return {"success": False, "error": str(e)}
