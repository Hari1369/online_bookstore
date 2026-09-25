# 📚 Online Bookstore

A full-stack **Django** web application for browsing, purchasing, and managing books, with a token-authenticated **REST API** (Django REST Framework) for auth, book catalog, cart, and order management, alongside server-rendered pages for the storefront and an admin/staff panel.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Environment Variables (.env)](#environment-variables-env)
- [Database Setup](#database-setup)
- [Running the Project](#running-the-project)
- [Creating an Admin (Superuser) Account](#creating-an-admin-superuser-account)
- [API Documentation](#api-documentation)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)

---

## Features

- 🔐 User signup / login / logout with Django sessions **and** DRF Token authentication
- 📖 Book catalog with categories, stock (copies), images and downloadable PDFs
- 🛒 Cart management (add / update / remove items)
- 📦 Order placement (cart → order, with stock validation) and order status tracking
- 🧑‍💼 Admin/staff pages for managing users, categories, and books
- ✉️ Password-reset flow via email (Gmail SMTP)

## Tech Stack

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| Backend        | Django 6.1, Django REST Framework 3.18       |
| Database       | PostgreSQL (via `psycopg`)                   |
| Auth           | Django Auth (web) + DRF Token Auth (API)     |
| Frontend       | Django Templates, vanilla JS, CSS             |
| Media/Files    | Django `ImageField` / `FileField` (local disk)|
| Env management | `python-dotenv`                              |

## Project Structure

```
online_bookstore/
├── manage.py
├── requirements.txt
├── .env                          # local secrets (not committed)
├── online_bookstore/             # project settings package
│   ├── settings.py
│   ├── urls.py                   # root URL conf → includes api/, members/, management_system/
│   ├── wsgi.py / asgi.py
├── api/                          # REST API app (DRF)
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── members/                      # auth: signup, login, logout, password reset, user admin
├── management_system/            # storefront: books, categories, cart, orders (models + web views)
├── static/                       # css, js, csv
└── media/                        # uploaded book images & PDFs
```

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 13+** running locally (or reachable) with a database created
- `pip` / `venv`
- A Gmail account with an **App Password** if you want real password-reset emails (optional — see below)

## Setup & Installation

```bash
# 1. Clone / unzip the project, then move into the project root (the folder with manage.py)
cd online_bookstore

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Environment Variables (.env)

Create a `.env` file in the **project root** (same folder as `manage.py`). This project only reads two environment variables today, both for outgoing email (password-reset):

```env
# .env
EMAIL_USER=your_gmail_address@gmail.com
EMAIL_APP_PASSWORD="your 16 char app password"
```

| Variable             | Required? | Purpose                                                                 |
|----------------------|-----------|--------------------------------------------------------------------------|
| `EMAIL_USER`         | No        | Gmail address used to send password-reset emails via SMTP               |
| `EMAIL_APP_PASSWORD` | No        | Gmail **App Password** (not your normal password) for SMTP auth         |

If either variable is missing, `settings.py` automatically falls back to Django's **console email backend** — reset emails just print to your terminal instead of sending, so the app still runs fine without a `.env` file.

To generate a Gmail App Password: enable 2-Step Verification on the Google account → **Google Account → Security → App passwords** → generate one for "Mail".

> ⚠️ **Important — this project does not call `load_dotenv()` automatically.** `python-dotenv` is listed in `requirements.txt` but `settings.py` reads variables with plain `os.environ.get(...)`, so a `.env` file sitting on disk is **not** picked up by itself. Use one of these to actually load it:
>
> **Option A (recommended, no code change) — use the dotenv CLI:**
> ```bash
> dotenv run -- python manage.py runserver
> ```
> **Option B — export the vars manually in your shell before running:**
> ```bash
> export EMAIL_USER=your_gmail_address@gmail.com
> export EMAIL_APP_PASSWORD="your app password"
> python manage.py runserver
> ```
> **Option C — wire it up in code (one-time change):** add `from dotenv import load_dotenv; load_dotenv()` near the top of `online_bookstore/settings.py`, before the `os.environ.get(...)` calls. After that, a plain `python manage.py runserver` will pick up `.env` automatically.

### Other settings currently hardcoded in `settings.py` (not env-driven)

These are **not** read from `.env` in the current code — they're fixed values in `settings.py`. Edit them directly there if your local setup differs:

- `SECRET_KEY` — Django secret key (dev-only value checked into the repo)
- `DEBUG = True`
- `DATABASES` — PostgreSQL connection (see below)

## Database Setup

The project uses **PostgreSQL** with these settings currently hardcoded in `online_bookstore/settings.py`:

| Setting  | Value                     |
|----------|---------------------------|
| Engine   | `django.db.backends.postgresql` |
| Name     | `dummy_online_bookstore`  |
| User     | `admin`                   |
| Password | `admin`                   |
| Host     | `127.0.0.1`                |
| Port     | `5432`                     |

Create the matching role and database locally (adjust if you change `settings.py`):

```sql
-- run in psql
CREATE USER admin WITH PASSWORD 'admin';
CREATE DATABASE dummy_online_bookstore OWNER admin;
```

Then apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Running the Project

```bash
python manage.py runserver
```

- Storefront: `http://127.0.0.1:8000/index_page/`
- Login / Signup: `http://127.0.0.1:8000/`
- Django admin: `http://127.0.0.1:8000/admin/`
- REST API base: `http://127.0.0.1:8000/api/`

Static/media files are served automatically in `DEBUG=True` mode.

## Creating an Admin (Superuser) Account

Admin-only API actions (creating/editing/deleting books, updating order status, deleting orders) require `is_superuser = True`.

```bash
python manage.py createsuperuser
```

## API Documentation

Full endpoint-by-endpoint documentation (auth, books, cart, orders — with sample request/response bodies and status codes) is provided as an importable **Postman collection**: `postman_collection.json`.

**To use it:**
1. Open Postman → **Import** → select `postman_collection.json`.
2. Set the collection variable `base_url` (defaults to `http://127.0.0.1:8000/api`).
3. Run **Auth → Signup** or **Auth → Login** first — the collection script automatically saves the returned token into the `{{token}}` variable, which every other request uses via `Authorization: Token {{token}}`.

### Quick reference

All endpoints are prefixed with `/api/` and (except signup/login) require the header:
`Authorization: Token <your_token>`

| Method | Endpoint                | Auth        | Description                                  |
|--------|--------------------------|-------------|-----------------------------------------------|
| POST   | `/auth/signup/`          | Public      | Create an account, returns a token            |
| POST   | `/auth/login/`           | Public      | Log in, returns a token                       |
| POST   | `/auth/logout/`          | Token       | Invalidate current token                      |
| GET    | `/auth/me/`              | Token       | Current user's profile                        |
| GET    | `/books/`                | Token       | List all active books                         |
| POST   | `/books/`                | Admin       | Create a book                                 |
| GET    | `/books/<id>/`           | Token       | Book detail                                   |
| PUT    | `/books/<id>/`           | Admin       | Update a book                                 |
| DELETE | `/books/<id>/`           | Admin       | Soft-delete (deactivate) a book               |
| GET    | `/cart/`                 | Token       | Get current user's cart                       |
| POST   | `/cart/`                 | Token       | Add a book to the cart                        |
| PUT    | `/cart/<item_id>/`       | Token       | Update quantity of a cart item                |
| DELETE | `/cart/<item_id>/`       | Token       | Remove a cart item                            |
| GET    | `/orders/`               | Token       | List current user's orders                    |
| POST   | `/orders/`               | Token       | Place an order from the current cart          |
| GET    | `/orders/<id>/`          | Token       | Order detail                                  |
| PUT    | `/orders/<id>/`          | Admin       | Update order status                           |
| DELETE | `/orders/<id>/`          | Admin       | Delete an order                               |

### Standard HTTP status codes used

| Code | Meaning                              |
|------|----------------------------------------|
| 200  | Successful GET / PUT                  |
| 201  | Successfully created                  |
| 204  | Successful request, no response body  |
| 400  | Bad request / validation error        |
| 401  | Authentication required / invalid token |
| 403  | Permission denied                     |
| 404  | Resource not found                    |
| 500  | Server error                          |

See `postman_collection.json` for full request/response examples for every endpoint.

## Security Notes

- **Never commit `.env` or real secrets.** Add `.env` to `.gitignore` if it isn't already.
- The Gmail **App Password** is a credential — if one was ever committed or shared, revoke/regenerate it from your Google Account's App Passwords page.
- `SECRET_KEY` in `settings.py` and the Postgres `admin`/`admin` credentials are development-only placeholders — replace them with strong, unique values (ideally loaded from environment variables) before deploying anywhere public, and set `DEBUG = False` in production.

## Troubleshooting

| Problem                                   | Fix                                                                 |
|--------------------------------------------|----------------------------------------------------------------------|
| `psycopg.OperationalError` on startup      | Postgres isn't running, or the DB/user in `settings.py` don't exist — see [Database Setup](#database-setup) |
| Password-reset emails not arriving         | `.env` values aren't loaded (see the dotenv note above) or the App Password is wrong/expired |
| `401 Unauthorized` on API calls            | Missing/expired `Authorization: Token <token>` header — log in again via `/api/auth/login/` |
| `403 Forbidden` on book/order admin actions| The logged-in user isn't a superuser — see [Creating an Admin Account](#creating-an-admin-superuser-account) |
