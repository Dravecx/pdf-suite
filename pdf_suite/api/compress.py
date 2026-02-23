"""PDF compression API."""
import os
import frappe
import pikepdf
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def compress_pdf(file_url, quality="medium", output_filename=None):
    """Compress a PDF to reduce file size.

    Args:
        file_url: Source PDF file URL
        quality: "low" (max compression), "medium", "high" (min compression)
        output_filename: Optional output filename
    """
    try:
        path = get_file_path(file_url)
        original_size = os.path.getsize(path)
        output_filename = output_filename or "compressed.pdf"

        # Map quality to pikepdf stream settings
        stream_settings = {
            "low": {
                "compress_streams": True,
                "stream_decode_level": pikepdf.StreamDecodeLevel.all,
                "object_stream_mode": pikepdf.ObjectStreamMode.generate,
                "recompress_flate": True,
            },
            "medium": {
                "compress_streams": True,
                "stream_decode_level": pikepdf.StreamDecodeLevel.specialized,
                "object_stream_mode": pikepdf.ObjectStreamMode.generate,
            },
            "high": {
                "compress_streams": True,
                "object_stream_mode": pikepdf.ObjectStreamMode.generate,
            },
        }

        settings = stream_settings.get(quality, stream_settings["medium"])

        temp_path = get_temp_path()
        try:
            with pikepdf.open(path) as pdf:
                # Remove metadata that's not needed
                if quality == "low":
                    pdf.remove_unreferenced_resources()

                pdf.save(temp_path, **settings)

            compressed_size = os.path.getsize(temp_path)

            with open(temp_path, "rb") as f:
                content = f.read()

            url = save_file_to_frappe(content, output_filename)

            reduction = ((original_size - compressed_size) / original_size) * 100

            return {
                "success": True,
                "data": {
                    "file_url": url,
                    "filename": output_filename,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "reduction_percent": round(reduction, 1),
                    "original_size_human": _human_size(original_size),
                    "compressed_size_human": _human_size(compressed_size),
                },
            }
        finally:
            cleanup_temp(temp_path)

    except Exception as e:
        frappe.log_error(f"compress_pdf error: {e}")
        return {"success": False, "error": str(e)}


def _human_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
