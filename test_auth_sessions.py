import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

html_path = os.path.abspath('index.html').replace('\\', '/')

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,900')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"PASS: {msg}")

try:
    print("--- 1. LOAD INDEX.HTML ---")
    driver.get('file:///' + html_path)
    time.sleep(1)

    # Clean storage first
    driver.execute_script("localStorage.clear(); sessionStorage.clear(); initAdminAuth();")

    # Verify initial viewer state
    assert_true(driver.execute_script("return currentSession === null;"), "Initial currentSession is null")
    assert_true(driver.execute_script("return getEffectiveRole() === 'viewer';"), "Initial effective role is viewer")
    assert_true(driver.execute_script("return !canScore();"), "Initial canScore() is False")
    assert_true(driver.execute_script("return !isAdmin();"), "Initial isAdmin() is False")

    print("\n--- 2. VERIFY SINGLE LOGIN MODAL (NO CHOICES / TABS) ---")
    driver.execute_script("openAdminLoginModal();")
    time.sleep(0.3)
    modal_hidden = driver.execute_script("return document.getElementById('adminLoginModal').classList.contains('hidden');")
    assert_true(not modal_hidden, "Login modal is opened (not hidden)")

    # Confirm there are NO scope or role choice tabs
    scope_tabs_exist = driver.execute_script("return !!document.getElementById('scopeBtnMlbb');")
    role_tabs_exist = driver.execute_script("return !!document.getElementById('roleBtnMarshal');")
    pin_input_exists = driver.execute_script("return !!document.getElementById('adminPinInput');")
    assert_true(not scope_tabs_exist, "No scope selection tabs in DOM")
    assert_true(not role_tabs_exist, "No role selection tabs in DOM")
    assert_true(pin_input_exists, "Single #adminPinInput exists")

    # Take screenshot of clean single-input login modal
    artifact_modal_path = os.path.join(r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055", "verified_single_login_modal.png")
    driver.save_screenshot(artifact_modal_path)
    print(f"Modal screenshot saved to: {artifact_modal_path}")

    print("\n--- 3. TEST INVALID PASSWORD REJECTION ---")
    driver.execute_script("""
        document.getElementById('adminPinInput').value = 'invalidpassword123';
        submitRoleLogin();
    """)
    assert_true(driver.execute_script("return currentSession === null;"), "Invalid password does not create session")
    is_err_visible = driver.execute_script("return !document.getElementById('adminPinError').classList.contains('hidden');")
    assert_true(is_err_visible, "Error banner is visible after invalid password")
    err_text = driver.execute_script("return document.getElementById('adminPinErrorText').innerText;")
    assert_true("incorrect" in err_text.lower(), f"Error message displays: {err_text}")

    print("\n--- 4. TEST MLBB PASSWORD ROUTING (mlbb2026 -> MLBB Dashboard) ---")
    # Start from CODM dashboard to prove routing
    driver.execute_script("openEsportDashboard('codm');")
    assert_true(driver.execute_script("return currentEsport === 'codm';"), "Pre-condition: currently on CODM dashboard")

    # Enter MLBB password
    driver.execute_script("""
        openAdminLoginModal();
        document.getElementById('adminPinInput').value = 'mlbb2026';
        submitRoleLogin();
    """)
    time.sleep(0.3)

    assert_true(driver.execute_script("return currentSession !== null;"), "Session created for mlbb2026")
    assert_true(driver.execute_script("return currentSession.accountId === 'mlbb_marshal';"), "Account is mlbb_marshal")
    assert_true(driver.execute_script("return currentSession.gameScope === 'mlbb';"), "Session scope is mlbb")
    assert_true(driver.execute_script("return currentEsport === 'mlbb';"), "Auto-routed to MLBB dashboard based on password!")
    assert_true(driver.execute_script("return canScore('mlbb') === true;"), "canScore('mlbb') is TRUE")
    assert_true(driver.execute_script("return canScore('codm') === false;"), "canScore('codm') is FALSE (scoped)")

    # Take screenshot of MLBB dashboard after password route
    artifact_mlbb_path = os.path.join(r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055", "verified_mlbb_dashboard_routed.png")
    driver.save_screenshot(artifact_mlbb_path)
    print(f"MLBB dashboard screenshot saved: {artifact_mlbb_path}")

    print("\n--- 4b. TEST EXIT CONFIRMATION MODAL & PROCEED FLOW ---")
    # Click Exit button in the header
    driver.execute_script("document.getElementById('headerExitBtn').click();")
    time.sleep(0.3)

    # Verify confirmation modal is shown
    confirm_modal_visible = driver.execute_script("return !document.getElementById('actionConfirmModal').classList.contains('hidden');")
    assert_true(confirm_modal_visible, "Action confirmation modal displayed on Exit click")

    modal_title = driver.execute_script("return document.getElementById('confirmModalTitle').innerText;")
    modal_msg = driver.execute_script("return document.getElementById('confirmModalMessage').innerText;")
    btn_text = driver.execute_script("return document.getElementById('confirmModalBtnText').innerText;")
    assert_true("exit" in modal_title.lower(), f"Modal title mentions exit: {modal_title}")
    assert_true("proceed" in modal_msg.lower(), f"Modal message asks to proceed: {modal_msg}")
    assert_true("proceed" in btn_text.lower(), f"Submit button confirms proceed: {btn_text}")

    # Capture screenshot of Exit Confirmation Dialog
    artifact_exit_confirm_path = os.path.join(r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055", "verified_exit_confirmation_modal.png")
    driver.save_screenshot(artifact_exit_confirm_path)
    print(f"Exit confirmation screenshot saved: {artifact_exit_confirm_path}")

    # 1. Test Cancel: modal closes, session remains active
    driver.execute_script("closeActionConfirmModal();")
    assert_true(driver.execute_script("return currentSession !== null;"), "Session remains active after cancelling exit")

    # 2. Test Proceed: modal proceeds and logs out
    driver.execute_script("document.getElementById('headerExitBtn').click();")
    time.sleep(0.2)
    driver.execute_script("document.getElementById('confirmModalSubmitBtn').click();")
    time.sleep(0.3)

    assert_true(driver.execute_script("return currentSession === null;"), "Session terminated after clicking Proceed & Exit")
    assert_true(driver.execute_script("return getEffectiveRole() === 'viewer';"), "Reverted to viewer mode after proceeding with exit")

    print("\n--- 5. TEST CODM PASSWORD ROUTING (codm2026 -> CODM Dashboard) ---")

    # Stay on MLBB dashboard, enter CODM password
    assert_true(driver.execute_script("return currentEsport === 'mlbb';"), "Pre-condition: currently on MLBB dashboard")
    driver.execute_script("""
        openAdminLoginModal();
        document.getElementById('adminPinInput').value = 'codm2026';
        submitRoleLogin();
    """)
    time.sleep(0.3)

    assert_true(driver.execute_script("return currentSession !== null;"), "Session created for codm2026")
    assert_true(driver.execute_script("return currentSession.accountId === 'codm_marshal';"), "Account is codm_marshal")
    assert_true(driver.execute_script("return currentSession.gameScope === 'codm';"), "Session scope is codm")
    assert_true(driver.execute_script("return currentEsport === 'codm';"), "Auto-routed to CODM dashboard based on password!")
    assert_true(driver.execute_script("return canScore('codm') === true;"), "canScore('codm') is TRUE")
    assert_true(driver.execute_script("return canScore('mlbb') === false;"), "canScore('mlbb') is FALSE (scoped)")

    # Take screenshot of CODM dashboard after password route
    artifact_codm_path = os.path.join(r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055", "verified_codm_dashboard_routed.png")
    driver.save_screenshot(artifact_codm_path)
    print(f"CODM dashboard screenshot saved: {artifact_codm_path}")

    print("\n--- 6. TEST MLBB ADMIN PASSWORD ROUTING (mlbbadmin -> MLBB Admin) ---")
    driver.execute_script("logoutSession();")
    driver.execute_script("""
        openAdminLoginModal();
        document.getElementById('adminPinInput').value = 'mlbbadmin';
        submitRoleLogin();
    """)
    time.sleep(0.3)

    assert_true(driver.execute_script("return currentSession.accountId === 'mlbb_admin';"), "Account is mlbb_admin")
    assert_true(driver.execute_script("return currentEsport === 'mlbb';"), "Auto-routed to MLBB dashboard for MLBB Admin")
    assert_true(driver.execute_script("return isAdmin('mlbb') === true;"), "isAdmin('mlbb') is TRUE")
    assert_true(driver.execute_script("return isAdmin('codm') === false;"), "isAdmin('codm') is FALSE")

    print("\n--- 7. TEST CODM ADMIN PASSWORD ROUTING (codmadmin -> CODM Admin) ---")
    driver.execute_script("logoutSession();")
    driver.execute_script("""
        openAdminLoginModal();
        document.getElementById('adminPinInput').value = 'codmadmin';
        submitRoleLogin();
    """)
    time.sleep(0.3)

    assert_true(driver.execute_script("return currentSession.accountId === 'codm_admin';"), "Account is codm_admin")
    assert_true(driver.execute_script("return currentEsport === 'codm';"), "Auto-routed to CODM dashboard for CODM Admin")
    assert_true(driver.execute_script("return isAdmin('codm') === true;"), "isAdmin('codm') is TRUE")
    assert_true(driver.execute_script("return isAdmin('mlbb') === false;"), "isAdmin('mlbb') is FALSE")

    print("\n--- 8. TEST TOURNAMENT DIRECTOR PASSWORD (admin2026 -> All Games) ---")
    driver.execute_script("logoutSession();")
    # Return to Landing Hub
    driver.execute_script("showEsportHub();")
    hub_visible = driver.execute_script("return !document.getElementById('esportLandingHub').classList.contains('hidden');")
    assert_true(hub_visible, "Pre-condition: on Landing Hub")

    driver.execute_script("""
        openAdminLoginModal();
        document.getElementById('adminPinInput').value = 'admin2026';
        submitRoleLogin();
    """)
    time.sleep(0.3)

    assert_true(driver.execute_script("return currentSession.accountId === 'super_admin';"), "Account is super_admin")
    assert_true(driver.execute_script("return currentSession.gameScope === 'all';"), "Scope is 'all'")
    assert_true(driver.execute_script("return isAdmin('mlbb') === true;"), "Director is admin in MLBB")
    assert_true(driver.execute_script("return isAdmin('codm') === true;"), "Director is admin in CODM")
    hub_hidden_after_login = driver.execute_script("return document.getElementById('esportLandingHub').classList.contains('hidden');")
    assert_true(hub_hidden_after_login, "Hub transitioned to active dashboard on Director login")

    print("\n--- 9. TEST SESSION PERSISTENCE & EXPIRATION ---")
    driver.refresh()
    time.sleep(1)
    assert_true(driver.execute_script("return currentSession !== null;"), "Session preserved after page refresh")
    assert_true(driver.execute_script("return currentSession.accountId === 'super_admin';"), "Session account is still super_admin")

    # Manually expire
    driver.execute_script("currentSession.expiresAt = Date.now() - 5000; saveSession(currentSession);")
    assert_true(driver.execute_script("return loadSession() === null;"), "loadSession() returns null when expired")
    driver.refresh()
    time.sleep(1)
    assert_true(driver.execute_script("return currentSession === null;"), "currentSession is null after expired session page reload")
    assert_true(driver.execute_script("return getEffectiveRole() === 'viewer';"), "Reverted to viewer upon expiration")

    print("\n==========================================")
    print("ALL TESTS PASSED! 100% SINGLE LOGIN & ROUTING VERIFIED! 🎉")
    print("==========================================")

finally:
    driver.quit()
