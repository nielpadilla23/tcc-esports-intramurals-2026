import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

sys.stdout.reconfigure(encoding='utf-8')

artifacts_dir = r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055"
html_path = os.path.abspath('index.html').replace('\\', '/')

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,850')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"❌ FAILED: {msg}")
        driver.quit()
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

try:
    print("=================================================================")
    print("--- 1. LOAD INDEX.HTML AND OPEN CODM BATTLE ROYALE ---")
    print("=================================================================")
    driver.get(f'file:///{html_path}')
    time.sleep(1)

    # Enter CODM BR mode
    driver.execute_script("openEsportDashboard('codm', 'br');")
    time.sleep(0.5)

    br_container = driver.find_element(By.ID, "codmBattleRoyaleContainer")
    assert_true(br_container.is_displayed(), "CODM Battle Royale container is displayed")

    # Verify Live Stage button exists in BR header
    live_stage_btn = driver.find_element(By.CSS_SELECTOR, "#codmBattleRoyaleContainer button[onclick*='openBrLiveStage']")
    assert_true(live_stage_btn is not None, "Live Stage button exists in BR header")

    print("\n=================================================================")
    print("--- 2. OPEN BR LIVE STAGE IN PRE-DROP STATE (ROUND 0) ---")
    print("=================================================================")
    # Click Live Stage button
    driver.execute_script("arguments[0].click();", live_stage_btn)
    time.sleep(0.5)

    overlay = driver.find_element(By.ID, "theaterModeOverlay")
    assert_true(overlay.is_displayed(), "Theater Mode overlay opened cleanly")

    stage_title = driver.find_element(By.ID, "theaterEsportTitle").text
    assert_true("battle royale" in stage_title.lower(), f"Theater title contains Battle Royale (got: {stage_title})")

    stage_badge = driver.find_element(By.ID, "theaterFormatBadge").text
    assert_true("8 rounds" in stage_badge.lower(), f"Format badge contains 8 Rounds (got: {stage_badge})")

    # Take screenshot of pre-drop Live Stage
    driver.save_screenshot(os.path.join(artifacts_dir, "br_live_stage_predrop.png"))
    print("Saved pre-drop Live Stage screenshot: br_live_stage_predrop.png")

    # Close theater mode
    driver.execute_script("closeTheaterMode();")
    time.sleep(0.5)
    assert_true(not overlay.is_displayed(), "Theater Mode closed cleanly")

    print("\n=================================================================")
    print("--- 3. SIMULATE FULL 8-ROUND BR TOURNAMENT ---")
    print("=================================================================")
    driver.execute_script("submitAdminPin('admin2026');")
    time.sleep(0.3)
    driver.execute_script("simulateCodmBrTournament();")
    time.sleep(0.5)

    # Verify completed rounds count
    completed_rounds = driver.execute_script("return Object.values(CODM_BR_DATA.rounds || {}).filter(r => r && r.status === 'completed').length;")
    assert_true(completed_rounds == 8, f"All 8 rounds completed in simulation (got: {completed_rounds})")

    # Get standings to know who is leading
    standings = driver.execute_script("return calculateBrStandings();")
    leader = standings[0]
    chaser = standings[1]
    print(f"Top Leader: {leader['name']} with {leader['totalPoints']} pts (Lead margin: {leader['totalPoints'] - chaser['totalPoints']} pts)")

    print("\n=================================================================")
    print("--- 4. OPEN BR LIVE STAGE WITH FULL ACCUMULATED SCORES ---")
    print("=================================================================")
    driver.execute_script("openBrLiveStage();")
    time.sleep(0.8)

    assert_true(overlay.is_displayed(), "Live stage opened with full tournament data")

    # Check that ONLY the BR Live Stage slide is loaded (slide count = 1)
    slide_total = driver.find_element(By.ID, "theaterSlideTotal").text
    assert_true(slide_total == "1", f"Only BR Live Stage slide is loaded (theaterSlideTotal = {slide_total})")

    slide_body_text = driver.find_element(By.ID, "theaterSlideBody").text

    # Verify Leader Spotlight is displayed
    assert_true(leader['name'].lower() in slide_body_text.lower(), f"Leader name {leader['name']} is prominently displayed in Live Stage")
    assert_true(f"{leader['totalPoints']} pts".lower() in slide_body_text.lower() or str(leader['totalPoints']) in slide_body_text, f"Leader's total accumulated score {leader['totalPoints']} is displayed")
    assert_true("accumulated standings" in slide_body_text.lower(), "Accumulated Standings title is displayed")
    assert_true(chaser['name'].lower() in slide_body_text.lower(), f"2nd team {chaser['name']} is displayed in scoreboard")

    # Verify top hero cards are removed as requested
    assert_true("2nd contender" not in slide_body_text.lower(), "Top 2nd contender card is removed")
    assert_true("3rd contender" not in slide_body_text.lower(), "Top 3rd contender card is removed")

    # Verify -0 pts, -1 pts differential badges are NOT present on total points
    assert_true("-0 pts" not in slide_body_text.lower() and "-0" not in slide_body_text, "Point differential badges (-0, -1) removed from Total Points")

    # Verify zero scroll (both vertically and horizontally)
    slide_body = driver.find_element(By.ID, "theaterSlideBody")
    scroll_height = driver.execute_script("return arguments[0].scrollHeight;", slide_body)
    client_height = driver.execute_script("return arguments[0].clientHeight;", slide_body)
    scroll_width = driver.execute_script("return arguments[0].scrollWidth;", slide_body)
    client_width = driver.execute_script("return arguments[0].clientWidth;", slide_body)
    print(f"Desktop Stage Dimensions: H={client_height} vs scrollH={scroll_height}, W={client_width} vs scrollW={scroll_width}")
    assert_true(scroll_height <= client_height + 4, f"Zero vertical scroll on desktop (scrollH={scroll_height} <= clientH={client_height})")
    assert_true(scroll_width <= client_width + 4, f"Zero horizontal scroll on desktop (scrollW={scroll_width} <= clientW={client_width})")

    # Verify zero bracket clutter
    assert_true("upper bracket" not in slide_body_text.lower(), "Upper Bracket is NOT present (no bracket clutter)")
    assert_true("lower bracket" not in slide_body_text.lower(), "Lower Bracket is NOT present (no bracket clutter)")

    # Save desktop screenshot
    driver.save_screenshot(os.path.join(artifacts_dir, "br_live_stage_full.png"))
    print("Saved simulated full Live Stage screenshot: br_live_stage_full.png")

    print("\n=================================================================")
    print("--- 5. TEST MOBILE VIEW (375x812) ---")
    print("=================================================================")
    driver.set_window_size(375, 812)
    time.sleep(0.5)

    driver.save_screenshot(os.path.join(artifacts_dir, "br_live_stage_mobile.png"))
    print("Saved mobile Live Stage screenshot: br_live_stage_mobile.png")

    print("\n=================================================================")
    print("🎉 ALL BR LIVE STAGE VERIFICATIONS PASSED FLAWLESSLY!")
    print("=================================================================")

finally:
    driver.quit()
