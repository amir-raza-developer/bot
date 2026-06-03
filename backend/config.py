# ==========================================
# ⚙️ CONFIGURATION FILE - CENTRALIZED SETTINGS
# ==========================================

import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# BROWSER SETTINGS
# ==========================================
BROWSER_SETTINGS = {
    'headless': False,  # Show browser window
    'start_maximized': True,
    'disable_notifications': True,
    'disable_popup_blocking': True,
    'disable_extensions': True,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
}

# ==========================================
# ANTI-DETECTION SETTINGS
# ==========================================
ANTI_DETECTION = {
    'use_proxies': True,
    'proxy_list': [
        'http://proxy1.com:8080',
        'http://proxy2.com:8080',
    ],
    'use_vpn': False,
    'rotate_user_agent': True,
    'add_delays': True,
    'min_delay': 2,
    'max_delay': 5,
    'typing_speed': 0.05,  # seconds per character
}

# ==========================================
# FACEBOOK SETTINGS
# ==========================================
FACEBOOK_SETTINGS = {
    'marketplace_url': 'https://www.facebook.com/marketplace',
    'create_listing_url': 'https://www.facebook.com/marketplace/create/item',
    'selling_page': 'https://www.facebook.com/marketplace/you/selling',
    'login_url': 'https://www.facebook.com/login',
    'timeout': 10,  # seconds
}

# ==========================================
# AUTOMATION SETTINGS
# ==========================================
AUTOMATION = {
    'max_listings_per_run': 100,
    'max_titles': 10,
    'max_locations': 10,
    'max_tags': 20,
    'save_screenshots': True,
    'screenshot_dir': 'backend/',
}

# ==========================================
# RETRY SETTINGS
# ==========================================
RETRY = {
    'max_attempts': 3,
    'retry_delay': 5,  # seconds
    'timeout': 30,  # seconds
}
