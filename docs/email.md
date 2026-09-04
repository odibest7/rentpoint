# Email Configuration Guide for RentPoint (100% Free Forever)

This guide provides step-by-step instructions to set up **100% free forever** email delivery for password resets, booking receipts, and notifications in RentPoint.

---

## Recommended Free Providers Comparison

| Provider                                         | Free Tier Allowance               | Credit Card Required? | Custom Domain Required?              | Best For                              |
| :----------------------------------------------- | :-------------------------------- | :-------------------- | :----------------------------------- | :------------------------------------ |
| **Gmail SMTP (App Password)** ⭐ _(Recommended)_ | **500 emails/day** (15,000/month) | **No**                | **No** (works with any `@gmail.com`) | Easiest setup, zero cost, zero hassle |
| **Brevo (Sendinblue)**                           | **300 emails/day** (9,000/month)  | **No**                | Optional                             | Professional transactional emails     |
| **Resend**                                       | **3,000 emails/month** (100/day)  | **No**                | Recommended                          | Modern developer API                  |

---

## Option 1: Gmail SMTP Setup (Recommended — 100% Free Forever)

You can use any standard Gmail or Google Workspace account to send up to **500 free emails per day**. Google requires an **App Password** (a dedicated 16-character security token) rather than your normal account password.

### Step-by-Step Setup:

#### Step 1: Enable 2-Step Verification on your Google Account

1. Open your browser and go to: [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Log in to the Google account you want RentPoint to send emails from (e.g., `rentpoint.notifications@gmail.com` or your personal Gmail).
3. Under **"How you sign in to Google"**, click **2-Step Verification** and follow the prompts to enable it (if not already enabled).

#### Step 2: Generate an App Password

1. In the search bar at the top of your Google Account page, type: **`App Passwords`** (or go directly to [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)).
2. Under **"App name"**, enter: `RentPoint`
3. Click **Create**.
4. Google will display a **16-character password** (e.g., `abcd efgh ijkl mnop`).
5. **Copy this 16-character code** (you will not be able to view it again once you close the popup).

#### Step 3: Add the Credentials to your RentPoint `.env`

Open your `c:\rentpoint\.env` file and add or update the following lines:

```ini
# --------------------------------------------------------------------------
# Email Configuration (Gmail SMTP - 100% Free Forever)
# --------------------------------------------------------------------------
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=RentPoint <your-email@gmail.com>
```

> [!TIP]
> Paste the 16-character App Password for `EMAIL_HOST_PASSWORD` without spaces (e.g. `abcdefghijklmnop`).

---

## Option 2: Brevo (Sendinblue) Setup (Free 300 emails/day)

If you prefer a dedicated transactional email service:

1. Create a free account at [https://www.brevo.com/](https://www.brevo.com/).
2. In the top-right menu, click your account name and select **SMTP & API**.
3. Under the **SMTP** tab, locate:
   - **SMTP Server:** `smtp-relay.brevo.com`
   - **Port:** `587`
   - **Login:** (Your Brevo account email)
   - Click **Generate a new SMTP key** and copy the generated key.
4. Add to `.env`:

```ini
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-brevo-login-email@example.com
EMAIL_HOST_PASSWORD=your-brevo-smtp-master-key
DEFAULT_FROM_EMAIL=RentPoint <your-verified-sender@example.com>
```

---

## Option 3: Local Development (Console Backend)

When testing locally without sending real emails over the internet:

- If `EMAIL_HOST` is not set in `.env` and `DJANGO_DEBUG=True`, Django automatically prints all emails directly into your **terminal console**!
- You can see the full reset link printed in the terminal immediately, click it, and test the password reset without needing any internet connection.

---

## Testing Your Email Setup

To test your email configuration from the command line:

```bash
python manage.py shell
```

Then run:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject="[RentPoint] Test Email",
    message="This is a test email confirming your RentPoint SMTP setup is working!",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["your-personal-email@gmail.com"],
    fail_silently=False,
)
```

If it returns `1`, your email was successfully sent!

---

## Troubleshooting Checklist

1. **Error: `SMTPAuthenticationError` / `Username and Password not accepted`**:
   - Make sure you are using an **App Password** and NOT your normal Google account password.
   - Make sure 2-Step Verification is turned ON for the Google account.
2. **Error: `ConnectionRefusedError` / `Timeout`**:
   - Check that `EMAIL_PORT=587` and `EMAIL_USE_TLS=True`.
   - Some hosting environments block outbound port 25, so port 587 with TLS is standard.
3. **Emails going to Spam**:
   - For Gmail SMTP, ensure `DEFAULT_FROM_EMAIL` matches your `EMAIL_HOST_USER` address.
