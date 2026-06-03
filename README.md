# SMBot — Facebook Marketplace Automation
## Browser Engine: Playwright (no ChromeDriver, no version mismatch)

---

## Install

```bash
pip install -r requirements.txt
playwright install chromium
```

## Setup & Run

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open browser: http://127.0.0.1:8000

---

## Workflow

1. `/form/` — Fill listing data (titles, price, images, locations, tags) → Save
2. `/automation/` — Enter FB credentials → Select type → Set count → Start Bot
3. Bot: Login → Fill drafts → Open tabs → Click Next → Publish → Close slowly

---

## Pages

| URL | Page |
|-----|------|
| `/` | Landing page |
| `/accounts/login/` | Login |
| `/accounts/signup/` | Sign Up |
| `/dashboard/` | Dashboard (stats, accounts, schedules) |
| `/form/` | Form Filler |
| `/automation/` | Automation Dashboard |
| `/bulk/` | Bulk Upload (CSV/XLSX) |
| `/admin/` | Django Admin |

---

## Automation Types

| Type | Status |
|------|--------|
| Draft Publisher | ✅ Full Playwright flow |
| New Accounts – Faster | ✅ Routes to draft publisher |
| New Accounts – Slower | ✅ Routes to draft publisher |
| Old Accounts – No Limits | ✅ Routes to draft publisher |
| Relist Facebook Ads | ✅ Playwright |
| Renew Facebook Listings | ✅ Playwright |
| Delete Duplicate Listings | ✅ Playwright |
| Delete All Listings | ✅ Playwright |
| Draft Delete Automation | ✅ Playwright |
| Open Custom Link | ✅ Playwright |

---

## Why Playwright (not Selenium)

- No ChromeDriver download — no version mismatch errors
- Built-in anti-detection (navigator.webdriver patched automatically)
- Faster, more reliable selectors
- Native multi-tab/context support
- Works on Python 3.10, 3.11, 3.12, 3.13

---

## Requirements

- Windows 10/11
- Python 3.10+
- Google Chrome installed (Playwright uses its own Chromium)
"# bot" 
"# bot" 
"# bot" 
"# bot" 
"# bot" 
"# bot" 
"# bot" 
