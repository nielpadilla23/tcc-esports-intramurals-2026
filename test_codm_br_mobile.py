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
# Mobile viewport size: 375x812 (iPhone standard)
options.add_argument('--window-size=375,812')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"❌ FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

try:
    print("--- 1. LOAD INDEX.HTML IN MOBILE VIEW (375x812) ---")
    driver.get('file:///' + html_path)
    time.sleep(0.5)

    driver.execute_script("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('tcc_firebase_disabled_v1', 'true');")
    driver.get('file:///' + html_path)
    time.sleep(1)
    driver.execute_script("initAdminAuth();")

    # Navigate to CODM BR
    driver.execute_script("openEsportDashboard('codm', 'br');")
    time.sleep(0.5)

    # Log in as admin and simulate BR tournament so we have real scores in all tables
    driver.execute_script("submitAdminPin('admin2026');")
    time.sleep(0.3)
    driver.execute_script("simulateCodmBrTournament();")
    time.sleep(0.5)

    # Select Round 1 to view active round table
    driver.execute_script("selectBrRound(1);")
    time.sleep(3) # Wait for confetti animation to finish

    print("\n--- 2. VERIFY MOBILE STANDINGS TABLE (TOTAL PTS BADGES) ---")
    # Verify that the Total Pts badges in standings table do not wrap or split
    pts_badges_info = driver.execute_script("""
      const table = document.getElementById('brStandingsTableBody');
      const rows = table.querySelectorAll('tr');
      const results = [];
      rows.forEach(r => {
        const lastCell = r.querySelector('td:last-child');
        const badge = lastCell ? lastCell.querySelector('span') : null;
        if (badge) {
          const rect = badge.getBoundingClientRect();
          const text = badge.innerText.trim();
          results.push({
            text: text,
            height: rect.height,
            width: rect.width,
            hasLineBreak: text.includes('\\n')
          });
        }
      });
      return results;
    """)

    print(f"Found {len(pts_badges_info)} Total Pts badges in standings table.")
    for b in pts_badges_info:
        print(f"Badge: '{b['text']}' | dimensions: {b['width']}x{b['height']}px | hasLineBreak: {b['hasLineBreak']}")
        assert_true(not b['hasLineBreak'], f"Badge '{b['text']}' has no line break")
        # In single line, badge height with py-1.5 is typically around 26-32px, whereas multiline split was 45-60px
        assert_true(b['height'] < 40, f"Badge '{b['text']}' is single line (height: {b['height']}px)")

    # Scroll standings table into view and scroll horizontally to reveal Total Pts
    driver.execute_script("""
      const tableWrapper = document.getElementById('brStandingsTableHead').closest('.overflow-x-auto');
      tableWrapper.scrollIntoView();
      tableWrapper.scrollLeft = 9999;
    """)
    time.sleep(0.4)
    screenshot_standings = os.path.join(artifacts_dir, "codm_br_mobile_standings_fixed.png")
    driver.save_screenshot(screenshot_standings)
    print(f"Saved mobile standings screenshot: {screenshot_standings}")

    print("\n--- 3. VERIFY MOBILE ROUND-BY-ROUND BREAKDOWN TABLE (PLACEMENT BADGES) ---")
    plc_badges_info = driver.execute_script("""
      const container = document.getElementById('brActiveRoundContainer');
      const table = container.querySelector('table');
      const rows = table.querySelectorAll('tbody tr');
      const results = [];
      rows.forEach(r => {
        const firstCell = r.querySelector('td:first-child');
        const badge = firstCell ? firstCell.querySelector('span') : null;
        if (badge) {
          const rect = badge.getBoundingClientRect();
          const text = badge.innerText.trim();
          results.push({
            text: text,
            height: rect.height,
            width: rect.width,
            hasLineBreak: text.includes('\\n')
          });
        }
      });
      return results;
    """)

    print(f"Found {len(plc_badges_info)} placement badges in active round table.")
    for b in plc_badges_info:
        print(f"Badge: '{b['text']}' | dimensions: {b['width']}x{b['height']}px | hasLineBreak: {b['hasLineBreak']}")
        assert_true(not b['hasLineBreak'], f"Placement badge '{b['text']}' has no line break")
        # Single line pill height is ~24-32px, whereas multiline broken pill was 45-60px
        assert_true(b['height'] < 40, f"Placement badge '{b['text']}' is single line (height: {b['height']}px)")

    # Scroll active round breakdown table into view and take screenshot
    driver.execute_script("document.getElementById('brActiveRoundContainer').scrollIntoView();")
    time.sleep(0.3)
    screenshot_round = os.path.join(artifacts_dir, "codm_br_mobile_round_breakdown_fixed.png")
    driver.save_screenshot(screenshot_round)
    print(f"Saved mobile round breakdown screenshot: {screenshot_round}")

    print("\n🎉 ALL MOBILE VIEW BADGE CHECKS PASSED PERFECTLY!")

except Exception as e:
    print(f"\n❌ UNHANDLED EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    driver.quit()
