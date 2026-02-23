"""Frappe File doctype helpers for PDF Suite."""
import os
import tempfile
import frappe


def get_file_path(file_url):
    """Get absolute file path from Frappe file URL."""
    if not file_url:
        frappe.throw("No file URL provided")

    if file_url.startswith("/files/"):
        file_path = frappe.get_site_path("public", file_url.lstrip("/"))
    elif file_url.startswith("/private/files/"):
        file_path = frappe.get_site_path(file_url.lstrip("/"))
    else:
        file_path = frappe.get_site_path("public", "files", file_url)

    if not os.path.exists(file_path):
        frappe.throw(f"File not found: {file_url}")

    return file_path


def save_file_to_frappe(content_bytes, filename, folder="Home", is_private=1):
    """Save bytes as a Frappe File document and return its URL."""
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "content": content_bytes,
        "folder": folder,
        "is_private": is_private,
    })
    file_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return file_doc.file_url


def get_temp_path(suffix=".pdf"):
    """Get a temporary file path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return path


def cleanup_temp(path):
    """Remove a temporary file if it exists."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
