# ==========================================
# SMBot - views_advanced.py (FIXED - Playwright only)
# ==========================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, os, time, random
from django.conf import settings
from .models import Listing, FacebookCredential
from .views import create_browser, pw_login, pw_fill_listing_form, format_price

try:
    from backend.ai_features import (
        title_generator, description_generator, tag_suggester,
        price_optimizer, timing_optimizer, behavior_analyzer, fraud_detector
    )
    from backend.proxy_rotation import proxy_manager
except Exception:
    title_generator = description_generator = tag_suggester = None
    price_optimizer = timing_optimizer = behavior_analyzer = fraud_detector = None
    proxy_manager = None


@csrf_exempt
def start_publishing_advanced(request):
    """
    Advanced bot with AI analysis, proxy rotation, and fingerprint spoofing.
    Uses Playwright (no Selenium).
    """
    print("=" * 70)
    print("🚀 SMBOT ADVANCED — AI + PROXY + FINGERPRINT")
    print("=" * 70)

    pw = browser = context = page = None
    try:
        # STEP 1: DATA
        print("\n📊 STEP 1: Fetching data...")
        creds = FacebookCredential.objects.last()
        if not creds:
            return JsonResponse({"success": False, "error": "❌ No credentials!"})

        listing = Listing.objects.all().order_by('-id').first()
        if not listing:
            return JsonResponse({"success": False, "error": "❌ No listings!"})

        try:
            data         = json.loads(request.body.decode("utf-8"))
            num_listings = int(data.get("tabs", 1))
        except Exception:
            num_listings = 1

        # STEP 2: AI ANALYSIS
        recommendations = []
        if behavior_analyzer:
            try:
                recommendations = behavior_analyzer.get_recommendations({
                    'title': listing.titles.first().title if listing.titles.exists() else '',
                    'description': listing.description,
                    'images': list(listing.images.all()),
                    'tags': listing.tags,
                })
                for rec in recommendations:
                    print(f"   {rec}")
            except Exception:
                pass

        # STEP 3: PROXY
        proxy_url = None
        if proxy_manager:
            try:
                if not proxy_manager.proxies:
                    proxy_manager.fetch_free_proxies(count=5)
                proxy_url = proxy_manager.get_best_proxy() if proxy_manager.working_proxies else None
                if proxy_url:
                    print(f"   🌐 Using proxy: {proxy_url[:30]}...")
            except Exception:
                pass

        all_titles    = list(listing.titles.order_by('id').values_list('title', flat=True))
        all_locations = list(listing.locations.order_by('id').values_list('location', flat=True))
        all_images    = [
            os.path.join(settings.MEDIA_ROOT, img.image.name)
            for img in listing.images.all().order_by('id')
        ]

        if not all_titles or not all_locations or not all_images:
            return JsonResponse({"success": False, "error": "❌ Missing data!"})

        # STEP 4: LAUNCH BROWSER
        from playwright.sync_api import sync_playwright
        pw_obj = sync_playwright().start()

        launch_args = [
            "--start-maximized", "--disable-notifications",
            "--no-sandbox", "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]
        browser_obj = pw_obj.chromium.launch(headless=False, args=launch_args)

        ctx_opts = dict(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
        )
        if proxy_url:
            ctx_opts["proxy"] = {"server": proxy_url}

        ctx = browser_obj.new_context(**ctx_opts)
        ctx.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            window.chrome = {runtime: {}};
        """)
        pg = ctx.new_page()
        print("   ✅ Browser launched")

        # STEP 5: LOGIN
        print("\n🔐 Logging in...")
        if not pw_login(pg, creds.phone_or_email, creds.password):
            browser_obj.close(); pw_obj.stop()
            return JsonResponse({"success": False, "error": "❌ Login failed!"})

        # STEP 6: CREATE LISTINGS
        print(f"\n📝 Creating {num_listings} listing(s)...")
        drafts_created = 0

        for i in range(num_listings):
            print(f"\n{'='*60}\n📝 Listing {i+1}/{num_listings}\n{'='*60}")

            if i > 0:
                delay = random.uniform(15, 30)
                print(f"   ⏱️ Rate-limit delay: {delay:.0f}s...")
                time.sleep(delay)

            title    = all_titles[i % len(all_titles)]
            location = all_locations[i % len(all_locations)]
            img_path = all_images[i % len(all_images)]

            if not os.path.exists(img_path):
                print(f"   ❌ Image not found: {img_path}")
                continue

            try:
                pg.goto("https://www.facebook.com/marketplace/create/item",
                        wait_until="domcontentloaded", timeout=30000)
                pg.wait_for_timeout(1000)

                ok = pw_fill_listing_form(pg, listing, title, location, img_path)
                if ok:
                    drafts_created += 1
                    print(f"   ✅ Listing {i+1} saved!")
                else:
                    print(f"   ⚠️ Listing {i+1} may not have saved")
            except Exception as e:
                print(f"   ❌ Error listing {i+1}: {e}")
                continue

        time.sleep(random.uniform(3, 6))
        browser_obj.close(); pw_obj.stop()

        return JsonResponse({
            "success": drafts_created > 0,
            "message": f"✅ Created {drafts_created}/{num_listings} listings (AI advanced mode)",
            "created": drafts_created,
            "ai_recommendations": recommendations,
            "proxy_used": bool(proxy_url),
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        try:
            if browser: browser.close()
            if pw: pw.stop()
        except Exception:
            pass
        return JsonResponse({"success": False, "error": f"❌ {str(e)}"})
