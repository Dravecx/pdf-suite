"""Shared PDF utilities for PDF Suite."""
import os
import pikepdf
from pdf_suite.utils.file_utils import get_file_path


def get_page_count(file_url):
    """Get page count of a PDF."""
    path = get_file_path(file_url)
    with pikepdf.open(path) as pdf:
        return len(pdf.pages)


def get_pdf_metadata(file_url):
    """Get PDF metadata (title, author, pages, file size, etc.)."""
    path = get_file_path(file_url)
    file_size = os.path.getsize(path)

    with pikepdf.open(path) as pdf:
        info = pdf.docinfo if pdf.docinfo else {}
        metadata = {
            "pages": len(pdf.pages),
            "file_size": file_size,
            "file_size_human": _human_size(file_size),
            "title": str(info.get("/Title", "")),
            "author": str(info.get("/Author", "")),
            "subject": str(info.get("/Subject", "")),
            "creator": str(info.get("/Creator", "")),
            "producer": str(info.get("/Producer", "")),
            "encrypted": pdf.is_encrypted,
        }

        # Get page dimensions from first page
        if len(pdf.pages) > 0:
            page = pdf.pages[0]
            box = page.mediabox
            metadata["width"] = float(box[2] - box[0])
            metadata["height"] = float(box[3] - box[1])

    return metadata


def _human_size(size_bytes):
    """Convert bytes to human readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
