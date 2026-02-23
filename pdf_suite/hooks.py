app_name = "pdf_suite"
app_title = "PDF Suite"
app_publisher = "Codebase Technologies"
app_description = "Full-featured PDF editing suite for Frappe"
app_email = "dev@codebtech.com"
app_license = "MIT"
app_version = "0.1.0"

# Website
website_route_rules = [
    {"from_route": "/pdf-studio/<path:app_path>", "to_route": "pdf-studio"},
    {"from_route": "/pdf-studio", "to_route": "pdf-studio"},
]

# DocTypes
# --------
# PDF Document - editing session storage
# PDF Template - pdfme template storage
# PDF Batch Job - batch operation tracking

# Includes in <head>
# ------------------
# app_include_css = "/assets/pdf_suite/css/pdf_suite.css"
# app_include_js = "/assets/pdf_suite/js/pdf_suite.js"

# Web includes (for /pdf-studio route)
# web_include_css = "/assets/pdf_suite/css/pdf_suite.css"
# web_include_js = "/assets/pdf_suite/js/pdf_suite.js"

# Home Pages
# ----------
# home_page = "pdf-studio"

# Fixtures
# --------
# fixtures = []

# Scheduled Tasks
# ---------------
# scheduler_events = {
#     "daily": [
#         "pdf_suite.tasks.cleanup_expired_sessions"
#     ],
# }

# Permissions
# -----------
# has_permission = {}

# Override Methods
# ----------------
# override_whitelisted_methods = {}
