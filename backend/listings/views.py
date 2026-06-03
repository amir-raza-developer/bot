# ==========================================
# SMBot - listings/views.py  (FIXED - Fast & Fully Automatic)
# Browser: Playwright only — zero Selenium
# ==========================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from .models import Listing, ListingTitle, ListingLocation, ListingImage, FacebookCredential
import json, os, time, random

# ==========================================
# UTILITIES
# ==========================================

def format_price(value):
    try:
        if value is None:
            return ""
        num = float(value)
        if num.is_integer():
            return str(int(num))
        return str(num).rstrip('0').rstrip('.')
    except Exception:
        return str(value)


def create_browser():
    """Launch Playwright Chromium. Returns (pw, browser, context, page)."""
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=False,
        args=[
            "--start-maximized",
            "--disable-notifications",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ]
    )
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        timezone_id="America/New_York",
    )
    # Stealth: hide automation signals on every page
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
        window.chrome = {runtime: {}};
    """)
    page = context.new_page()
    return pw, browser, context, page


# ==========================================
# LOGIN — Fast, fully automatic, no 3-min wait
# ==========================================

def pw_login(page, email, password):
    """
    Login to Facebook fully automatically.
    - Fills email + password with human-like typing
    - Clicks login button immediately
    - Polls URL every 1s (not 3s) for up to 60s
    - Pauses only when captcha/checkpoint detected
    Returns True on success, False on failure.
    """
    print("   🌐 Navigating to Facebook login...")
    page.goto("https://www.facebook.com/login", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)

    # Dismiss cookie/consent banners quickly
    for sel in [
        "[data-cookiebanner='accept_button']",
        "[aria-label='Allow all cookies']",
        "[aria-label='Accept all']",
        "button:has-text('Accept All')",
        "button:has-text('Accept')",
        "button:has-text('Allow')",
        "button:has-text('OK')",
    ]:
        try:
            page.click(sel, timeout=1000)
            page.wait_for_timeout(500)
            print("   ✅ Dismissed cookie banner")
            break
        except Exception:
            pass

    # ---- Fill Email ----
    email_sel = None
    for sel in ["#email", "input[name='email']", "input[type='email']",
                "input[placeholder*='email' i]", "input[placeholder*='phone' i]"]:
        try:
            page.wait_for_selector(sel, state="visible", timeout=5000)
            email_sel = sel
            break
        except Exception:
            continue

    if not email_sel:
        page.screenshot(path="login_debug.png")
        print("   ❌ Email field not found! Screenshot: login_debug.png")
        return False

    # Fast fill: use fill() then simulate keystrokes naturally
    page.fill(email_sel, "")
    page.type(email_sel, email, delay=random.randint(60, 110))
    page.wait_for_timeout(random.randint(400, 700))

    # ---- Fill Password ----
    pass_sel = None
    for sel in ["#pass", "input[name='pass']", "input[type='password']"]:
        try:
            page.wait_for_selector(sel, state="visible", timeout=5000)
            pass_sel = sel
            break
        except Exception:
            continue

    if not pass_sel:
        print("   ❌ Password field not found!")
        return False

    page.fill(pass_sel, "")
    page.type(pass_sel, password, delay=random.randint(60, 110))
    page.wait_for_timeout(random.randint(500, 900))

    # ---- Click Login Button (immediately, not after another delay) ----
    login_clicked = False
    for btn_sel in [
        "[name='login']",
        "button[type='submit']",
        "button:has-text('Log in')",
        "button:has-text('Log In')",
        "[data-testid='royal_login_button']",
    ]:
        try:
            page.click(btn_sel, timeout=3000)
            login_clicked = True
            print("   ✅ Login button clicked!")
            break
        except Exception:
            continue

    if not login_clicked:
        # Last resort: press Enter on password field
        page.focus(pass_sel)
        page.keyboard.press("Enter")
        login_clicked = True
        print("   ✅ Login submitted via Enter key")

    # ---- Wait for redirect (fast polling, 1s intervals, max 60s) ----
    print("   ⏳ Waiting for login redirect...")
    for attempt in range(60):
        page.wait_for_timeout(1000)
        url = page.url.lower()

        # Successful login — URL is no longer the login page
        if "facebook.com" in url and "login" not in url and "signup" not in url:
            print(f"   ✅ Login successful! ({url[:60]})")
            return True

        # Security checkpoint — pause and let user solve it
        if any(x in url for x in ["checkpoint", "captcha", "two_step",
                                   "login/device", "confirmemail", "recover"]):
            print(f"   🛑 Security check at attempt {attempt+1} — please solve it in the browser...")
            page.wait_for_timeout(8000)  # Check every 8s during captcha
            continue

        # Still on login page — check for error message
        if "login" in url:
            for err_sel in [
                "[id*='error']",
                "//div[@role='alert']",
                "//*[contains(@class,'error')]",
                "//*[contains(text(),'wrong')]",
                "//*[contains(text(),'incorrect')]",
            ]:
                try:
                    el = page.locator(err_sel).first
                    if el.is_visible():
                        print(f"   ❌ Login error detected: wrong credentials?")
                        return False
                except Exception:
                    pass

        if attempt % 10 == 9:
            print(f"   ⏳ Still waiting... ({attempt+1}/60s) URL: {url[:50]}")

    print("   ❌ Login timeout after 60 seconds")
    return False


# ==========================================
# DJANGO API VIEWS (no browser)
# ==========================================

@csrf_exempt
def save_listing(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        listing_id    = request.POST.get("listing_id")
        new_images    = request.FILES.getlist("images")
        existing_urls = request.POST.getlist("existing_images")

        if not new_images and not existing_urls:
            return JsonResponse({"success": False, "error": "At least one image is required!"}, status=400)

        titles       = request.POST.getlist("titles")
        locations    = request.POST.getlist("locations")
        price        = request.POST.get("price") or None
        description  = request.POST.get("description") or None
        category     = request.POST.get("category") or ""
        condition    = request.POST.get("condition") or ""
        tags         = request.POST.get("tags") or None
        availability = request.POST.get("availability") or None
        delivery     = request.POST.get("delivery") or None
        tabs_count   = int(request.POST.get("tabs") or 1)

        if listing_id:
            try:
                listing = Listing.objects.get(id=listing_id)
                listing.category, listing.condition, listing.price = category, condition, price
                listing.description, listing.tags, listing.availability = description, tags, availability
                listing.delivery, listing.tabs = delivery, tabs_count
                listing.save()
                listing.titles.all().delete()
                listing.locations.all().delete()
                kept = [u.split('/')[-1] for u in existing_urls]
                for img in listing.images.all():
                    if img.image.name.split('/')[-1] not in kept:
                        img.delete()
            except Listing.DoesNotExist:
                return JsonResponse({"success": False, "error": "Listing not found!"}, status=404)
        else:
            listing = Listing.objects.create(
                category=category, condition=condition, price=price,
                description=description, tags=tags, availability=availability,
                delivery=delivery, tabs=tabs_count
            )

        for t in titles:
            if t.strip():
                ListingTitle.objects.create(listing=listing, title=t.strip())
        for loc in locations:
            if loc.strip():
                ListingLocation.objects.create(listing=listing, location=loc.strip())
        for img_file in new_images:
            ListingImage.objects.create(listing=listing, image=img_file)

        image_urls = [img.image.url for img in listing.images.all().order_by('id')]
        return JsonResponse({"success": True, "message": "✅ Listing saved!",
                             "listing_id": listing.id, "image_urls": image_urls})
    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def get_latest_listing(request):
    try:
        listing = Listing.objects.latest("id")
        return JsonResponse({"success": True, "listing": {
            "id": listing.id,
            "category": listing.category,
            "condition": listing.condition,
            "price": str(listing.price) if listing.price else "",
            "description": listing.description or "",
            "tags": listing.tags or "",
            "availability": listing.availability or "",
            "delivery": listing.delivery or "",
            "tabs": listing.tabs,
            "titles": [t.title for t in listing.titles.all()],
            "locations": [l.location for l in listing.locations.all()],
            "images": [img.image.url for img in listing.images.all()],
        }})
    except Listing.DoesNotExist:
        return JsonResponse({"success": False, "error": "No listings found"})


@csrf_exempt
def save_credentials(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=400)
    try:
        data     = json.loads(request.body.decode("utf-8"))
        email    = (data.get("email") or data.get("phone") or "").strip()
        password = (data.get("password") or "").strip()
        if not email or not password:
            return JsonResponse({"success": False, "error": "Email and password required."}, status=400)
        FacebookCredential.objects.all().delete()
        FacebookCredential.objects.create(phone_or_email=email, password=password)
        return JsonResponse({"success": True, "message": "Credentials saved!"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def get_credentials(request):
    try:
        cred = FacebookCredential.objects.last()
        if cred:
            return JsonResponse({"success": True,
                                 "phone_or_email": cred.phone_or_email,
                                 "password": cred.password})
        return JsonResponse({"success": False, "error": "No credentials found."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
def debug_data(request):
    creds    = FacebookCredential.objects.last()
    listings = Listing.objects.all()
    data = {
        "credentials": {"exists": bool(creds), "email": creds.phone_or_email if creds else None},
        "listings_count": listings.count(),
        "listings": [],
        "media_root": str(settings.MEDIA_ROOT),
        "media_url": settings.MEDIA_URL,
    }
    for listing in listings:
        images_info = []
        for img in listing.images.all():
            abs_path = os.path.join(settings.MEDIA_ROOT, str(img.image))
            images_info.append({
                "filename": str(img.image),
                "absolute_path": abs_path,
                "exists": os.path.exists(abs_path),
                "size": os.path.getsize(abs_path) if os.path.exists(abs_path) else 0,
            })
        data["listings"].append({
            "id": listing.id,
            "titles": [t.title for t in listing.titles.all()],
            "images": images_info,
            "price": format_price(listing.price) if listing.price else "No price",
            "locations": [l.location for l in listing.locations.all()],
            "description": (listing.description[:50] + "...") if listing.description and len(listing.description) > 50 else listing.description,
        })
    return JsonResponse(data)


# ==========================================
# FAST FORM-FILL HELPERS
# ==========================================

def _try_click(page, selectors, timeout=2000):
    """Try clicking each selector, return True on first success."""
    for sel in selectors:
        try:
            page.click(sel, timeout=timeout)
            return True
        except Exception:
            pass
    return False


def _try_fill(page, selectors, value, timeout=3000):
    """Find first visible input and fill it. Returns True on success."""
    for sel in selectors:
        try:
            page.wait_for_selector(sel, state="visible", timeout=timeout)
            page.fill(sel, str(value))
            return True
        except Exception:
            pass
    return False


def _select_dropdown(page, label, value):
    """Open a dropdown by label text then click the target option."""
    # Open dropdown
    opened = _try_click(page, [
        f"//label[text()='{label}']/following::div[@role='button'][1]",
        f"//label[contains(text(),'{label}')]/following::div[@role='button'][1]",
        f"//span[text()='{label}']/following::div[@role='button'][1]",
        f"//div[@aria-label='{label}']",
        f"//div[@aria-label='{label} dropdown']",
    ], timeout=2000)

    if not opened:
        print(f"      ⚠️ {label} dropdown not opened")
        return False

    page.wait_for_timeout(600)

    # Click option
    clicked = _try_click(page, [
        f"//span[text()='{value}']",
        f"//div[@role='option']//span[text()='{value}']",
        f"//div[@role='option'][normalize-space()='{value}']",
        f"//div[@role='option'][contains(.,'{value}')]",
        f"//li[@role='option'][contains(.,'{value}')]",
    ], timeout=2000)

    if clicked:
        page.wait_for_timeout(300)
        print(f"      ✅ {label}: {value}")
    else:
        print(f"      ⚠️ {label} option '{value}' not found")
    return clicked


def pw_fill_listing_form(page, listing, title, location, image_path):
    """
    Fill one complete FB Marketplace listing form — fast, no unnecessary waits.
    Returns True if draft was saved.
    """

    # ── 1. IMAGE ──────────────────────────────────────────────────────────────
    print("   1️⃣  Uploading image...")
    try:
        page.wait_for_selector("input[type='file']", state="attached", timeout=8000)
        page.set_input_files("input[type='file']", image_path)
        page.wait_for_timeout(1500)
        print("      ✅ Image uploaded")
    except Exception as e:
        print(f"      ⚠️ Image upload error: {e}")

    # ── 2. TITLE ──────────────────────────────────────────────────────────────
    print("   2️⃣  Filling title...")
    filled = _try_fill(page, [
        "input[placeholder='Title']",
        "input[aria-label='Title']",
        "input[name='title']",
        "//label[text()='Title']/following::input[1]",
    ], title, timeout=4000)
    if filled:
        print(f"      ✅ Title: {title[:50]}")
    else:
        print("      ⚠️ Title field not found")

    # ── 3. PRICE ──────────────────────────────────────────────────────────────
    print("   3️⃣  Filling price...")
    price_str = format_price(listing.price)
    filled = _try_fill(page, [
        "input[placeholder='Price']",
        "input[aria-label='Price']",
        "input[name='price']",
        "//label[text()='Price']/following::input[1]",
    ], price_str, timeout=3000)
    if filled:
        print(f"      ✅ Price: {price_str}")
    else:
        print("      ⚠️ Price field not found")

    # ── 4. CATEGORY ───────────────────────────────────────────────────────────
    if listing.category:
        print(f"   4️⃣  Category: {listing.category}...")
        _select_dropdown(page, "Category", listing.category)

    # ── 5. CONDITION ──────────────────────────────────────────────────────────
    if listing.condition:
        print(f"   5️⃣  Condition: {listing.condition}...")
        _select_dropdown(page, "Condition", listing.condition)

    # ── 6. DESCRIPTION ────────────────────────────────────────────────────────
    if listing.description:
        print("   6️⃣  Filling description...")
        filled = _try_fill(page, [
            "textarea[placeholder='Description']",
            "textarea[aria-label*='Description']",
            "textarea[placeholder*='Describe']",
            "//textarea[@placeholder='Description']",
        ], listing.description, timeout=3000)
        if filled:
            print("      ✅ Description filled")
        else:
            print("      ⚠️ Description field not found")

    # ── 7. AVAILABILITY ───────────────────────────────────────────────────────
    if listing.availability:
        print(f"   7️⃣  Availability: {listing.availability}...")
        _select_dropdown(page, "Availability", listing.availability)

    # ── 8. TAGS ───────────────────────────────────────────────────────────────
    if listing.tags:
        print("   8️⃣  Adding tags...")
        try:
            tags_list = [t.strip() for t in listing.tags.split(",") if t.strip()]
            tag_sel = None
            for sel in [
                "//span[contains(text(),'Product tags')]/following::input[1]",
                "//span[contains(text(),'Product tags')]/following::div[@contenteditable='true'][1]",
                "//label[contains(text(),'tags')]/following::input[1]",
            ]:
                try:
                    page.wait_for_selector(sel, state="visible", timeout=2000)
                    tag_sel = sel
                    break
                except Exception:
                    pass

            if tag_sel:
                for tag in tags_list:
                    page.click(tag_sel)
                    page.wait_for_timeout(200)
                    page.type(tag_sel, tag, delay=50)
                    page.wait_for_timeout(400)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(400)
                print(f"      ✅ Added {len(tags_list)} tags")
            else:
                print("      ⚠️ Tags input not found, skipping")
        except Exception as e:
            print(f"      ⚠️ Tags error: {e}")

    # ── 9. LOCATION ───────────────────────────────────────────────────────────
    print(f"   9️⃣  Location: {location}...")
    try:
        loc_sel = None
        for sel in [
            "input[placeholder*='Location']",
            "input[aria-label*='Location']",
            "//label[text()='Location']/following::input[1]",
            "//input[@id and contains(@aria-label,'ocation')]",
        ]:
            try:
                page.wait_for_selector(sel, state="visible", timeout=2000)
                loc_sel = sel
                break
            except Exception:
                pass

        if loc_sel:
            page.click(loc_sel)
            page.wait_for_timeout(200)
            page.fill(loc_sel, "")
            page.type(loc_sel, location, delay=50)
            page.wait_for_timeout(1500)
            # Select first suggestion from dropdown
            for sug_sel in [
                "//ul[@role='listbox']/li[1]",
                "[role='listbox'] [role='option']:first-child",
                "[role='option']:first-child",
            ]:
                try:
                    page.click(sug_sel, timeout=2000)
                    break
                except Exception:
                    pass
            else:
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(300)
                page.keyboard.press("Enter")
            page.wait_for_timeout(300)
            print(f"      ✅ Location: {location}")
        else:
            print("      ⚠️ Location field not found")
    except Exception as e:
        print(f"      ⚠️ Location error: {e}")

    # ── 10. SAVE DRAFT ────────────────────────────────────────────────────────
    print("   🔟 Saving draft...")
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(1000)

    draft_selectors = [
        "//span[text()='Save draft']",
        "//div[@aria-label='Save draft']",
        "//div[text()='Save draft']",
        "//button[contains(text(),'Save draft')]",
        "//div[@role='button'][.//span[contains(text(),'Save draft')]]",
        "//div[@role='button'][.//span[contains(text(),'draft')]]",
    ]

    # Two passes: direct + after scrolling
    for scroll_y in [0, 300, 600, 0]:
        page.evaluate(f"window.scrollTo(0,{scroll_y})")
        page.wait_for_timeout(600)
        for sel in draft_selectors:
            try:
                page.click(sel, timeout=2500)
                page.wait_for_timeout(2000)
                print("      ✅ Draft saved!")
                return True
            except Exception:
                pass

    print("      ❌ Save draft button not found")
    return False


def pw_open_drafts(page, context):
    """Navigate to selling page, collect all draft URLs, open each in a new tab."""
    print("\n📂 Opening drafts...")
    page.goto("https://www.facebook.com/marketplace/you/selling",
              wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # Scroll to load all drafts
    for _ in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(500)

    # Collect draft URLs
    draft_urls = []
    for sel in [
        "a[aria-label='Continue'][role='link']",
        "//a[@role='link'][.//span[text()='Continue']]",
    ]:
        links = page.locator(sel).all()
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and "/marketplace/edit/" in href and href not in draft_urls:
                    draft_urls.append(href)
            except Exception:
                pass
        if draft_urls:
            break

    if not draft_urls:
        print("   ❌ No draft URLs found!")
        try:
            page.screenshot(path="no_drafts_found.png")
        except Exception:
            pass
        return []

    print(f"   ✅ Found {len(draft_urls)} draft(s)")

    # Open each draft in a fresh tab
    draft_pages = []
    for idx, url in enumerate(draft_urls):
        try:
            new_page = context.new_page()
            new_page.goto(url, wait_until="domcontentloaded", timeout=30000)
            new_page.wait_for_timeout(1500)
            draft_pages.append(new_page)
            print(f"   ✅ Draft {idx+1}/{len(draft_urls)} opened")
        except Exception as e:
            print(f"   ⚠️ Could not open draft {idx+1}: {e}")

    return draft_pages


# ==========================================
# MAIN BOT — start_publishing
# ==========================================

@csrf_exempt
def start_publishing(request):
    """Main entry point — routes to correct automation type."""
    try:
        data           = json.loads(request.body.decode("utf-8"))
        automation_type = data.get("automation_type", "draft_publisher")
    except Exception:
        automation_type = "draft_publisher"

    if automation_type == "renew_facebook_listings":
        return run_renew_listings(request)
    elif automation_type == "relist_facebook_ads":
        return run_relist_ads(request)
    elif automation_type == "delete_duplicate_listings":
        return run_delete_duplicates(request)
    elif automation_type == "delete_all_listings":
        return run_delete_all(request)
    elif automation_type == "draft_delete_automation":
        return run_delete_drafts(request)
    elif automation_type == "open_custom_link":
        return run_open_custom_link(request)

    # ─── DRAFT PUBLISHER (default) ─────────────────────────────────────────
    print("=" * 70)
    print("🚀 SMBOT — DRAFT PUBLISHER")
    print("=" * 70)

    pw = browser = context = page = None
    try:
        # STEP 1: GET DATA
        print("\n📊 STEP 1: Fetching data...")
        creds = FacebookCredential.objects.last()
        if not creds:
            return JsonResponse({"success": False, "error": "❌ No credentials saved!"})

        listing = Listing.objects.all().order_by('-id').first()
        if not listing:
            return JsonResponse({"success": False, "error": "❌ No listings saved!"})

        all_titles    = list(listing.titles.order_by('id').values_list('title', flat=True))
        all_locations = list(listing.locations.order_by('id').values_list('location', flat=True))
        all_images    = [
            os.path.join(settings.MEDIA_ROOT, img.image.name)
            for img in listing.images.all().order_by('id')
        ]

        if not all_titles or not all_locations or not all_images:
            return JsonResponse({"success": False, "error": "❌ Missing titles, locations or images!"})

        try:
            body         = json.loads(request.body.decode("utf-8"))
            num_listings = int(body.get("tabs", 1))
        except Exception:
            num_listings = 1

        print(f"   ✅ Email: {creds.phone_or_email}")
        print(f"   📝 Titles: {len(all_titles)}  📍 Locations: {len(all_locations)}  🖼️ Images: {len(all_images)}")
        print(f"   💰 Price: {format_price(listing.price)}  📦 Category: {listing.category}")
        print(f"   🔢 Listings to create: {num_listings}")

        # STEP 2: LAUNCH BROWSER
        print("\n🌐 STEP 2: Launching browser...")
        pw, browser, context, page = create_browser()
        print("   ✅ Browser launched")

        # STEP 3: LOGIN
        print("\n🔐 STEP 3: Logging in...")
        if not pw_login(page, creds.phone_or_email, creds.password):
            browser.close(); pw.stop()
            return JsonResponse({"success": False, "error": "❌ Login failed or timed out!"})

        # STEP 4: FILL & SAVE DRAFTS
        print(f"\n💾 STEP 4: Creating {num_listings} draft(s)...")
        drafts_created = 0

        for i in range(num_listings):
            print(f"\n{'='*60}")
            print(f"📝 Draft {i+1}/{num_listings}")
            print(f"{'='*60}")
            title    = all_titles[i % len(all_titles)]
            location = all_locations[i % len(all_locations)]
            img_path = all_images[i % len(all_images)]

            if not os.path.exists(img_path):
                print(f"   ❌ Image file not found: {img_path}")
                continue

            try:
                page.goto("https://www.facebook.com/marketplace/create/item",
                          wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1000)
                page.evaluate("window.scrollTo(0,0)")

                success = pw_fill_listing_form(page, listing, title, location, img_path)
                if success:
                    drafts_created += 1
                    print(f"   ✅ Draft {i+1} saved!")
                else:
                    print(f"   ⚠️ Draft {i+1} may not have saved")
                    try:
                        page.screenshot(path=f"error_draft_{i+1}.png")
                    except Exception:
                        pass

            except Exception as e:
                print(f"   ❌ Error on draft {i+1}: {e}")
                try:
                    page.screenshot(path=f"error_draft_{i+1}.png")
                except Exception:
                    pass
                continue

        print(f"\n   ✅ Drafts created: {drafts_created}/{num_listings}")
        if drafts_created == 0:
            browser.close(); pw.stop()
            return JsonResponse({"success": False, "error": "❌ No drafts saved!"})

        # STEP 5: OPEN DRAFTS IN TABS
        print("\n📂 STEP 5: Opening all drafts...")
        draft_pages = pw_open_drafts(page, context)

        if not draft_pages:
            browser.close(); pw.stop()
            return JsonResponse({"success": False,
                                 "error": "❌ No draft tabs opened! Check no_drafts_found.png"})

        # STEP 6: CLICK NEXT ON ALL TABS
        print(f"\n➡️ STEP 6: Clicking Next on {len(draft_pages)} tab(s)...")
        next_count = 0
        next_selectors = [
            "//div[@aria-label='Next']",
            "//div[@role='button'][@aria-label='Next']",
            "//span[text()='Next']",
            "//button[text()='Next']",
            "//div[@role='button'][.//span[text()='Next']]",
        ]
        for idx, dp in enumerate(draft_pages):
            try:
                dp.evaluate("window.scrollTo(0,0)")
                dp.wait_for_timeout(800)
                if _try_click(dp, next_selectors, timeout=3000):
                    dp.wait_for_timeout(600)
                    next_count += 1
                    print(f"   ✅ Next clicked on tab {idx+1}")
                else:
                    print(f"   ⚠️ Next button not found on tab {idx+1}")
                    try:
                        dp.screenshot(path=f"error_next_{idx+1}.png")
                    except Exception:
                        pass
            except Exception as e:
                print(f"   ⚠️ Error Next tab {idx+1}: {e}")

        # STEP 7: PUBLISH ALL TABS (fast)
        print(f"\n🚀 STEP 7: Publishing {len(draft_pages)} listing(s)...")
        published = 0
        publish_selectors = [
            "//div[@aria-label='Publish']",
            "//div[@role='button'][@aria-label='Publish']",
            "//span[text()='Publish']",
            "//button[text()='Publish']",
            "//div[@role='button'][.//span[text()='Publish']]",
        ]
        for idx, dp in enumerate(draft_pages):
            try:
                if _try_click(dp, publish_selectors, timeout=3000):
                    dp.wait_for_timeout(400)
                    published += 1
                    print(f"   ✅ Published listing {idx+1}")
                else:
                    print(f"   ⚠️ Publish button not found on tab {idx+1}")
                    try:
                        dp.screenshot(path=f"error_publish_{idx+1}.png")
                    except Exception:
                        pass
            except Exception as e:
                print(f"   ⚠️ Error publishing tab {idx+1}: {e}")

        # STEP 8: CLOSE TABS (human-like delay)
        print("\n🧹 STEP 8: Closing tabs...")
        for idx, dp in enumerate(draft_pages):
            try:
                dp.close()
                print(f"   ✅ Closed tab {idx+1}")
                time.sleep(random.uniform(4, 10))
            except Exception:
                pass

        # STEP 9: CLOSE BROWSER
        try:
            browser.close()
            pw.stop()
            print("   ✅ Browser closed")
        except Exception:
            pass

        print(f"\n{'='*70}")
        print("🎉 BOT COMPLETED!")
        print(f"   📝 Drafts: {drafts_created}  🚀 Published: {published}")
        print(f"{'='*70}")

        return JsonResponse({
            "success": True,
            "message": f"✅ Done! Created {drafts_created} drafts, published {published} listings!",
            "created": drafts_created,
            "published": published,
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        try:
            if browser: browser.close()
            if pw: pw.stop()
        except Exception:
            pass
        return JsonResponse({"success": False, "error": f"❌ Critical error: {str(e)}"})


# ==========================================
# AUTOMATION TYPE HANDLERS
# ==========================================

def _launch_and_login(target_url, creds):
    """Helper: launch browser → login → goto target_url. Returns (pw, browser, context, page)."""
    pw, browser, context, page = create_browser()
    ok = pw_login(page, creds.phone_or_email, creds.password)
    if not ok:
        try: browser.close(); pw.stop()
        except Exception: pass
        raise Exception("Login failed or timed out")
    page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    return pw, browser, context, page


@csrf_exempt
def run_renew_listings(request):
    creds = FacebookCredential.objects.last()
    if not creds:
        return JsonResponse({"success": False, "error": "No credentials saved!"})
    pw = browser = None
    try:
        pw, browser, context, page = _launch_and_login(
            "https://www.facebook.com/marketplace/you/selling", creds)

        # Scroll to load all listings
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)

        renewed = 0
        btns = page.locator(
            "//div[@role='button'][.//span[contains(text(),'Renew')]]"
        ).all()
        for btn in btns:
            try:
                btn.scroll_into_view_if_needed()
                page.wait_for_timeout(400)
                btn.click()
                page.wait_for_timeout(random.randint(1500, 3000))
                renewed += 1
            except Exception:
                continue

        browser.close(); pw.stop()
        return JsonResponse({"success": True, "message": f"✅ Renewed {renewed} listings!"})
    except Exception as e:
        if browser: browser.close()
        if pw: pw.stop()
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def run_relist_ads(request):
    creds = FacebookCredential.objects.last()
    if not creds:
        return JsonResponse({"success": False, "error": "No credentials saved!"})
    pw = browser = None
    try:
        pw, browser, context, page = _launch_and_login(
            "https://www.facebook.com/marketplace/you/selling", creds)

        relisted = 0
        btns = page.locator(
            "//div[@role='button'][.//span[contains(text(),'Relist')]]"
        ).all()
        for btn in btns[:20]:
            try:
                btn.scroll_into_view_if_needed()
                page.wait_for_timeout(400)
                btn.click()
                page.wait_for_timeout(random.randint(1500, 3000))
                relisted += 1
            except Exception:
                continue

        browser.close(); pw.stop()
        return JsonResponse({"success": True, "message": f"✅ Relisted {relisted} ads!"})
    except Exception as e:
        if browser: browser.close()
        if pw: pw.stop()
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def run_delete_duplicates(request):
    creds = FacebookCredential.objects.last()
    if not creds:
        return JsonResponse({"success": False, "error": "No credentials saved!"})
    pw = browser = None
    try:
        pw, browser, context, page = _launch_and_login(
            "https://www.facebook.com/marketplace/you/selling", creds)

        for _ in range(5):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

        seen, deleted = {}, 0
        articles = page.locator("//div[@role='article']").all()
        for article in articles:
            try:
                title_el = article.locator("//span[string-length(text())>3]").first
                title = title_el.inner_text().strip().lower()
                if title in seen:
                    article.locator("//div[@aria-label='More options']").first.click()
                    page.wait_for_timeout(400)
                    page.locator("//div[@role='menuitem'][.//span[contains(text(),'Delete')]]").click(timeout=2000)
                    page.wait_for_timeout(400)
                    page.locator("//div[@role='button'][.//span[text()='Delete']]").click(timeout=2000)
                    deleted += 1
                    page.wait_for_timeout(800)
                else:
                    seen[title] = True
            except Exception:
                continue

        browser.close(); pw.stop()
        return JsonResponse({"success": True, "message": f"✅ Deleted {deleted} duplicates!"})
    except Exception as e:
        if browser: browser.close()
        if pw: pw.stop()
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def run_delete_all(request):
    creds = FacebookCredential.objects.last()
    if not creds:
        return JsonResponse({"success": False, "error": "No credentials saved!"})
    pw = browser = None
    try:
        pw, browser, context, page = _launch_and_login(
            "https://www.facebook.com/marketplace/you/selling", creds)

        deleted = 0
        for _ in range(200):
            try:
                page.locator("(//div[@aria-label='More options'])[1]").click(timeout=3000)
                page.wait_for_timeout(400)
                page.locator("//div[@role='menuitem'][.//span[contains(text(),'Delete')]]").click(timeout=2000)
                page.wait_for_timeout(400)
                page.locator("//div[@role='button'][.//span[text()='Delete']]").click(timeout=2000)
                deleted += 1
                page.wait_for_timeout(1000)
            except Exception:
                break

        browser.close(); pw.stop()
        return JsonResponse({"success": True, "message": f"✅ Deleted {deleted} listings!"})
    except Exception as e:
        if browser: browser.close()
        if pw: pw.stop()
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def run_delete_drafts(request):
    creds = FacebookCredential.objects.last()
    if not creds:
        return JsonResponse({"success": False, "error": "No credentials saved!"})
    pw = browser = None
    try:
        pw, browser, context, page = _launch_and_login(
            "https://www.facebook.com/marketplace/you/selling", creds)

        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

        links = page.locator("a[aria-label='Continue'][role='link']").all()
        draft_urls = []
        for l in links:
            try:
                href = l.get_attribute("href")
                if href:
                    draft_urls.append(href)
            except Exception:
                pass

        deleted = 0
        for url in draft_urls:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(1500)
                _try_click(page, [
                    "//div[@aria-label='Delete listing']",
                    "//div[@aria-label='Delete']",
                ], timeout=3000)
                page.wait_for_timeout(400)
                _try_click(page, [
                    "//div[@role='button'][.//span[text()='Delete']]",
                ], timeout=2000)
                deleted += 1
                page.wait_for_timeout(800)
            except Exception:
                continue

        browser.close(); pw.stop()
        return JsonResponse({"success": True, "message": f"✅ Deleted {deleted} draft listings!"})
    except Exception as e:
        if browser: browser.close()
        if pw: pw.stop()
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
def run_open_custom_link(request):
    creds = FacebookCredential.objects.last()
    if not creds:
        return JsonResponse({"success": False, "error": "No credentials saved!"})
    try:
        body        = json.loads(request.body.decode("utf-8"))
        custom_link = body.get("custom_link", "https://www.facebook.com/marketplace")
    except Exception:
        custom_link = "https://www.facebook.com/marketplace"

    pw = browser = None
    try:
        pw, browser, context, page = _launch_and_login(custom_link, creds)
        # Browser intentionally stays open so user can interact
        return JsonResponse({"success": True, "message": f"✅ Opened: {custom_link}"})
    except Exception as e:
        if browser: browser.close()
        if pw: pw.stop()
        return JsonResponse({"success": False, "error": str(e)})
