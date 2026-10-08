import os
import sys
import time
import json

sys.stdout.reconfigure(encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

html_path = os.path.abspath('index.html').replace('\\', '/')
artifacts_dir = r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1440,960')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"❌ FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

try:
    print("=================================================================")
    print("--- 1. LOAD INDEX.HTML AND VERIFY VIEWER ACCESS RESTRICTION ---")
    print("=================================================================")
    driver.get('http://localhost:8080/index.html')
    time.sleep(1)

    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    driver.get('http://localhost:8080/index.html')
    time.sleep(1)

    # In default viewer mode, btnHeaderCoinToss should NOT be displayed
    btn_coin_toss = driver.find_element(By.ID, "btnHeaderCoinToss")
    is_displayed = btn_coin_toss.is_displayed()
    assert_true(not is_displayed, "Coin Toss header button is hidden for spectator/viewer mode (.marshal-only)")

    # Attempting to open coin toss modal while in viewer mode triggers auth required notification
    driver.execute_script("openCoinTossModal();")
    modal_hidden = driver.execute_script("return document.getElementById('coinTossModal').classList.contains('hidden');")
    assert_true(modal_hidden, "Coin toss modal remains hidden when called by unauthenticated viewer")

    print("\n=================================================================")
    print("--- 2. LOG IN AS MLBB MARSHAL & VERIFY MARSHAL VISIBILITY ---")
    print("=================================================================")
    driver.execute_script("""
        openAdminLoginModal();
        document.getElementById('adminPinInput').value = 'mlbb2026';
        submitRoleLogin();
    """)
    time.sleep(0.8)

    session_account = driver.execute_script("return currentSession ? currentSession.accountId : null;")
    assert_true(session_account == 'mlbb_marshal', f"Successfully authenticated as mlbb_marshal (got {session_account})")

    is_marshal_btn_visible = btn_coin_toss.is_displayed()
    assert_true(is_marshal_btn_visible, "Coin Toss header button is visible for Table Marshal")

    screenshot_path = os.path.join(artifacts_dir, "marshal_header_coin_toss_visible.png")
    driver.save_screenshot(screenshot_path)
    print(f"📸 Saved screenshot: {screenshot_path}")

    print("\n=================================================================")
    print("--- 3. OPEN COIN TOSS MODAL & TEST TEAM ASSIGNMENT & SWAP ---")
    print("=================================================================")
    btn_coin_toss.click()
    time.sleep(0.5)

    modal_open = driver.execute_script("return !document.getElementById('coinTossModal').classList.contains('hidden');")
    assert_true(modal_open, "Coin Toss Modal opens successfully")

    # Select CIT for Heads and CBA for Tails
    driver.execute_script("""
        document.getElementById('coinTossHeadsSelect').value = 'CIT';
        document.getElementById('coinTossTailsSelect').value = 'CBA';
        updateCoinTossPreview();
    """)
    heads_val = driver.execute_script("return document.getElementById('coinTossHeadsSelect').value;")
    tails_val = driver.execute_script("return document.getElementById('coinTossTailsSelect').value;")
    assert_true(heads_val == 'CIT' and tails_val == 'CBA', f"Heads set to CIT and Tails set to CBA (got {heads_val}, {tails_val})")

    # Test swap
    driver.execute_script("swapCoinTossSides();")
    heads_swapped = driver.execute_script("return document.getElementById('coinTossHeadsSelect').value;")
    tails_swapped = driver.execute_script("return document.getElementById('coinTossTailsSelect').value;")
    assert_true(heads_swapped == 'CBA' and tails_swapped == 'CIT', f"Swap Sides correctly inverted assignments to Heads=CBA, Tails=CIT (got {heads_swapped}, {tails_swapped})")

    screenshot_modal = os.path.join(artifacts_dir, "coin_toss_modal_ready.png")
    driver.save_screenshot(screenshot_modal)
    print(f"📸 Saved screenshot: {screenshot_modal}")

    print("\n=================================================================")
    print("--- 4. EXECUTE COIN FLIP & VERIFY 3D ANIMATION & OUTCOME ---")
    print("=================================================================")
    btn_flip = driver.find_element(By.ID, "btnFlipCoin")
    btn_flip.click()

    is_flipping = driver.execute_script("return isCoinTossing;")
    assert_true(is_flipping, "Coin toss in-progress state is active (card spinning)")

    # Wait for the 1.8s flip animation + audio
    time.sleep(2.2)

    is_flipping_done = driver.execute_script("return !isCoinTossing;")
    assert_true(is_flipping_done, "Coin toss animation completed and landed on a face")

    # Check outcome banner
    outcome_html = driver.execute_script("return document.getElementById('coinTossOutcomeBanner').innerHTML;")
    assert_true("RESULT:" in outcome_html and ("HEADS" in outcome_html or "TAILS" in outcome_html), f"Outcome banner announced valid result: {outcome_html[:120]}")
    assert_true("Wins the Toss" in outcome_html, "Winning team announced in outcome banner")

    screenshot_outcome = os.path.join(artifacts_dir, "coin_toss_result_banner.png")
    driver.save_screenshot(screenshot_outcome)
    print(f"📸 Saved screenshot: {screenshot_outcome}")

    print("\n=================================================================")
    print("--- 5. CHECK AUDIT HISTORY LOG & REPEATED TOSSES ---")
    print("=================================================================")
    history_len = driver.execute_script("return coinTossHistory.length;")
    assert_true(history_len == 1, f"Audit history contains exactly 1 recorded toss (got {history_len})")

    # Flip 2 more times to test consecutive spins and randomness distribution
    for i in range(2):
        print(f"Executing toss #{i+2}...")
        driver.execute_script("flipCoin();")
        time.sleep(2.1)

    history_len_after = driver.execute_script("return coinTossHistory.length;")
    assert_true(history_len_after == 3, f"Audit history successfully logged 3 tosses (got {history_len_after})")

    history_text = driver.execute_script("return document.getElementById('coinTossHistoryList').innerText;")
    print(f"Audit log excerpt:\n{history_text}")

    screenshot_history = os.path.join(artifacts_dir, "coin_toss_audit_history.png")
    driver.save_screenshot(screenshot_history)
    print(f"📸 Saved screenshot: {screenshot_history}")

    driver.execute_script("closeCoinTossModal();")
    time.sleep(0.3)
    modal_closed = driver.execute_script("return document.getElementById('coinTossModal').classList.contains('hidden');")
    assert_true(modal_closed, "Coin Toss modal closed successfully")

    print("\n=================================================================")
    print("--- 6. TEST LAUNCH FROM SCORE EDIT MODAL WITH MATCH CONTEXT ---")
    print("=================================================================")
    # Assign match teams for ub_qf1 and open score modal
    driver.execute_script("""
        PLAYOFF_DATA['ub_qf1'].team1 = 'CIT';
        PLAYOFF_DATA['ub_qf1'].team2 = 'CBA';
        openScoreModal('ub_qf1');
    """)
    time.sleep(0.5)

    score_modal_open = driver.execute_script("return !document.getElementById('scoreEditModal').classList.contains('hidden');")
    assert_true(score_modal_open, "Match Score Modal opened for ub_qf1")

    # Click Coin Toss inside scoreEditModal
    driver.execute_script("openCoinTossModalFromMatch();")
    time.sleep(0.5)

    coin_modal_context_open = driver.execute_script("return !document.getElementById('coinTossModal').classList.contains('hidden');")
    assert_true(coin_modal_context_open, "Coin Toss Modal opened from Match Score Modal")

    # Verify team 1 and team 2 of ub_qf1 are preselected
    match_t1 = driver.execute_script("return PLAYOFF_DATA['ub_qf1'].team1;")
    match_t2 = driver.execute_script("return PLAYOFF_DATA['ub_qf1'].team2;")
    heads_match_sel = driver.execute_script("return document.getElementById('coinTossHeadsSelect').value;")
    tails_match_sel = driver.execute_script("return document.getElementById('coinTossTailsSelect').value;")

    assert_true(heads_match_sel == match_t1, f"Heads preselected with match team 1 ({match_t1})")
    assert_true(tails_match_sel == match_t2, f"Tails preselected with match team 2 ({match_t2})")

    screenshot_match_context = os.path.join(artifacts_dir, "coin_toss_match_context_opened.png")
    driver.save_screenshot(screenshot_match_context)
    print(f"📸 Saved screenshot: {screenshot_match_context}")

    driver.execute_script("closeCoinTossModal(); closeScoreModal();")

    print("\n=================================================================")
    print("🏆 ALL REFEREE COIN TOSS RANDOMIZER TESTS PASSED PERFECTLY!")
    print("=================================================================")

finally:
    driver.quit()
