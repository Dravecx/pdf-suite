# PDF Suite

Full-featured PDF editing suite for Frappe. Works as a standalone app at `/pdf-studio` and can be embedded into other Frappe apps via iframe.

## Features

- **Edit PDFs** — Annotate, sign, highlight, draw, add text/images
- **Merge** — Combine multiple PDFs into one
- **Split** — Split PDFs by page ranges or every N pages
- **Compress** — Reduce file size with configurable quality
- **Convert** — PDF to DOCX, DOCX to PDF
- **OCR** — Make scanned PDFs searchable (English, Arabic)
- **Watermark** — Add text or image watermarks
- **Protect** — Encrypt/decrypt with AES-256
- **Templates** — Design and generate PDFs from templates
- **Batch** — Process multiple files at once

## Installation

```bash
bench get-app https://github.com/Dravecx/pdf-suite
bench --site your-site install-app pdf_suite
```

### System Dependencies

These are installed automatically on Frappe Cloud:

- tesseract-ocr (OCR)
- libreoffice-writer (DOCX conversion)
- poppler-utils (PDF to image)
- ghostscript (PDF processing)

## Development

```bash
cd frontend
npm install
npm run dev    # Dev server at http://localhost:3001
npm run build  # Build to pdf_suite/public/dist/
```

## Architecture

- **Backend**: Python APIs using pikepdf, pdfplumber, reportlab, pytesseract
- **Frontend**: Vue 3 + PDF.js + Fabric.js + pdf-lib
- **No PyMuPDF** (AGPL) — all operations use permissive-licensed libraries

## License

MIT
