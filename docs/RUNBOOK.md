# RentPoint — Runbook

RentPoint is the Automated Web-Based Property and Rental Management System
for Nsukka Urban described in the project report, built as a real, working
Django application rather than a mock-up. This document is the single
reference for how the system is designed, how to run it, and how to operate
it day to day.

---

## 1. What was built and why

The report's scope defines five objectives. Each one maps directly onto a
part of this codebase:

| Report objective                                                   | Where it lives                                              |
| ------------------------------------------------------------------ | ----------------------------------------------------------- |
| Web platform for presenting/managing rentable items and properties | `listings` app                                              |
| Item owners list items; customers view details and prices          | `listings` app (owner CRUD + public catalogue)              |
| Secure electronic payment mechanism                                | `transactions` app + `transactions/services.py`             |
| Transaction management for recording/monitoring payments           | `transactions` app (`Transaction` model, receipts, history) |
| Withdrawal mechanism for item owners                               | `wallet` app (`Wallet`, `WithdrawalRequest`)                |

The two operational user types from the report — **customer** and **item
owner** — are modelled as a single `role` field on a custom `User` model
(`accounts` app), so authorization logic lives in one place instead of being
duplicated across views. The **administrator** role from the report is
covered by Django's built-in `is_staff` / `is_superuser` flags and the
Django admin site, rather than a third custom role.

### Design decisions worth knowing about

- **Payment gateway is abstracted**, not hard-coded. `transactions/services.py`
  defines a small `BasePaymentGateway` interface with `charge()` and
  `verify()`. The live implementation is `PaystackGateway`, which handles
  the hosted checkout and verification flow against Paystack's API. The
  project is intentionally configured as Paystack-only, with no mock or
  alternate provider in normal operation. See §6.
- **Money math happens in one place.** `transactions/views.py::_mark_transaction_paid`
  is the only function that marks a transaction paid, calculates the
  platform commission, and credits the item owner's wallet. It runs inside
  a single atomic database transaction so the transaction record and the
  wallet balance can never fall out of sync.
- **Withdrawals are reviewed, not automatic.** An item owner's withdrawal
  request is stored as its own auditable record (`WithdrawalRequest`) with
  a `pending` status. An administrator approves or rejects it from the
  Django admin (bulk actions are provided), which then debits the wallet.
  This matches the report's description of a distinct withdrawal mechanism
  and avoids ever debiting a balance without a record of who approved it.
- **Two Django installs are not needed.** Every piece the report lists
  (Python, Django, HTML, CSS, JavaScript, SQLite, MySQL, Bootstrap-style
  responsive layout) is present, but hand-written CSS is used instead of
  the Bootstrap framework itself, to keep the codebase free of a heavy
  third-party front-end dependency while still meeting every visual and
  responsiveness requirement in the report.

---

## 2. Project layout

```
rentpoint/
├── manage.py
├── requirements.txt
├── .env.example              # copy to .env and fill in for your machine
├── config/                   # project-wide settings, URLs, WSGI/ASGI
│   ├── settings.py
│   └── urls.py
├── accounts/                 # custom User model, sign up, login, profile
├── listings/                 # Category, Item, ItemImage + owner CRUD + catalogue
├── transactions/             # Transaction model, checkout, receipts, payment gateway
├── wallet/                   # Wallet, WithdrawalRequest, earnings dashboard
├── core/                     # home page, about, how-it-works, dashboard redirect
├── templates/                # base.html + shared partials (navbar, footer, alerts)
├── static/
│   ├── css/main.css          # the entire design system, hand-written
│   └── js/main.js            # mobile nav, alert dismiss, formset add, confirm dialogs
├── media/                    # uploaded item photos (created at runtime)
└── docs/
    ├── RUNBOOK.md            # this file
    └── DESIGN.md             # the visual design plan and rationale
```

Each Django app owns its own `models.py`, `views.py`, `urls.py`, `forms.py`
(where relevant), `admin.py`, and `templates/<app_name>/`. Nothing reaches
across app boundaries except through explicit imports (e.g. `transactions`
imports the `Item` model from `listings` and the `Wallet` model from
`wallet`), so any one app can be read, tested, or replaced on its own.

---

## 3. Running it locally

### Requirements

- Python 3.11 or later
- pip

### Steps

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# open .env and set DJANGO_SECRET_KEY to a random string at minimum

# 4. Apply database migrations (SQLite by default, no setup needed)
python manage.py migrate

# 5. Create an administrator account
python manage.py createsuperuser

# 6. (Optional) Load demo categories, a demo item owner, and sample listings
python manage.py seed_demo_data
# creates username "demo_owner", password "DemoOwner!2026"

# 7. Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the site and `http://127.0.0.1:8000/admin/`
for the administrator area.

---

## 4. Environment variables

All configuration lives in environment variables (see `.env.example`), so
the same codebase runs in development and production without code changes.

| Variable                                                  | Purpose                                                                | Default                                    |
| --------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------ |
| `DJANGO_SECRET_KEY`                                       | Cryptographic signing key                                              | insecure dev key (change before deploying) |
| `DJANGO_DEBUG`                                            | Verbose error pages                                                    | `True`                                     |
| `DJANGO_ALLOWED_HOSTS`                                    | Comma-separated allowed hostnames                                      | `127.0.0.1,localhost,testserver`           |
| `DJANGO_CSRF_TRUSTED_ORIGINS`                             | Comma-separated trusted origins for CSRF (needed behind HTTPS proxies) | empty                                      |
| `DB_ENGINE`                                               | `sqlite` (default) or `mysql`                                          | `sqlite`                                   |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection details (only read when `DB_ENGINE=mysql`)            | —                                          |
| `PLATFORM_NAME`                                           | Brand name shown across the site                                       | `RentPoint`                                |
| `PLATFORM_SERVICE_AREA`                                   | Location text shown across the site                                    | `Nsukka Urban`                             |
| `PLATFORM_COMMISSION_PERCENT`                             | Platform's cut of each paid transaction                                | `8`                                        |
| `MINIMUM_WITHDRAWAL_AMOUNT`                               | Smallest withdrawal an item owner can request                          | `1000`                                     |
| `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`              | Paystack API credentials used by the app                               | empty                                      |

---

## 5. Switching from SQLite to MySQL

The report specifies SQLite for development/testing and MySQL for
production. To switch:

```bash
# in .env
DB_ENGINE=mysql
DB_NAME=rentpoint
DB_USER=rentpoint
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Then install the MySQL driver (already listed in `requirements.txt`) and
re-run migrations against the new database:

```bash
pip install mysqlclient
python manage.py migrate
```

No application code changes are required; `config/settings.py` reads
`DB_ENGINE` and configures `DATABASES` accordingly.

---

## 6. Connecting a real payment gateway

The app is configured to use Paystack as the only payment provider.

To work with a real gateway:

1. Fill in the valid Paystack secret/public key values in `.env`.
2. The callback URL is generated dynamically from the current request, so
   there is no separate `.env` value to maintain for it.
3. No view, template, or model needs to change — `transactions/views.py`
   only ever calls `get_gateway().charge(...)`.

---

## 7. Roles and permissions, in practice

- **Anonymous visitor** — can browse `/listings/`, view item detail pages,
  read the about/how-it-works pages, and sign up.
- **Customer** (`role=customer`) — everything above, plus renting an item
  (which creates a `Transaction`), paying for it, and viewing their own
  transaction history and receipts.
- **Item owner** (`role=item_owner`) — can create, edit, and remove their
  own listings; cannot rent items (a customer account is required for
  that); can view their sales transactions, their wallet balance, and
  request withdrawals.
- **Administrator** (`is_staff=True`) — full access to `/admin/`, where
  every model can be inspected, and where withdrawal requests are approved
  or rejected via the "Approve and pay" / "Reject" bulk actions on the
  `WithdrawalRequest` admin page.

Ownership is enforced in the view layer: `listings/views.py` filters every
owner-facing queryset by `owner=request.user`, so one item owner can never
edit or delete another's listing, and `transactions/views.py` only lets a
customer see their own receipts (or the relevant item owner, or staff).

---

## 8. Verified end-to-end (what has actually been tested)

The following flows were exercised against a real SQLite database during
development, not just written and assumed to work:

- Customer sign-up → login redirect to the catalogue
- Item owner sign-up and login → redirect to "My listings"
- Browsing, searching, and filtering the public catalogue
- Viewing an item detail page
- Starting a rental, being taken to checkout, paying, and landing on a
  correctly populated receipt
- Commission and owner-earning amounts calculating correctly on payment
  (verified arithmetic: 8% commission held back, remainder credited)
- The item owner's wallet balance increasing after a customer's payment
- An item owner creating a new listing through the form (including the
  image formset)
- An item owner submitting a withdrawal request and seeing it listed as
  "Pending review"
- Administrator login and access to `/admin/`
- `python manage.py check` passing with zero issues
- All public pages returning HTTP 200

## 9. Suggested next steps before a public launch

- Keep the Paystack test/live keys aligned with the correct account and mode.
- Add automated tests (`accounts/tests.py`, `listings/tests.py`, etc. are
  present as empty files, ready to be filled in) so future changes cannot
  silently break the payment or withdrawal flow.
- Configure a production web server (Gunicorn is already in
  `requirements.txt`) behind Nginx, with `DEBUG=False` and a real
  `DJANGO_SECRET_KEY`.
- Point `DB_ENGINE` at a managed MySQL instance and run `migrate`.
- Add email notifications for payment confirmation and withdrawal status
  changes (not built yet — the report does not require it, but it is a
  natural extension of the transaction and withdrawal records that already
  exist).
