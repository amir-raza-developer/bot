# SMBot - anti_detection.py
# Anti-detection is handled natively by Playwright context in views.py:
#   - navigator.webdriver patched to undefined
#   - plugins spoofed
#   - window.chrome set
#   - custom user agent / locale / timezone set in new_context()

def get_anti_detection_status():
    return {"active": True, "method": "Playwright context init_script + context options"}
