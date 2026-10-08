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

    # Clean local storage first
    driver.execute_script("localStorage.clear(); sessionStorage.clear(); initAdminAuth();")

    # Verify initial viewer state
    assert_true(driver.execute_script("return currentSession === null;"), "Initial currentSession is null")
    assert_true(driver.execute_script("return getEffectiveRole() === 'viewer';"), "Initial effective role is viewer")
    assert_true(driver.execute_script("return !canScore();"), "Initial canScore() is False")
    assert_true(driver.execute_script("return !isAdmin();"), "Initial isAdmin() is False")

    print("\n--- 2. TEST LOGIN MODAL PRESETS & UI ---")
    driver.execute_script("openAdminLoginModal();")
    modal_hidden = driver.execute_script("return document.getElementById('adminLoginModal').classList.contains('hidden');")
    assert_true(not modal_hidden, "Login modal is opened (not hidden)")

    # Test selecting CODM scope tab
    driver.execute_script("selectLoginScope('codm');")
    assert_true(driver.execute_script("return targetLoginScope === 'codm';"), "targetLoginScope updated to codm")
    hint_text = driver.execute_script("return document.getElementById('loginPinHint').innerText;")
    assert_true("codm" in hint_text.lower(), f"CODM hint displayed: {hint_text}")

    # Test selecting Admin role tab
    driver.execute_script("selectLoginTargetRole('admin');")
    assert_true(driver.execute_script("return targetLoginRole === 'admin';"), "targetLoginRole updated to admin")
    hint_text_admin = driver.execute_script("return document.getElementById('loginPinHint').innerText;")
    assert_true("codmadmin" in hint_text_admin.lower(), f"CODM admin hint displayed: {hint_text_admin}")

    # Test quickFillAccount('mlbb_marshal')
    driver.execute_script("quickFillAccount('mlbb_marshal');")
    assert_true(driver.execute_script("return targetLoginScope === 'mlbb';"), "Scope switched to mlbb via quickFill")
    assert_true(driver.execute_script("return targetLoginRole === 'marshal';"), "Role switched to marshal via quickFill")
    pin_val = driver.execute_script("return document.getElementById('adminPinInput').value;")
    assert_true(pin_val == "mlbb2026", f"PIN prefilled: {pin_val}")

    print("\n--- 3. TEST MLBB MARSHAL LOGIN & SCOPING ---")
    # Submit login
    driver.execute_script("submitRoleLogin();")
    assert_true(driver.execute_script("return currentSession !== null;"), "Session created successfully")
    session_id = driver.execute_script("return currentSession.accountId;")
    session_scope = driver.execute_script("return currentSession.gameScope;")
    session_role = driver.execute_script("return currentSession.role;")
    assert_true(session_id == "mlbb_marshal", f"Account ID is mlbb_marshal ({session_id})")
    assert_true(session_scope == "mlbb", f"Game scope is mlbb ({session_scope})")
    assert_true(session_role == "marshal", f"Role is marshal ({session_role})")

    # Test permissions in MLBB
    driver.execute_script("switchEsport('mlbb');")
    assert_true(driver.execute_script("return canScore('mlbb') === true;"), "canScore('mlbb') is TRUE for MLBB Marshal")
    assert_true(driver.execute_script("return isAdmin('mlbb') === false;"), "isAdmin('mlbb') is FALSE for MLBB Marshal")
    assert_true(driver.execute_script("return getEffectiveRole('mlbb') === 'marshal';"), "Effective role in MLBB is marshal")
    assert_true(driver.execute_script("return document.body.classList.contains('role-marshal');"), "body has role-marshal class in MLBB")

    # Test permissions when switched to CODM
    driver.execute_script("switchEsport('codm');")
    assert_true(driver.execute_script("return canScore('codm') === false;"), "canScore('codm') is FALSE for MLBB Marshal in CODM")
    assert_true(driver.execute_script("return isAdmin('codm') === false;"), "isAdmin('codm') is FALSE for MLBB Marshal in CODM")
    assert_true(driver.execute_script("return getEffectiveRole('codm') === 'viewer';"), "Effective role in CODM is viewer")
    assert_true(driver.execute_script("return document.body.classList.contains('role-viewer');"), "body has role-viewer class in CODM")
    assert_true(driver.execute_script("return !document.body.classList.contains('role-marshal');"), "body does NOT have role-marshal class in CODM")

    # Switch back to MLBB - permissions automatically restored
    driver.execute_script("switchEsport('mlbb');")
    assert_true(driver.execute_script("return canScore() === true;"), "canScore() automatically restored when switching back to MLBB")
    assert_true(driver.execute_script("return document.body.classList.contains('role-marshal');"), "body has role-marshal class back in MLBB")

    print("\n--- 4. TEST SESSION PERSISTENCE ACROSS REFRESH ---")
    driver.refresh()
    time.sleep(1)
    assert_true(driver.execute_script("return currentSession !== null;"), "Session preserved after page refresh")
    assert_true(driver.execute_script("return currentSession.accountId === 'mlbb_marshal';"), "Session account is still mlbb_marshal")

    print("\n--- 5. TEST LOGOUT ---")
    driver.execute_script("logoutSession();")
    assert_true(driver.execute_script("return currentSession === null;"), "Session is null after logout")
    assert_true(driver.execute_script("return getEffectiveRole() === 'viewer';"), "Effective role reset to viewer")
    assert_true(driver.execute_script("return localStorage.getItem('tcc_auth_session_v1') === null;"), "Storage key cleared")

    print("\n--- 6. TEST CODM MARSHAL LOGIN & SCOPING ---")
    driver.execute_script("openAdminLoginModal();")
    driver.execute_script("quickFillAccount('codm_marshal');")
    driver.execute_script("submitRoleLogin();")

    assert_true(driver.execute_script("return currentSession.accountId === 'codm_marshal';"), "Logged in as codm_marshal")
    driver.execute_script("switchEsport('codm');")
    assert_true(driver.execute_script("return canScore('codm') === true;"), "canScore('codm') is TRUE for CODM Marshal")
    assert_true(driver.execute_script("return canScore('mlbb') === false;"), "canScore('mlbb') is FALSE for CODM Marshal")

    driver.execute_script("switchEsport('mlbb');")
    assert_true(driver.execute_script("return canScore() === false;"), "MLBB view is locked for CODM Marshal")
    assert_true(driver.execute_script("return document.body.classList.contains('role-viewer');"), "body has role-viewer in MLBB for CODM Marshal")

    print("\n--- 7. TEST CODM ADMIN LOGIN & SCOPING ---")
    driver.execute_script("openAdminLoginModal();")
    driver.execute_script("quickFillAccount('codm_admin');")
    driver.execute_script("submitRoleLogin();")

    assert_true(driver.execute_script("return currentSession.accountId === 'codm_admin';"), "Logged in as codm_admin")
    driver.execute_script("switchEsport('codm');")
    assert_true(driver.execute_script("return isAdmin('codm') === true;"), "isAdmin('codm') is TRUE for CODM Admin")
    assert_true(driver.execute_script("return isAdmin('mlbb') === false;"), "isAdmin('mlbb') is FALSE for CODM Admin")
    assert_true(driver.execute_script("return canScore('codm') === true;"), "canScore('codm') is TRUE for CODM Admin")
    assert_true(driver.execute_script("return canScore('mlbb') === false;"), "canScore('mlbb') is FALSE for CODM Admin")

    print("\n--- 8. TEST SUPER ADMIN (TOURNAMENT DIRECTOR - ALL GAMES) ---")
    driver.execute_script("openAdminLoginModal();")
    driver.execute_script("quickFillAccount('super_admin');")
    driver.execute_script("submitRoleLogin();")

    assert_true(driver.execute_script("return currentSession.accountId === 'super_admin';"), "Logged in as super_admin")
    assert_true(driver.execute_script("return currentSession.gameScope === 'all';"), "Scope is 'all'")

    # In MLBB
    driver.execute_script("switchEsport('mlbb');")
    assert_true(driver.execute_script("return isAdmin('mlbb') === true;"), "Director has isAdmin in MLBB")
    assert_true(driver.execute_script("return canScore('mlbb') === true;"), "Director has canScore in MLBB")
    assert_true(driver.execute_script("return document.body.classList.contains('role-admin');"), "body has role-admin in MLBB")

    # In CODM
    driver.execute_script("switchEsport('codm');")
    assert_true(driver.execute_script("return isAdmin('codm') === true;"), "Director has isAdmin in CODM")
    assert_true(driver.execute_script("return canScore('codm') === true;"), "Director has canScore in CODM")
    assert_true(driver.execute_script("return document.body.classList.contains('role-admin');"), "body has role-admin in CODM")

    print("\n--- 9. TEST SESSION EXPIRATION ---")
    # Manually expire the session
    driver.execute_script("currentSession.expiresAt = Date.now() - 5000; saveSession(currentSession);")
    expired = driver.execute_script("return loadSession() === null;")
    assert_true(expired, "loadSession() returns null when expiresAt is in the past")
    driver.refresh()
    time.sleep(1)
    assert_true(driver.execute_script("return currentSession === null;"), "currentSession is null after expired session page reload")
    assert_true(driver.execute_script("return getEffectiveRole() === 'viewer';"), "Reverted to viewer upon expiration")

    # Take screenshot of login modal for proof artifact
    driver.execute_script("openAdminLoginModal();")
    time.sleep(0.5)
    artifact_path = os.path.join(r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055", "verified_login_portal_scoped.png")
    driver.save_screenshot(artifact_path)
    print(f"\nScreenshot saved to: {artifact_path}")

    print("\nALL AUTH & SESSION TESTS PASSED SUCCESSFULLY! 🎉")

finally:
    driver.quit()
