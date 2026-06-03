# SMBot - proxy_rotation.py (Playwright-ready, no Selenium)
import random
import requests
from datetime import datetime

class AdvancedProxyManager:
    def __init__(self, proxy_list=None):
        self.proxies          = proxy_list or []
        self.working_proxies  = []
        self.dead_proxies     = []
        self.current_index    = 0
        self.last_rotation    = datetime.now()
        self.rotation_interval = 30
        self.proxy_performance = {}

    def fetch_free_proxies(self, count=10):
        try:
            r = requests.get(
                "https://www.proxy-list.download/api/v1/get?type=http", timeout=5)
            if r.status_code == 200:
                self.proxies = [f"http://{p}" for p in r.text.split("\r\n")[:count] if p]
                print(f"✅ Fetched {len(self.proxies)} proxies")
                return self.proxies
        except Exception as e:
            print(f"❌ Proxy fetch error: {e}")
        return []

    def validate_proxy(self, proxy):
        try:
            r = requests.get("https://httpbin.org/ip",
                             proxies={"http": proxy, "https": proxy}, timeout=5)
            if r.status_code == 200:
                self.working_proxies.append(proxy)
                self.proxy_performance[proxy] = {"success": 1, "failed": 0, "last_used": datetime.now()}
                return True
        except Exception:
            self.dead_proxies.append(proxy)
        return False

    def get_random_proxy(self):
        return random.choice(self.working_proxies) if self.working_proxies else None

    def get_next_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

    def get_best_proxy(self):
        if not self.proxy_performance:
            return self.get_random_proxy()
        return max(self.proxy_performance, key=lambda k: self.proxy_performance[k]["success"])

    def auto_rotate_if_needed(self):
        diff = (datetime.now() - self.last_rotation).total_seconds()
        if diff >= self.rotation_interval:
            self.last_rotation = datetime.now()
            return self.get_next_proxy()
        return None

    def mark_proxy_failed(self, proxy):
        if proxy in self.proxy_performance:
            self.proxy_performance[proxy]["failed"] += 1
            if self.proxy_performance[proxy]["failed"] > 5 and proxy in self.proxies:
                self.proxies.remove(proxy)

    def get_playwright_proxy(self):
        """Return Playwright-compatible proxy dict or None."""
        url = self.get_best_proxy()
        return {"server": url} if url else None

proxy_manager = AdvancedProxyManager()
