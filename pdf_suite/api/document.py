"""PDF Document editing session APIs."""
import json
import frappe


@frappe.whitelist()
def save_edit_session(file_url, annotations, page_modifications=None, session_name=None):
    """Save an editing session (annotations, modifications) to PDF Document doctype.

    Args:
        file_url: Original PDF file URL
        annotations: JSON string of Fabric.js annotations per page
        page_modifications: JSON string of page operations (reorder, delete, rotate)
        session_name: Existing session name to update (or creates new)
    """
    try:
        if isinstance(annotations, str):
            annotations = json.loads(annotations)
        if isinstance(page_modifications, str) and page_modifications:
            page_modifications = json.loads(page_modifications)

        if session_name:
            # Update existing session
            doc = frappe.get_doc("PDF Document", session_name)
            doc.annotations = json.dumps(annotations)
            if page_modifications:
                doc.page_modifications = json.dumps(page_modifications)
            doc.save(ignore_permissions=True)
        else:
            # Create new session
            doc = frappe.get_doc({
                "doctype": "PDF Document",
                "source_file": file_url,
                "annotations": json.dumps(annotations),
                "page_modifications": json.dumps(page_modifications or []),
                "owner": frappe.session.user,
            })
            doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "success": True,
            "data": {
                "session_name": doc.name,
                "message": "Session saved",
            },
        }
    except Exception as e:
        frappe.log_error(f"save_edit_session error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def load_edit_session(session_name):
    """Load a previously saved editing session."""
    try:
        doc = frappe.get_doc("PDF Document", session_name)

        return {
            "success": True,
            "data": {
                "session_name": doc.name,
                "source_file": doc.source_file,
                "annotations": json.loads(doc.annotations or "[]"),
                "page_modifications": json.loads(doc.page_modifications or "[]"),
                "modified": str(doc.modified),
            },
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Session not found"}
    except Exception as e:
        frappe.log_error(f"load_edit_session error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def list_edit_sessions():
    """List all editing sessions for the current user."""
    try:
        sessions = frappe.get_all(
            "PDF Document",
            filters={"owner": frappe.session.user},
            fields=["name", "source_file", "modified", "creation"],
            order_by="modified desc",
            limit_page_length=50,
        )

        return {
            "success": True,
            "data": {"sessions": sessions, "count": len(sessions)},
        }
    except Exception as e:
        frappe.log_error(f"list_edit_sessions error: {e}")
        return {"success": False, "error": str(e)}
