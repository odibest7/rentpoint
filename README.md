# RentPoint

An automated, web-based property and rental management system built for
Nsukka Urban: item owners list rentable items and property, customers
browse and pay for rentals electronically, and every payment produces a
permanent, transparent transaction record.

Built with Python, Django, HTML, CSS, and JavaScript, with SQLite for
development and MySQL for production, matching the technology plan in the
accompanying project report.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit DJANGO_SECRET_KEY at minimum
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data   # optional: adds sample categories & listings
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Documentation

- **[docs/RUNBOOK.md](docs/RUNBOOK.md)**: Full architecture, environment
  variables, how to switch to MySQL, how to connect a real payment
  gateway, roles and permissions, and what has been tested end to end.
  Start here.
- **[docs/DESIGN.md](docs/DESIGN.md)**: The visual design plan and the
  reasoning behind every colour, font, and layout decision.

## Project structure

```
accounts/       Custom User model (customer / item owner roles), auth, profile
listings/       Categories, items/properties, owner listing management, public catalogue
transactions/   Rental checkout, payment gateway abstraction, receipts, transaction history
wallet/         Item owner earnings balance and withdrawal requests
core/           Home page, about, how-it-works, dashboard routing
templates/      Shared base template, navbar, footer
static/         Hand-written CSS design system and vanilla JavaScript
docs/           RUNBOOK.md and DESIGN.md
```
