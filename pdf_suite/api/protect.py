"""PDF encryption/decryption APIs."""
import frappe
import pikepdf
from pdf_suite.utils.file_utils import get_file_path, save_file_to_frappe, get_temp_path, cleanup_temp


@frappe.whitelist()
def encrypt_pdf(file_url, user_password="", owner_password="", output_filename=None):
    """Encrypt a PDF with password protection.

    Args:
        file_url: Source PDF file URL
        user_password: Password to open the PDF (empty = no open password)
        owner_password: Password to edit/print (required)
        output_filename: Optional output filename
    """
    try:
        if not owner_password:
            return {"success": False, "error": "Owner password is required"}

        path = get_file_path(file_url)
        output_filename = output_filename or "protected.pdf"

        temp_path = get_temp_path()
        try:
            with pikepdf.open(path) as pdf:
                permissions = pikepdf.Permissions(
                    extract=False,
                    modify_annotation=False,
                    modify_other=False,
                    modify_assembly=False,
                )

                encryption = pikepdf.Encryption(
                    user=user_password,
                    owner=owner_password,
                    R=6,  # AES-256
                    allow=permissions,
                )

                pdf.save(temp_path, encryption=encryption)

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
        frappe.log_error(f"encrypt_pdf error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def decrypt_pdf(file_url, password, output_filename=None):
    """Decrypt a password-protected PDF.

    Args:
        file_url: Source PDF file URL
        password: Password to unlock the PDF
        output_filename: Optional output filename
    """
    try:
        if not password:
            return {"success": False, "error": "Password is required"}

        path = get_file_path(file_url)
        output_filename = output_filename or "decrypted.pdf"

        temp_path = get_temp_path()
        try:
            with pikepdf.open(path, password=password) as pdf:
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

    except pikepdf.PasswordError:
        return {"success": False, "error": "Incorrect password"}
    except Exception as e:
        frappe.log_error(f"decrypt_pdf error: {e}")
        return {"success": False, "error": str(e)}
