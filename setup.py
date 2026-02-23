from setuptools import setup, find_packages

setup(
    name="pdf_suite",
    version="0.1.0",
    description="Full-featured PDF editing suite for Frappe",
    author="Codebase Technologies",
    author_email="dev@codebtech.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "pikepdf>=8.0.0",
        "pdfplumber>=0.10.0",
        "reportlab>=4.0",
        "fpdf2>=2.7.0",
        "pytesseract>=0.3.10",
        "pdf2docx>=0.5.8",
        "python-docx>=1.0.0",
        "Pillow>=10.0.0",
        "weasyprint>=62.0",
    ],
)
