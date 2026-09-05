import sys
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress headers/footers on cover page
            return
        
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 755, 572, 755)
        self.drawString(40, 760, "RentPoint — Full Project Engineering & Architecture Documentation")
        self.drawRightString(572, 760, "Nsukka Urban Rental Marketplace")
        
        # Footer
        self.line(40, 45, 572, 45)
        self.drawString(40, 32, "Confidential — RentPoint System Architecture & Reference Manual")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(572, 32, page_str)
        self.restoreState()

def build_pdf(pdf_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Palette
    c_navy = colors.HexColor("#0A2342")
    c_teal = colors.HexColor("#00A896")
    c_teal_dark = colors.HexColor("#028074")
    c_amber = colors.HexColor("#D97706")
    c_dark = colors.HexColor("#1E293B")
    c_muted = colors.HexColor("#64748B")
    c_bg_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_navy,
        alignment=0,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_teal_dark,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_navy,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_teal_dark,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_navy
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#065F46")
    )

    story = []

    # -------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------
    story.append(Spacer(1, 20))
    story.append(Paragraph("<font color='#00A896'><b>Rent</b></font><b>Point</b>", title_style))
    story.append(Paragraph("Automated Web-Based Property and Rental Management System for Nsukka Urban", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_teal, spaceBefore=0, spaceAfter=15))
    
    story.append(Paragraph("<b>Comprehensive Technical & Architectural Master Document</b>", h2_style))
    story.append(Paragraph("This document provides an exhaustive, end-to-end breakdown of the RentPoint system from initial scratch development to full production deployment. It covers all frameworks, libraries, modules, data models, subsystems, security architecture, design system tokens, workflows, and configuration specifications.", body_style))
    story.append(Spacer(1, 10))

    # Meta table
    meta_data = [
        [Paragraph("<b>Platform Name</b>", table_cell_bold), Paragraph("RentPoint", table_cell_style), Paragraph("<b>Target Area</b>", table_cell_bold), Paragraph("Nsukka Urban, Enugu State, Nigeria", table_cell_style)],
        [Paragraph("<b>Framework</b>", table_cell_bold), Paragraph("Django 6.1 (Python 3.14 / 3.11+)", table_cell_style), Paragraph("<b>Architecture</b>", table_cell_bold), Paragraph("Modular Multi-App MVT Architecture", table_cell_style)],
        [Paragraph("<b>Primary Payment Gateway</b>", table_cell_bold), Paragraph("Paystack (Card, Transfer, USSD)", table_cell_style), Paragraph("<b>Platform Fee</b>", table_cell_bold), Paragraph("8.0% Platform Commission", table_cell_style)],
        [Paragraph("<b>Database Engine</b>", table_cell_bold), Paragraph("SQLite (Dev) / PostgreSQL / MySQL", table_cell_style), Paragraph("<b>Production Server</b>", table_cell_bold), Paragraph("Gunicorn + WhiteNoise (Render / Railway)", table_cell_style)],
        [Paragraph("<b>Email Services</b>", table_cell_bold), Paragraph("Brevo SMTP / Gmail App Passwords", table_cell_style), Paragraph("<b>Document Date</b>", table_cell_bold), Paragraph("September 2026", table_cell_style)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 145, 110, 157])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Table of contents preview
    story.append(Paragraph("<b>Table of Contents</b>", h2_style))
    toc_items = [
        "1. Executive Overview & System Mission",
        "2. Complete Technology Stack & Dependency Matrix (What, Where & Why)",
        "3. System Architecture & Directory Layout",
        "4. Database Schema & Data Models Specification",
        "5. Core Functional Subsystems & Technical Implementation",
        "   5.1 Dual-Role Authentication & Password Recovery Subsystem",
        "   5.2 Owner Identity & NIN Verification Subsystem",
        "   5.3 Listing Management, Dynamic Units & Pricing Simulator",
        "   5.4 Booking Lifecycle, Daily Rate Calculation & Real Receipts Engine",
        "   5.5 Payment Gateway (Paystack), Escrow & Wallet Settlement Engine",
        "   5.6 Site Administration, Moderation & Dispute Resolution",
        "6. Frontend Engineering & Custom Design System",
        "7. Production Deployment, Environment Configuration & Operational Runbook",
        "8. Complete Project File Reference Matrix"
    ]
    for item in toc_items:
        story.append(Paragraph(f"&bull; {item}", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 1: EXECUTIVE OVERVIEW
    # -------------------------------------------------------------
    story.append(Paragraph("1. Executive Overview & System Mission", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("<b>1.1 Background & Problem Statement</b>", h2_style))
    story.append(Paragraph(
        "In urban university and commercial towns such as <b>Nsukka Urban</b>, access to rental properties, event equipment (canopies, chairs, sound systems), household gadgets, tools, and appliances has historically suffered from several friction points: unverified vendors, lack of price transparency, payment disputes, zero digital audit trail, physical receipts that get lost, and insecurity for equipment owners who rent to strangers.",
        body_style
    ))
    story.append(Paragraph(
        "<b>RentPoint</b> was conceived, architected, and built as a comprehensive, modern, automated web-based rental management platform that connects verified Item Owners with Customers looking to rent items, backed by automated Paystack escrow payments, digital receipts, NIN identity verification, dispute handling, and a digital wallet payout system.",
        body_style
    ))

    story.append(Paragraph("<b>1.2 Target Stakeholders & Roles</b>", h2_style))
    story.append(Paragraph("The platform enforces distinct access controls and permissions across three principal user categories:", body_style))
    story.append(Paragraph("<b>1. Customer (Renter):</b> Searches and filters verified listings in Nsukka Urban, calculates multi-day rental costs with clear formulas, books items, pays via Paystack, receives immediate printable PDF/HTML receipts, tracks active/completed bookings, requests extensions, and files disputes if needed.", bullet_style))
    story.append(Paragraph("<b>2. Item Owner:</b> Creates and manages listings with multiple high-resolution photos, dynamic item unit descriptions (e.g. 50 chairs, 4 pots, 2 sound mixers), daily pricing, views real-time earnings simulations, verifies national identity via NIN and webcam selfie, tracks incoming bookings, approves returns, and withdraws rental earnings to their Nigerian bank account.", bullet_style))
    story.append(Paragraph("<b>3. Platform Administrator:</b> Reviews and approves/rejects Owner NIN verification submissions, reviews transaction disputes, monitors rental volumes, approves bank withdrawal payouts, and manages site-wide configurations.", bullet_style))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 2: TECHNOLOGY STACK & DEPENDENCIES
    # -------------------------------------------------------------
    story.append(Paragraph("2. Complete Technology Stack & Dependency Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph("Every dependency in RentPoint was deliberately selected to ensure zero unnecessary bloat, robust security, zero-cost production capability, and high performance:", body_style))

    tech_headers = [Paragraph("<b>Technology / Package</b>", table_header_style), Paragraph("<b>Version</b>", table_header_style), Paragraph("<b>Where Used</b>", table_header_style), Paragraph("<b>Purpose & Technical Rationale</b>", table_header_style)]
    tech_rows = [
        [Paragraph("<b>Django</b>", table_cell_bold), Paragraph("6.1.*", table_cell_style), Paragraph("Core Backend (All Apps)", table_cell_style), Paragraph("Web framework providing ORM, authentication, CSRF/XSS protection, template engine, CBVs, form validation, and admin.", table_cell_style)],
        [Paragraph("<b>Python</b>", table_cell_bold), Paragraph("3.11 - 3.14", table_cell_style), Paragraph("Runtime Language", table_cell_style), Paragraph("Primary server-side language executing all business logic, financial arithmetic, and security tokens.", table_cell_style)],
        [Paragraph("<b>Pillow</b>", table_cell_bold), Paragraph(">=12.3.0", table_cell_style), Paragraph("<code>listings/models.py</code>, <code>accounts/models.py</code>", table_cell_style), Paragraph("Image processing engine handling listing uploads, thumbnail generation, and NIN verification photo verification.", table_cell_style)],
        [Paragraph("<b>WhiteNoise</b>", table_cell_bold), Paragraph("6.*", table_cell_style), Paragraph("<code>config/wsgi.py</code>, <code>config/settings.py</code>", table_cell_style), Paragraph("Serves compressed static files directly from Gunicorn with cache-busting hashes, eliminating complex Nginx configurations on cloud hosts.", table_cell_style)],
        [Paragraph("<b>Gunicorn</b>", table_cell_bold), Paragraph("23.*", table_cell_style), Paragraph("Production WSGI Runner", table_cell_style), Paragraph("High-concurrency, multi-worker WSGI HTTP server designed for production deployment on Render/Railway/Fly.io.", table_cell_style)],
        [Paragraph("<b>psycopg2-binary</b>", table_cell_bold), Paragraph("2.*", table_cell_style), Paragraph("<code>config/settings.py</code>", table_cell_style), Paragraph("PostgreSQL database adapter enabling connection to free cloud databases (Supabase, Railway, Neon, AWS RDS).", table_cell_style)],
        [Paragraph("<b>mysqlclient</b>", table_cell_bold), Paragraph("2.*", table_cell_style), Paragraph("<code>config/settings.py</code>", table_cell_style), Paragraph("High-performance MySQL driver used when DB_ENGINE=mysql on shared cPanel or cloud MySQL instances.", table_cell_style)],
        [Paragraph("<b>ReportLab</b>", table_cell_bold), Paragraph("4.*", table_cell_style), Paragraph("<code>docs/</code>, Document Generator", table_cell_style), Paragraph("Generates pixel-perfect, secure, standalone PDF documentation and formal system manuals programmatically.", table_cell_style)],
        [Paragraph("<b>Paystack API</b>", table_cell_bold), Paragraph("v2 REST / Inline", table_cell_style), Paragraph("<code>transactions/views.py</code>, <code>wallet/views.py</code>", table_cell_style), Paragraph("Primary Nigerian payment gateway handling Debit Card, Bank Transfer, and USSD payments with HMAC SHA512 webhooks.", table_cell_style)],
        [Paragraph("<b>Brevo / Gmail SMTP</b>", table_cell_bold), Paragraph("TLS (Port 587)", table_cell_style), Paragraph("<code>accounts/forms.py</code>, <code>config/settings.py</code>", table_cell_style), Paragraph("Free SMTP transactional delivery for password recovery links, rental receipts, and account notices.", table_cell_style)],
        [Paragraph("<b>Vanilla JS</b>", table_cell_bold), Paragraph("ES6+ Native", table_cell_style), Paragraph("<code>static/js/main.js</code>", table_cell_style), Paragraph("Zero-dependency client scripting for camera capture, dynamic pricing calculator, gallery zoom, password strength meter.", table_cell_style)],
        [Paragraph("<b>Vanilla CSS3</b>", table_cell_bold), Paragraph("Design Tokens", table_cell_style), Paragraph("<code>static/css/main.css</code>", table_cell_style), Paragraph("Custom design system with CSS custom properties, responsive Flexbox/Grid, print stylesheets, glassmorphism, and animations.", table_cell_style)],
    ]
    
    tech_table = Table([tech_headers] + tech_rows, colWidths=[90, 50, 115, 277])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(tech_table)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 3: SYSTEM ARCHITECTURE & DIRECTORY LAYOUT
    # -------------------------------------------------------------
    story.append(Paragraph("3. System Architecture & Modular Layout", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph(
        "RentPoint follows Django's clean <b>Separation of Concerns</b> by organizing features into isolated domain apps. The platform is configured so each app owns its models, forms, views, URLs, tests, and domain templates:",
        body_style
    ))

    arch_headers = [Paragraph("<b>Directory / App</b>", table_header_style), Paragraph("<b>Core Responsibility & Components</b>", table_header_style)]
    arch_rows = [
        [Paragraph("<b><code>config/</code></b>", table_cell_bold), Paragraph("Root configuration holding <code>settings.py</code> (environment-driven, auto-switches DBs, email, staticfiles), <code>urls.py</code> (master routing table), and <code>wsgi.py</code>.", table_cell_style)],
        [Paragraph("<b><code>accounts/</code></b>", table_cell_bold), Paragraph("User identity, RBAC (Customer vs. Item Owner), NIN verification submission, live webcam selfie capture, profile management, and 4-step secure password reset.", table_cell_style)],
        [Paragraph("<b><code>listings/</code></b>", table_cell_bold), Paragraph("Categories, Item catalog, multi-photo gallery upload, daily pricing, search/filter, condition rating, dynamic quantity units, and owner pricing simulators.", table_cell_style)],
        [Paragraph("<b><code>transactions/</code></b>", table_cell_bold), Paragraph("Rental checkout, daily rate formula calculation, Paystack payment processing, itemized real receipts, receipt printing, rental status transitions, extensions, and disputes.", table_cell_style)],
        [Paragraph("<b><code>wallet/</code></b>", table_cell_bold), Paragraph("Financial ledger for Item Owners, escrow balance holds, platform commission calculation (8%), available balance tracking, and bank account withdrawal requests.", table_cell_style)],
        [Paragraph("<b><code>core/</code></b>", table_cell_bold), Paragraph("Landing page, search discovery, Site Admin dashboard (NIN review, dispute resolution, analytics), custom 404/500 handlers, and site-wide context processors.", table_cell_style)],
        [Paragraph("<b><code>static/</code></b>", table_cell_bold), Paragraph("Custom design system in <code>css/main.css</code>, client behaviors in <code>js/main.js</code>, and SVG brand assets/favicons in <code>img/</code>.", table_cell_style)],
        [Paragraph("<b><code>templates/</code></b>", table_cell_bold), Paragraph("Shared global templates: <code>base.html</code>, navigation bars, flash messages, modal popups, error pages, and site admin views.", table_cell_style)],
        [Paragraph("<b><code>docs/</code></b>", table_cell_bold), Paragraph("Complete operations documentation: <code>RUNBOOK.md</code>, <code>DESIGN.md</code>, <code>email.md</code>, <code>render.md</code>, and <code>rentpointdoc.pdf</code>.", table_cell_style)],
    ]
    arch_table = Table([arch_headers] + arch_rows, colWidths=[120, 412])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 4: DATABASE SCHEMA & DATA MODELS
    # -------------------------------------------------------------
    story.append(Paragraph("4. Database Schema & Data Models Specification", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph("The database schema enforces referential integrity, decimal precision for currency amounts, indexed query lookups, and lifecycle status machines:", body_style))

    model_headers = [Paragraph("<b>Model Name</b>", table_header_style), Paragraph("<b>Key Fields & Data Types</b>", table_header_style), Paragraph("<b>Business Rules & Relationships</b>", table_header_style)]
    model_rows = [
        [
            Paragraph("<b><code>User</code></b><br/>(accounts)", table_cell_bold),
            Paragraph("<code>role</code> (CUSTOMER / ITEM_OWNER)<br/><code>phone_number</code> (CharField 20)<br/><code>verification_status</code> (UNVERIFIED / PENDING / VERIFIED / REJECTED)<br/><code>address</code> (CharField 255)", table_cell_style),
            Paragraph("Extends <code>AbstractUser</code>. Central identity entity for customers, item owners, and site administrators. Enforces role-based views and guards.", table_cell_style)
        ],
        [
            Paragraph("<b><code>OwnerVerification</code></b><br/>(accounts)", table_cell_bold),
            Paragraph("<code>owner</code> (OneToOne &rarr; User)<br/><code>full_legal_name</code> (CharField 200)<br/><code>nin</code> (CharField 11)<br/><code>selfie_image</code> (ImageField)<br/><code>nin_front_image</code> (ImageField)<br/><code>nin_back_image</code> (ImageField)<br/><code>status</code> (PENDING / APPROVED / REJECTED)", table_cell_style),
            Paragraph("Collects verified NIN and webcam selfie photos. Overrides <code>save()</code> and <code>delete()</code> to automatically clean up disk image files when updated or deleted.", table_cell_style)
        ],
        [
            Paragraph("<b><code>Category</code></b><br/>(listings)", table_cell_bold),
            Paragraph("<code>name</code> (CharField 100, unique)<br/><code>slug</code> (SlugField 100, unique)<br/><code>description</code> (TextField)", table_cell_style),
            Paragraph("Organizes items (e.g. Household & Kitchen, Sound Systems, Party Equipment, Power & Generators, Construction).", table_cell_style)
        ],
        [
            Paragraph("<b><code>Item</code></b><br/>(listings)", table_cell_bold),
            Paragraph("<code>owner</code> (ForeignKey &rarr; User)<br/><code>category</code> (ForeignKey &rarr; Category)<br/><code>name</code> (CharField 200)<br/><code>daily_rate</code> (DecimalField 10,2)<br/><code>quantity_available</code> (PositiveIntegerField)<br/><code>condition</code> (EXCELLENT / GOOD / FAIR)<br/><code>is_active</code> (BooleanField)", table_cell_style),
            Paragraph("Represents rental inventory. Computes dynamic units (e.g. '1 spoon', '4 pots', '50 chairs') and checks real-time availability.", table_cell_style)
        ],
        [
            Paragraph("<b><code>Transaction</code></b><br/>(transactions)", table_cell_bold),
            Paragraph("<code>customer</code> (ForeignKey &rarr; User)<br/><code>item</code> (ForeignKey &rarr; Item)<br/><code>start_date</code>, <code>end_date</code> (DateField)<br/><code>duration_days</code> (IntegerField)<br/><code>quantity</code> (IntegerField)<br/><code>daily_rate</code> (DecimalField)<br/><code>subtotal</code>, <code>platform_fee</code>, <code>total_amount</code> (DecimalField 10,2)<br/><code>status</code> (PENDING / PAID / ACTIVE / COMPLETED / CANCELLED / DISPUTED)<br/><code>payment_reference</code> (CharField 100, unique)", table_cell_style),
            Paragraph("The central contract of a rental. Automatically calculates pricing formula (<code>daily_rate × quantity × days</code>). Manages Paystack payment verification, receipt generation, and escrow release.", table_cell_style)
        ],
        [
            Paragraph("<b><code>Wallet</code></b><br/>(wallet)", table_cell_bold),
            Paragraph("<code>owner</code> (OneToOne &rarr; User)<br/><code>balance</code> (DecimalField 12,2)<br/><code>pending_balance</code> (DecimalField 12,2)", table_cell_style),
            Paragraph("Maintains ledger balance for each Item Owner. Escrow holds funds during active rentals and credits available balance upon verified return.", table_cell_style)
        ],
        [
            Paragraph("<b><code>WithdrawalRequest</code></b><br/>(wallet)", table_cell_bold),
            Paragraph("<code>wallet</code> (ForeignKey &rarr; Wallet)<br/><code>amount</code> (DecimalField 10,2)<br/><code>bank_name</code>, <code>account_number</code>, <code>account_name</code><br/><code>status</code> (PENDING / APPROVED / REJECTED)", table_cell_style),
            Paragraph("Enables item owners to withdraw earned rental income. Enforces minimum withdrawal threshold (₦1,000) and balance checks.", table_cell_style)
        ]
    ]

    model_table = Table([model_headers] + model_rows, colWidths=[90, 180, 262])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(model_table)
    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 5: CORE FUNCTIONAL SUBSYSTEMS
    # -------------------------------------------------------------
    story.append(Paragraph("5. Core Functional Subsystems & Technical Implementation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("5.1 Dual-Role Authentication & Password Recovery Subsystem", h2_style))
    story.append(Paragraph(
        "RentPoint implements strict role-based registration via distinct entry points (<code>/accounts/signup/customer/</code> and <code>/accounts/signup/item-owner/</code>) to prevent accidental role ambiguity. Password authentication uses Django's Argon2/PBKDF2 SHA256 password hashers.",
        body_style
    ))
    story.append(Paragraph("<b>Password Reset Engineering:</b>", h3_style))
    story.append(Paragraph("<b>1. Timing Attack & Enumeration Protection:</b> Submitting an unknown email returns the identical success confirmation screen, preventing malicious actors from harvesting registered emails.", bullet_style))
    story.append(Paragraph("<b>2. Branded HTML Email Dispatch:</b> Sends responsive, cross-client HTML emails (with dark navy header, emerald CTA button, and 24-hour expiration token) alongside a plain-text fallback.", bullet_style))
    story.append(Paragraph("<b>3. Interactive Client-Side Strength Meter:</b> Built in <code>static/js/main.js</code> with dynamic 4-bar colored feedback (Weak &rarr; Fair &rarr; Good &rarr; Strong) and real-time rule checklist.", bullet_style))
    story.append(Paragraph("<b>4. One-Time Token Invalidation:</b> Once used or expired, tokens immediately invalidate, redirecting to an explicit 'Link Expired or Invalid' recovery screen.", bullet_style))

    story.append(Paragraph("5.2 Owner Identity & NIN Verification Subsystem", h2_style))
    story.append(Paragraph(
        "To build customer trust, Item Owners must verify their identity. The owner submits their 11-digit NIN, live front and back card images, and a live webcam photo captured directly via HTML5 <code>navigator.mediaDevices.getUserMedia()</code>. Submissions enter a <code>PENDING</code> queue reviewed in the Site Admin panel.",
        body_style
    ))

    story.append(Paragraph("5.3 Booking Lifecycle, Daily Rate Calculation & Real Receipts Engine", h2_style))
    story.append(Paragraph(
        "Rentals are calculated per day rather than ambiguous event units. The system applies a rigorous pricing formula:",
        body_style
    ))
    story.append(Paragraph("<b>Daily Calculation Formula:</b> Total = Daily Rate &times; Quantity &times; Duration (Days)", code_style))
    story.append(Paragraph(
        "Upon payment, RentPoint generates a <b>Real Itemized Receipt</b> (<code>_receipt_card.html</code>) structured like modern financial enterprise receipts (Stripe/Square/Apple), featuring:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Clean Proportions:</b> 44% Item Description, 18% Daily Rate, 10% Qty count, 12% Duration, 16% Amount.", bullet_style))
    story.append(Paragraph("&bull; <b>Structured Metadata Badges:</b> Folder category pill tag and green verified condition badge.", bullet_style))
    story.append(Paragraph("&bull; <b>Mathematical Breakdown Badge:</b> Explicit rate verification showing <code>Calculation: ₦Rate × Qty × Days = ₦Total</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>High-DPI Print Stylesheet:</b> Dedicated <code>@media print</code> CSS ensuring receipts fit standard A4/invoice paper with headers, borders, and barcodes without browser clutter.", bullet_style))

    story.append(Paragraph("5.4 Payment Gateway (Paystack), Escrow & Wallet Settlement Engine", h2_style))
    story.append(Paragraph(
        "Payments are processed through Paystack Inline/Standard. When a customer pays, funds are not sent directly to the owner. Instead, RentPoint acts as an <b>Escrow Agent</b>:",
        body_style
    ))
    story.append(Paragraph("1. Customer pays <code>Total Amount</code> &rarr; Webhook verifies HMAC SHA512 signature &rarr; Transaction status becomes <code>PAID</code>.", bullet_style))
    story.append(Paragraph("2. Net amount (<code>Total - 8% Commission</code>) is recorded into the Owner's Wallet as <code>pending_balance</code>.", bullet_style))
    story.append(Paragraph("3. When the rental period ends and the item is returned in good condition, the status transitions to <code>COMPLETED</code> and the funds automatically move from <code>pending_balance</code> to <code>balance</code>.", bullet_style))
    story.append(Paragraph("4. The Item Owner can initiate a bank withdrawal request to any verified Nigerian bank account.", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 6: FRONTEND DESIGN SYSTEM
    # -------------------------------------------------------------
    story.append(Paragraph("6. Frontend Engineering & Custom Design System", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph(
        "RentPoint's frontend is entirely dependency-free: no heavy npm build steps, Webpack configurations, or bloated CSS frameworks. It uses vanilla CSS3 custom properties and clean vanilla JavaScript for lightning-fast page loads.",
        body_style
    ))

    design_headers = [Paragraph("<b>Design Token / Variable</b>", table_header_style), Paragraph("<b>Value / Hex</b>", table_header_style), Paragraph("<b>Application & Usage</b>", table_header_style)]
    design_rows = [
        [Paragraph("<code>--color-primary-navy</code>", table_cell_bold), Paragraph("#0A2342", table_cell_style), Paragraph("Primary brand identity, page headers, navigation bar, authority badges, and button active states.", table_cell_style)],
        [Paragraph("<code>--color-accent-teal</code>", table_cell_bold), Paragraph("#00A896", table_cell_style), Paragraph("Primary CTA gradients, interactive links, success highlights, active tabs, and focus outlines.", table_cell_style)],
        [Paragraph("<code>--color-accent-amber</code>", table_cell_bold), Paragraph("#D97706", table_cell_style), Paragraph("Item owner badges, warnings, pending statuses, and review stars.", table_cell_style)],
        [Paragraph("<code>--color-bg</code>", table_cell_bold), Paragraph("#F8FAFC", table_cell_style), Paragraph("Clean modern background tone preventing eye strain and enhancing contrast.", table_cell_style)],
        [Paragraph("<code>--font-display</code>", table_cell_bold), Paragraph("'Outfit', sans-serif", table_cell_style), Paragraph("Typography for high-impact headlines, numbers, currency values, and card titles.", table_cell_style)],
        [Paragraph("<code>--font-body</code>", table_cell_bold), Paragraph("'Plus Jakarta Sans'", table_cell_style), Paragraph("Clean, readable body copy, form inputs, metadata tags, and table cells.", table_cell_style)],
        [Paragraph("<code>--font-mono</code>", table_cell_bold), Paragraph("'JetBrains Mono'", table_cell_style), Paragraph("Financial receipts, reference codes, timestamps, and currency calculations.", table_cell_style)],
    ]
    design_table = Table([design_headers] + design_rows, colWidths=[150, 110, 272])
    design_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(design_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 7: PRODUCTION DEPLOYMENT & OPERATIONS
    # -------------------------------------------------------------
    story.append(Paragraph("7. Production Deployment & Operations Runbook", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))
    story.append(Paragraph(
        "RentPoint is architected to run seamlessly on both zero-config local development environments and multi-container cloud infrastructure (Render, Railway, Fly.io, AWS, Heroku):",
        body_style
    ))

    story.append(Paragraph("<b>7.1 Automated Database Switching:</b>", h2_style))
    story.append(Paragraph("Setting <code>DB_ENGINE=postgres</code> and providing a <code>DATABASE_URL</code> (e.g. from Supabase) automatically configures PostgreSQL with SSL enforcement. In local development, leaving it unset defaults safely to SQLite.", body_style))

    story.append(Paragraph("<b>7.2 Static Asset Delivery:</b>", h2_style))
    story.append(Paragraph("When <code>DJANGO_DEBUG=False</code>, WhiteNoise automatically compresses static files into Gzip/Brotli format and applies permanent cache headers (<code>Cache-Control: max-age=31536000</code>).", body_style))

    story.append(Paragraph("<b>7.3 Production Security Hardening:</b>", h2_style))
    story.append(Paragraph("&bull; <b>SSL / HTTPS Enforcement:</b> <code>SECURE_SSL_REDIRECT = True</code> and <code>SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>HSTS Preload:</b> <code>SECURE_HSTS_SECONDS = 31536000</code> (1 year) with subdomains enabled.", bullet_style))
    story.append(Paragraph("&bull; <b>Secure Cookies:</b> <code>SESSION_COOKIE_SECURE = True</code> and <code>CSRF_COOKIE_SECURE = True</code>.", bullet_style))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # SECTION 8: COMPLETE FILE REFERENCE MATRIX
    # -------------------------------------------------------------
    story.append(Paragraph("8. Complete Project File Reference Matrix", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=8))

    file_headers = [Paragraph("<b>File Path</b>", table_header_style), Paragraph("<b>Type</b>", table_header_style), Paragraph("<b>Detailed Functionality & Role</b>", table_header_style)]
    file_rows = [
        [Paragraph("<code>manage.py</code>", table_cell_bold), Paragraph("CLI Entry", table_cell_style), Paragraph("Django's command-line runner for migrations, tests, local dev server, and custom management commands.", table_cell_style)],
        [Paragraph("<code>config/settings.py</code>", table_cell_bold), Paragraph("Settings", table_cell_style), Paragraph("Master configuration: database engine switching, email backend, WhiteNoise, Paystack keys, and security hardening.", table_cell_style)],
        [Paragraph("<code>config/urls.py</code>", table_cell_bold), Paragraph("Root Router", table_cell_style), Paragraph("Top-level URL dispatch table mounting accounts, listings, transactions, wallet, core, and media handlers.", table_cell_style)],
        [Paragraph("<code>accounts/models.py</code>", table_cell_bold), Paragraph("Models", table_cell_style), Paragraph("Defines <code>User</code> (multi-role) and <code>OwnerVerification</code> with automated media deletion.", table_cell_style)],
        [Paragraph("<code>accounts/forms.py</code>", table_cell_bold), Paragraph("Forms", table_cell_style), Paragraph("Defines <code>SignUpForm</code>, <code>LoginForm</code>, <code>RentPointPasswordResetForm</code>, and <code>OwnerVerificationForm</code>.", table_cell_style)],
        [Paragraph("<code>accounts/views.py</code>", table_cell_bold), Paragraph("Views", table_cell_style), Paragraph("Implements customer/owner registration, login/logout, password reset CBVs, and identity verification.", table_cell_style)],
        [Paragraph("<code>listings/models.py</code>", table_cell_bold), Paragraph("Models", table_cell_style), Paragraph("Defines <code>Category</code>, <code>Item</code> (daily rate, quantity, condition), and <code>ItemImage</code>.", table_cell_style)],
        [Paragraph("<code>listings/views.py</code>", table_cell_bold), Paragraph("Views", table_cell_style), Paragraph("Listing catalog, search/filter, detail view, creation/edit forms, and photo management.", table_cell_style)],
        [Paragraph("<code>transactions/models.py</code>", table_cell_bold), Paragraph("Models", table_cell_style), Paragraph("Defines <code>Transaction</code>, <code>RentalExtension</code>, <code>Dispute</code>, and <code>Review</code> models.", table_cell_style)],
        [Paragraph("<code>transactions/views.py</code>", table_cell_bold), Paragraph("Views", table_cell_style), Paragraph("Checkout handler, Paystack payment webhook, real itemized receipt rendering, return confirmation.", table_cell_style)],
        [Paragraph("<code>wallet/models.py</code>", table_cell_bold), Paragraph("Models", table_cell_style), Paragraph("Defines <code>Wallet</code>, <code>WalletTransaction</code>, and <code>WithdrawalRequest</code>.", table_cell_style)],
        [Paragraph("<code>wallet/views.py</code>", table_cell_bold), Paragraph("Views", table_cell_style), Paragraph("Earnings overview, ledger statement, and bank withdrawal request submission.", table_cell_style)],
        [Paragraph("<code>core/views.py</code>", table_cell_bold), Paragraph("Views", table_cell_style), Paragraph("Landing page, custom Site Admin dashboard (NIN reviews, disputes, withdrawals, analytics), 404/500 handlers.", table_cell_style)],
        [Paragraph("<code>static/css/main.css</code>", table_cell_bold), Paragraph("CSS System", table_cell_style), Paragraph("Comprehensive design system tokens, typography, cards, receipt styling, and print stylesheets.", table_cell_style)],
        [Paragraph("<code>static/js/main.js</code>", table_cell_bold), Paragraph("JavaScript", table_cell_style), Paragraph("Camera capture, image zoom gallery, dynamic pricing calculator, and password strength meter.", table_cell_style)],
        [Paragraph("<code>docs/email.md</code>", table_cell_bold), Paragraph("Docs", table_cell_style), Paragraph("Step-by-step setup guide for 100% free forever transactional email delivery (Gmail App Password & Brevo).", table_cell_style)],
        [Paragraph("<code>docs/RUNBOOK.md</code>", table_cell_bold), Paragraph("Docs", table_cell_style), Paragraph("Production deployment manual, environment variable reference, database commands, and maintenance.", table_cell_style)],
    ]
    file_table = Table([file_headers] + file_rows, colWidths=[125, 65, 342])
    file_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(file_table)

    # Build document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {pdf_path}")

if __name__ == "__main__":
    out_dir = Path("c:/rentpoint/docs")
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_file = out_dir / "rentpointdoc.pdf"
    build_pdf(str(pdf_file))
