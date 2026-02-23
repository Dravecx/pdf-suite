"""Batch PDF operation APIs using frappe.enqueue()."""
import json
import frappe


@frappe.whitelist()
def start_batch(operation, file_urls, options=None):
    """Start a batch PDF operation as a background job.

    Args:
        operation: Operation type (merge, split, compress, watermark, ocr)
        file_urls: JSON list of file URLs to process
        options: JSON dict of operation-specific options
    """
    try:
        if isinstance(file_urls, str):
            file_urls = json.loads(file_urls)
        if isinstance(options, str) and options:
            options = json.loads(options)

        valid_operations = ["merge", "split", "compress", "watermark", "ocr", "convert"]
        if operation not in valid_operations:
            return {"success": False, "error": f"Invalid operation: {operation}"}

        # Create batch job record
        batch_doc = frappe.get_doc({
            "doctype": "PDF Batch Job",
            "operation": operation,
            "status": "Queued",
            "total_files": len(file_urls),
            "processed_files": 0,
            "file_urls": json.dumps(file_urls),
            "options": json.dumps(options or {}),
            "owner": frappe.session.user,
        })
        batch_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Enqueue the job
        frappe.enqueue(
            "pdf_suite.api.batch.process_batch",
            batch_name=batch_doc.name,
            queue="long",
            timeout=600,
        )

        return {
            "success": True,
            "data": {
                "batch_name": batch_doc.name,
                "status": "Queued",
                "message": "Batch job started",
            },
        }
    except Exception as e:
        frappe.log_error(f"start_batch error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_batch_status(batch_name):
    """Get the status of a batch job."""
    try:
        doc = frappe.get_doc("PDF Batch Job", batch_name)
        return {
            "success": True,
            "data": {
                "batch_name": doc.name,
                "operation": doc.operation,
                "status": doc.status,
                "total_files": doc.total_files,
                "processed_files": doc.processed_files,
                "results": json.loads(doc.results or "[]"),
                "error": doc.error_message or "",
            },
        }
    except frappe.DoesNotExistError:
        return {"success": False, "error": "Batch job not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def process_batch(batch_name):
    """Process a batch job (called via frappe.enqueue)."""
    try:
        doc = frappe.get_doc("PDF Batch Job", batch_name)
        doc.status = "Processing"
        doc.save(ignore_permissions=True)
        frappe.db.commit()

        file_urls = json.loads(doc.file_urls)
        options = json.loads(doc.options or "{}")
        operation = doc.operation

        results = []

        # Map operations to their handlers
        handlers = {
            "compress": _batch_compress,
            "watermark": _batch_watermark,
            "ocr": _batch_ocr,
        }

        if operation == "merge":
            # Merge is a single operation on all files
            from pdf_suite.api.merge import merge_pdfs
            result = merge_pdfs(file_urls, options.get("output_filename"))
            results.append(result)
            doc.processed_files = len(file_urls)
        elif operation in handlers:
            handler = handlers[operation]
            for i, url in enumerate(file_urls):
                result = handler(url, options)
                results.append(result)
                doc.processed_files = i + 1
                doc.save(ignore_permissions=True)
                frappe.db.commit()
        else:
            doc.status = "Failed"
            doc.error_message = f"Unknown operation: {operation}"
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return

        doc.status = "Completed"
        doc.results = json.dumps(results)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"process_batch error: {e}")
        doc = frappe.get_doc("PDF Batch Job", batch_name)
        doc.status = "Failed"
        doc.error_message = str(e)
        doc.save(ignore_permissions=True)
        frappe.db.commit()


def _batch_compress(file_url, options):
    from pdf_suite.api.compress import compress_pdf
    return compress_pdf(file_url, quality=options.get("quality", "medium"))


def _batch_watermark(file_url, options):
    from pdf_suite.api.watermark import add_text_watermark
    return add_text_watermark(
        file_url,
        text=options.get("text", "CONFIDENTIAL"),
        opacity=options.get("opacity", 0.15),
    )


def _batch_ocr(file_url, options):
    from pdf_suite.api.ocr import ocr_pdf
    return ocr_pdf(file_url, language=options.get("language", "eng"))
