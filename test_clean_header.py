import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.stdout.reconfigure(encoding='utf-8')

html_path = os.path.abspath('index.html').replace('\\', '/')
artifacts_dir = r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,800')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"❌ FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

try:
    print("--- 1. LOAD INDEX.HTML IN DESKTOP VIEW (1280x800) ---")
    driver.get('file:///' + html_path)
    time.sleep(0.5)

    driver.execute_script("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('tcc_firebase_disabled_v1', 'true');")
    driver.get('file:///' + html_path)
    time.sleep(1)
    driver.execute_script("initAdminAuth();")

    # Navigate to MLBB dashboard
    driver.execute_script("openEsportDashboard('mlbb');")
    time.sleep(0.5)

    header_html = driver.execute_script("return document.getElementById('appHeader').innerHTML;")

    # 1. Verify quick esport switcher pill removed
    has_btn_mlbb = driver.execute_script("return !!document.getElementById('btnNavEsportMLBB');")
    has_btn_codm = driver.execute_script("return !!document.getElementById('btnNavEsportCODM');")
    assert_true(not has_btn_mlbb and not has_btn_codm, "Esport switcher pill (MLBB/CODM) removed from header")

    # 2. Verify Database button removed from header
    has_btn_db = driver.execute_script("return !!document.getElementById('btnHeaderDatabase');")
    assert_true(not has_btn_db, "Header Database button removed from header")

    # 3. Verify Viewer badge removed from header
    has_viewer_badge = "Viewer" in header_html
    assert_true(not has_viewer_badge, "Viewer badge removed from header")

    # Capture desktop clean header screenshot
    screenshot_desktop = os.path.join(artifacts_dir, "header_clean_desktop.png")
    driver.save_screenshot(screenshot_desktop)
    print(f"Saved clean desktop header screenshot: {screenshot_desktop}")

    print("\n--- 2. TEST MOBILE VIEW (375x812) ---")
    driver.set_window_size(375, 812)
    time.sleep(0.5)

    screenshot_mobile = os.path.join(artifacts_dir, "header_clean_mobile.png")
    driver.save_screenshot(screenshot_mobile)
    print(f"Saved clean mobile header screenshot: {screenshot_mobile}")

    print("\n--- 3. VERIFY LOGIN STILL WORKS CLEANLY ---")
    driver.execute_script("submitAdminPin('codm2026');")
    time.sleep(0.3)
    role = driver.execute_script("return currentSession ? currentSession.role : null;")
    assert_true(role == 'marshal', f"Logged in as marshal successfully (role: {role})")

    driver.execute_script("logoutSession(false);")
    time.sleep(0.3)
    header_html_after_logout = driver.execute_script("return document.getElementById('appHeader').innerHTML;")
    assert_true("Viewer" not in header_html_after_logout, "Viewer badge remains absent after logout")

    print("\n🎉 ALL HEADER CLEANLINESS CHECKS PASSED PERFECTLY!")

except Exception as e:
    print(f"\n❌ UNHANDLED EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    driver.quit()
