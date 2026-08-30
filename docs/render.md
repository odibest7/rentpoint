# Deploying RentPoint to Render

This guide explains how to deploy the Django project to Render using a production PostgreSQL database, Gunicorn, and Whitenoise.

---

## 1. Prerequisites

Before you begin, make sure you have:

- a Render account: https://render.com
- a GitHub account connected to Render
- this project pushed to a GitHub repository
- a Paystack account and valid keys for the live or test environment you want to use

You should already have the repository on GitHub and the app working locally.

---

## 2. Prepare the project for Render

### 2.1 Confirm the app is using a production-ready web server

This project already includes the Python dependencies needed for Render, including Gunicorn and Whitenoise.

Check the project root and make sure these are present:

- `requirements.txt`
- `manage.py`
- `config/settings.py`
- `config/wsgi.py`

The app is set up to run with Gunicorn via the WSGI entry point:

- `config.wsgi:application`

### 2.2 Make sure static files are handled properly

The project already uses WhiteNoise when `DEBUG=False` in `config/settings.py`.

That means Render should work with the app as long as you set:

- `DJANGO_DEBUG=False`

Render will serve the static files after collectstatic runs.

### 2.3 Recommended Python version

If Render does not auto-detect your Python version correctly, add a `runtime.txt` file in the project root.

Example content:

```txt
python-3.12.5
```

Use the Python version that matches your local environment and your installed packages.

---

## 3. Prepare your production environment variables

Create a production `.env` locally or at least prepare the values you will paste into Render.

Use the following variables for the deployed app.

### Required Django variables

```env
DJANGO_SECRET_KEY=your-very-long-random-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=rentpoint.onrender.com,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://rentpoint.onrender.com
```

Replace `rentpoint` with your actual Render service name.

If you plan to use a custom domain, add it as well:

```env
DJANGO_ALLOWED_HOSTS=rentpoint.onrender.com,yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://rentpoint.onrender.com,https://yourdomain.com
```

### Required database variables

Render can provide a managed PostgreSQL database, and this project already supports Postgres.

Use the direct connection string provided by Render for the database:

```env
DB_ENGINE=postgres
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

You can also use separate variables instead of `DATABASE_URL`, but the `DATABASE_URL` method is the simplest on Render.

### Business variables

```env
PLATFORM_NAME=RentPoint
PLATFORM_SERVICE_AREA=Nsukka Urban
PLATFORM_COMMISSION_PERCENT=8
MINIMUM_WITHDRAWAL_AMOUNT=1000
```

### Paystack variables

```env
PAYSTACK_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxx
```

Important:

- use test keys for testing
- use live keys only when you are ready to accept real payments
- the secret and public key must belong to the same Paystack account and mode

---

## 4. Create a PostgreSQL database on Render

### Step-by-step

1. Log in to Render.
2. Click New +
3. Select PostgreSQL
4. Choose a name such as `rentpoint-db`
5. Select the region closest to your users
6. Keep the database plan suitable for your current stage
7. Create the database
8. Copy the connection string after it is created

Render will give you something like:

```txt
postgres://username:password@host:5432/dbname
```

Use that value for `DATABASE_URL` in Render environment variables.

---

## 5. Create the web service

### Step-by-step

1. Go to your Render dashboard
2. Click New +
3. Select Web Service
4. Connect your GitHub repository
5. Choose the repository for RentPoint
6. Set the service name, for example:

```txt
rentpoint
```

### Build & start settings

Set the following values:

- Root Directory: leave empty unless your repo has multiple apps
- Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

- Start Command:

```bash
gunicorn config.wsgi:application
```

Render will use the application entry point from:

- `config/wsgi.py`

### Auto-Deploy

You may enable automatic deploys from the main branch if you want.

---

## 6. Add environment variables in Render

Inside your Render web service, open the Environment tab and add the full list of production variables:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=rentpoint.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://rentpoint.onrender.com
DB_ENGINE=postgres
DATABASE_URL=postgresql://...from-render-db...
PLATFORM_NAME=RentPoint
PLATFORM_SERVICE_AREA=Nsukka Urban
PLATFORM_COMMISSION_PERCENT=8
MINIMUM_WITHDRAWAL_AMOUNT=1000
PAYSTACK_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxxxxx
PAYSTACK_PUBLIC_KEY=pk_live_xxxxxxxxxxxxxxxxxxxxx
```

If you have a custom domain, add it to the allowed hosts and trusted origins as well.

---

## 7. Run database migrations after deployment

Render does not automatically run Django migrations unless you create a deploy command that does it.

There are two common approaches:

### Option A: Run once after deployment from the Render shell

1. Open your Render service
2. Open the Shell tab
3. Run:

```bash
python manage.py migrate
```

### Option B: Set a one-time custom deploy command

Use this in a deploy command or shell before launching the app:

```bash
python manage.py migrate && python manage.py collectstatic --noinput
```

For most setups, it is safe to run migration once from the shell before the first live launch.

---

## 8. Create a superuser on Render

If the app needs an admin login, open Render Shell and run:

```bash
python manage.py createsuperuser
```

Then follow the prompts to create the admin account.

---

## 9. Check the app is live

After deployment succeeds, Render will provide a public URL such as:

```txt
https://rentpoint.onrender.com
```

Open the URL in the browser.

Test these basic flows:

- homepage loads
- login/signup works
- item listing pages load
- transaction checkout starts without crashing
- payment checkout opens the Paystack modal
- verification works with valid Paystack keys
- receipt renders after a successful payment

---

## 10. Common deployment issues and fixes

### 10.1 Static files do not load

Make sure:

- `DJANGO_DEBUG=False`
- `whitenoise` is installed
- `collectstatic` runs during build
- `STATIC_ROOT` is configured in `config/settings.py`

### 10.2 App crashes on startup

Check Render logs and review:

- missing environment variables
- invalid database connection string
- syntax errors in settings or app files
- missing Python dependency

### 10.3 Payment verification fails on Render

This is usually not a Render problem. It is usually a Paystack key mismatch or mode mismatch.

Check:

- same project/account for public and secret keys
- same test/live mode for both keys
- correct values in Render env vars
- valid Paystack keys in the correct environment

### 10.4 CSRF or host errors

If you see a host or CSRF failure, check:

```env
DJANGO_ALLOWED_HOSTS=rentpoint.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://rentpoint.onrender.com
```

and verify the domain matches your actual deployed URL.

---

## 11. Recommended final production setup

For a stable live deployment, the final setup should be:

- Render Web Service for Django app
- Render PostgreSQL database
- `DJANGO_DEBUG=False`
- `DB_ENGINE=postgres`
- `DATABASE_URL` from Render Postgres
- `PAYSTACK_SECRET_KEY` and `PAYSTACK_PUBLIC_KEY` from the correct live Paystack account
- custom domain configured if needed

---

## 12. Summary

The deployment flow is:

1. push repo to GitHub
2. create Postgres database on Render
3. create web service on Render
4. set build command and start command
5. add environment variables
6. run migrations
7. create admin user
8. deploy and test the app

That is the full Render deployment flow for this project.

---

## 13. Example final Render setup

Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start command:

```bash
gunicorn config.wsgi:application
```

Environment variables:

```env
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=rentpoint.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://rentpoint.onrender.com
DB_ENGINE=postgres
DATABASE_URL=postgresql://... 
PLATFORM_NAME=RentPoint
PLATFORM_SERVICE_AREA=Nsukka Urban
PLATFORM_COMMISSION_PERCENT=8
MINIMUM_WITHDRAWAL_AMOUNT=1000
PAYSTACK_SECRET_KEY=sk_live_...
PAYSTACK_PUBLIC_KEY=pk_live_...
```

Use the exact values from your Render database and Paystack dashboard.
