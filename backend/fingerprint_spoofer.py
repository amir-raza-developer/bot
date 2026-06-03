# SMBot - fingerprint_spoofer.py
# Fingerprint spoofing is handled natively by Playwright context in views.py.
# Kept as stub so views_advanced.py imports don't fail.

import random

class _FingerprintRandomizer:
    def rotate_fingerprint(self):
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "screen_width": random.choice([1366, 1440, 1920]),
            "screen_height": random.choice([768, 900, 1080]),
            "timezone": random.choice(["America/New_York", "Europe/London", "UTC"]),
        }

class _FingerprintApplier:
    def apply_fingerprint(self, driver, fp): pass
    def hide_headless_mode(self, driver): pass

fingerprint_randomizer = _FingerprintRandomizer()
fingerprint_applier    = _FingerprintApplier()

def get_fingerprint_status():
    return {"active": True, "method": "Playwright context init_script"}
