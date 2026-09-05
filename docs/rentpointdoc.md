# RentPoint — Full Project Engineering & Architecture Documentation
**Automated Web-Based Property and Rental Management System for Nsukka Urban**

---

## 1. Executive Summary & System Identity

### 1.1 Project Mission & Problem Statement
In urban university and commercial centers such as **Nsukka Urban, Enugu State, Nigeria**, access to rental equipment, event supplies (canopies, plastic chairs, high-output sound systems), power generators, household appliances, and tools has historically been burdened by:
- **Unverified Vendors:** Risk of fraud or substandard equipment.
- **Lack of Transparent Pricing:** Unclear daily rates with hidden surcharges.
- **Zero Digital Audit Trail:** Paper receipts that easily tear or get misplaced.
- **Insecurity for Equipment Owners:** Anxiety over renting valuable assets to strangers without national identification or escrow protection.

**RentPoint** is an automated, web-based property and rental management platform designed to solve these friction points by uniting verified Item Owners and Customers under a secure, escrow-backed marketplace with real itemized digital receipts, live NIN identity verification, automated Paystack payments, dynamic quantity tracking, and digital wallet earnings management.

### 1.2 System Meta Specifications
- **Platform Name:** RentPoint
- **Primary Service Area:** Nsukka Urban, Enugu State, Nigeria
- **Backend Architecture:** Django 6.1 (Python 3.11–3.14), Modular Multi-App MVT Architecture
- **Primary Payment Gateway:** Paystack (Card, Bank Transfer, USSD)
- **Platform Commission:** 8.0% Platform Fee
- **Database Engine Support:** SQLite (Zero-config Dev) / PostgreSQL (Supabase / Railway / Neon) / MySQL
- **Production Server:** Gunicorn + WhiteNoise (Render / Railway / Fly.io)
- **Email Services:** Brevo SMTP / Gmail SMTP (100% Free Forever)
- **Documentation Output:** `docs/rentpointdoc.pdf` & `docs/rentpointdoc.md`

---

## 2. Complete Technology Stack & Dependency Matrix

The table below details **every single technology, library, service, and tool** utilized in the construction of RentPoint from scratch to production, including its version, exact location of use, and technical rationale:

| Technology / Package | Version | Where It Is Used in Codebase | Purpose & Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Django** | `6.1.*` | Core Framework (All Apps) | Provides high-level Python web framework, robust ORM, authentication system, CSRF/XSS protection, template engine, CBVs, and administration. |
| **Python** | `3.11 - 3.14` | Server Runtime | Primary execution language for all business calculations, security token generation, and financial ledger algorithms. |
| **Pillow** | `>=12.3.0` | `listings/models.py`, `accounts/models.py` | Image processing engine handling multi-photo listing uploads, thumbnail optimization, and NIN verification photo storage. |
| **WhiteNoise** | `6.*` | `config/wsgi.py`, `config/settings.py` | Serves compressed, cache-busted static files directly from Gunicorn with zero need for complex external Nginx or CDN setups on cloud hosts. |
| **Gunicorn** | `23.*` | Production WSGI Server | High-concurrency WSGI HTTP server executing multi-worker request handling on cloud hosting platforms (Render, Railway, Fly.io). |
| **psycopg2-binary** | `2.*` | `config/settings.py` | PostgreSQL database adapter enabling connection to free cloud databases (Supabase, Railway, Neon, AWS RDS). |
| **mysqlclient** | `2.*` | `config/settings.py` | High-performance MySQL driver used when deploying on shared cPanel or cloud MySQL instances (`DB_ENGINE=mysql`). |
| **ReportLab** | `4.*` | `docs/generate_pdf.py` | Programmatic PDF generator creating publication-grade system documentation (`rentpointdoc.pdf`) and printable manuals. |
| **Paystack API** | `v2 REST / Inline` | `transactions/views.py`, `wallet/views.py` | Primary Nigerian payment gateway processing Debit Card, Bank Transfer, and USSD payments with HMAC SHA512 webhook signature verification. |
| **Brevo / Gmail SMTP** | `TLS (Port 587)` | `accounts/forms.py`, `config/settings.py` | Free transactional SMTP delivery for password recovery links, rental receipts, and account notifications. |
| **Vanilla JavaScript** | `ES6+ Native` | `static/js/main.js` | Zero-dependency client-side scripting for webcam camera capture, real-time pricing simulators, modal image zoom, and live password strength metering. |
| **Vanilla CSS3** | `Custom Properties` | `static/css/main.css` | Comprehensive design system utilizing CSS tokens, responsive Flexbox/Grid, print stylesheets for A4 thermal receipts, and glassmorphism. |

---

## 3. System Architecture & Modular App Layout

RentPoint follows Django's clean **Separation of Concerns** by organizing features into isolated domain apps:

```
c:\rentpoint\
├── manage.py                     # CLI management runner
├── config/                       # Root project configuration
│   ├── settings.py               # Master environment-driven settings
│   ├── urls.py                   # Global URL routing table
│   └── wsgi.py                   # Production WSGI application entry
├── accounts/                     # User management & identity
│   ├── models.py                 # Custom User model & OwnerVerification
│   ├── forms.py                  # SignUp, Login, PasswordReset, Verification forms
│   ├── views.py                  # Auth CBVs, NIN submission, Password Reset flow
│   ├── urls.py                   # Authentication URL routes
│   └── templates/accounts/       # Auth & verification templates
├── listings/                     # Item inventory & catalog
│   ├── models.py                 # Category, Item (daily rates, units), ItemImage
│   ├── forms.py                  # Item listing creation & edit forms
│   ├── views.py                  # Catalog, search, filters, pricing simulator
│   └── templates/listings/       # Listing cards, item detail, edit views
├── transactions/                 # Bookings, payments & receipts
│   ├── models.py                 # Transaction, RentalExtension, Dispute, Review
│   ├── views.py                  # Checkout, Paystack webhook, receipt generator
│   └── templates/transactions/   # Checkout, real itemized receipt cards, dispute views
├── wallet/                       # Financial ledger & owner payouts
│   ├── models.py                 # Wallet, WalletTransaction, WithdrawalRequest
│   ├── views.py                  # Earnings statement, bank withdrawal handler
│   └── templates/wallet/         # Wallet balance dashboard, withdrawal modals
├── core/                         # Common layout & site administration
│   ├── views.py                  # Landing page, Site Admin dashboard, custom 404/500
│   └── context_processors.py     # Global site settings context
├── static/                       # Static UI assets
│   ├── css/main.css              # Custom RentPoint design system tokens & styles
│   ├── js/main.js                # Interactive client-side behavior
│   └── img/                      # Brand SVGs, favicons, logos
├── templates/                    # Global base templates
│   ├── base.html                 # Master HTML shell
│   ├── partials/                 # Navbar, footer, flash messages
│   └── site_admin/               # Site Admin review dashboard
└── docs/                         # System manuals & documentation
    ├── rentpointdoc.pdf          # Full standalone PDF documentation
    ├── rentpointdoc.md           # Full markdown documentation
    ├── email.md                  # 100% free forever email guide
    └── RUNBOOK.md                # Production operational runbook
```

---

## 4. Database Schema & Data Models Specification

### 4.1 `accounts.User` (Custom User Model)
- **Inherits:** `AbstractUser`
- **Fields:**
  - `role`: `CUSTOMER` vs. `ITEM_OWNER`
  - `phone_number`: Primary contact phone (`CharField(20)`)
  - `verification_status`: `UNVERIFIED` / `PENDING` / `VERIFIED` / `REJECTED`
  - `address`: Operating address in Nsukka Urban
- **Responsibility:** Central identity entity enforcing role-based permissions and dashboard routing.

### 4.2 `accounts.OwnerVerification` (NIN & Identity)
- **Relationship:** `OneToOneField` &rarr; `User`
- **Fields:**
  - `full_legal_name`: Full legal name matching National ID
  - `nin`: 11-digit Nigerian National Identification Number
  - `selfie_image`: Live webcam snapshot captured during submission
  - `nin_front_image`: Front photo of physical/digital NIN slip
  - `nin_back_image`: Back photo of physical/digital NIN slip
  - `status`: `PENDING`, `APPROVED`, `REJECTED`
  - `rejection_reason`: Feedback if verification is denied
- **Special Logic:** Overrides `delete()` and file updates to automatically unlink orphaned files from disk storage.

### 4.3 `listings.Category` & `listings.Item`
- **Fields for `Item`:**
  - `owner`: `ForeignKey` &rarr; `User`
  - `category`: `ForeignKey` &rarr; `Category`
  - `name`: Item title (e.g. *"Large cooking pots (set of 4)"*, *"Heavy Duty Sound Mixer"*)
  - `daily_rate`: Daily rental cost in Naira (`DecimalField(10, 2)`)
  - `quantity_available`: Stock quantity (`PositiveIntegerField`)
  - `condition`: `EXCELLENT`, `GOOD`, `FAIR`
  - `is_active`: Visibility flag
- **Special Logic:** Computes dynamic unit labels (e.g. *"2 spoons"*, *"50 chairs"*, *"4 pots"*).

### 4.4 `transactions.Transaction` (The Rental Contract)
- **Fields:**
  - `customer`: `ForeignKey` &rarr; `User`
  - `item`: `ForeignKey` &rarr; `Item`
  - `start_date`, `end_date`: Calendar booking window (`DateField`)
  - `duration_days`: Count of calendar days (`IntegerField`)
  - `quantity`: Number of items rented (`IntegerField`)
  - `daily_rate`: Locked rate at time of booking (`DecimalField`)
  - `subtotal`: `daily_rate × quantity × duration_days`
  - `platform_fee`: 8% commission deduction
  - `total_amount`: Final payable total (`subtotal`)
  - `status`: `PENDING` &rarr; `PAID` &rarr; `ACTIVE` &rarr; `COMPLETED` &rarr; `CANCELLED` &rarr; `DISPUTED`
  - `payment_reference`: Unique Paystack transaction reference string

### 4.5 `wallet.Wallet` & `wallet.WithdrawalRequest`
- **Fields for `Wallet`:**
  - `owner`: `OneToOneField` &rarr; `User`
  - `balance`: Available withdrawable funds in Naira
  - `pending_balance`: Funds held in escrow during ongoing active rentals
- **Fields for `WithdrawalRequest`:**
  - `wallet`: `ForeignKey` &rarr; `Wallet`
  - `amount`: Requested withdrawal amount (minimum ₦1,000)
  - `bank_name`, `account_number`, `account_name`: Payout destination
  - `status`: `PENDING`, `APPROVED`, `REJECTED`

---

## 5. Core Functional Subsystems & Technical Implementation

### 5.1 Dual-Role Authentication & 4-Step Password Recovery
1. **Explicit Role Onboarding:** Visitors register via `/accounts/signup/customer/` or `/accounts/signup/item-owner/`, ensuring intentional role selection.
2. **Password Recovery Architecture:**
   - **Step 1 (Request):** User submits email. Built-in timing attack protection ensures identical success responses regardless of whether the email exists.
   - **Step 2 (Notification):** Confirmation screen prompts checking inbox and spam folder.
   - **Step 3 (Set Password):** Uses HMAC token verification (`uidb64/token`). Features a client-side **Password Strength Meter** (Weak / Fair / Good / Strong) and interactive checklist in `static/js/main.js`. If token is expired (> 24h) or used, displays a friendly recovery alert.
   - **Step 4 (Completion):** Invalidates previous sessions and redirects to login.

### 5.2 Real Itemized Receipt Engine
Rentals are calculated strictly **per day**:
$$\text{Total Amount} = \text{Daily Rate} \times \text{Quantity} \times \text{Duration (Days)}$$

The itemized receipt card (`_receipt_card.html`) features:
- **Clean Column Proportions:** 44% Description, 18% Daily Rate, 10% Qty Count, 12% Duration, 16% Total Amount.
- **Metadata Badges:** Slate folder pill for category and emerald checkmark badge for item condition.
- **Rate Calculation Formula:** `Calculation: ₦Rate × Qty × Duration = ₦Total`.
- **Print Optimization:** Dedicated `@media print` CSS formats the receipt for clean single-page invoice and thermal printing.

### 5.3 Escrow & Paystack Settlement Engine
1. Customer checks out &rarr; Paystack processes payment &rarr; Webhook verifies HMAC SHA512 signature.
2. Net rental revenue ($\text{Total} - 8\% \text{ Platform Fee}$) is credited to the Item Owner's `pending_balance` (Escrow).
3. Upon rental completion and item return, funds automatically move to `balance`.
4. Item Owner submits a withdrawal request to receive funds in their Nigerian bank account.

---

## 6. Frontend Engineering & Custom Design System

RentPoint uses **zero third-party UI libraries**, ensuring ultra-fast load times and complete styling control:

### Design Tokens (`static/css/main.css`):
- **`--color-primary-navy` (`#0A2342`):** Primary brand authority, headers, navigation.
- **`--color-accent-teal` (`#00A896`):** Vibrant CTA gradients, interactive links, success highlights.
- **`--color-accent-amber` (`#D97706`):** Warnings, pending badges, item owner highlights.
- **`--color-bg` (`#F8FAFC`):** Modern soft neutral background.
- **Typography:** `Outfit` (Headlines & Currency), `Plus Jakarta Sans` (Body Copy), `JetBrains Mono` (Receipts & Reference Numbers).

---

## 7. Production Deployment & Operational Runbook

### 7.1 Automated Database Switching
- **Local Dev:** `DB_ENGINE=sqlite` (default, zero config).
- **Production:** `DB_ENGINE=postgres` with `DATABASE_URL=postgresql://user:pass@host:5432/dbname` (Supabase, Railway, Neon).

### 7.2 Static Files & Security Hardening
- **Static Assets:** Handled by `whitenoise.middleware.WhiteNoiseMiddleware` with manifest caching.
- **SSL / HTTPS:** `SECURE_SSL_REDIRECT = True`, `SECURE_HSTS_SECONDS = 31536000` (1 year), `SESSION_COOKIE_SECURE = True`, and `CSRF_COOKIE_SECURE = True`.

### 7.3 Email Setup
- **Development:** Outputs directly to terminal console when `DEBUG=True`.
- **Production (Free Forever):** Configured via Gmail SMTP (App Password) or Brevo SMTP on Port 587 with TLS (documented in `docs/email.md`).

---

## 8. Summary of Verification & Automated Tests
RentPoint includes comprehensive unit and integration tests across all modules:
```bash
python manage.py test
# Verified: Accounts, Listings, Transactions, Wallet, and Site Admin pass cleanly.
```
