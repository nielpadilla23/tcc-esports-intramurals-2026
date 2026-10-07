import os, time, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.stdout.reconfigure(encoding='utf-8')
options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1600,1200')
driver = webdriver.Chrome(options=options)

file_path = os.path.abspath('index.html').replace(os.sep, '/')
driver.get(f'file:///{file_path}')
time.sleep(1.5)

# 1. Switch to CODM
print("--- TEST 1: Open CODM Dashboard ---")
driver.execute_script('openEsportDashboard("codm");')
time.sleep(1)
esport = driver.execute_script('return currentEsport;')
assert esport == 'codm', f"Expected codm, got {esport}"
print(f"Esport: {esport} - OK")

# 2. Simulate tournament as admin
print("\n--- TEST 2: Fast Sim Bracket as Admin ---")
driver.execute_script('currentUserRole = "admin"; updateAdminUI(); simulateDoubleElimination();')
time.sleep(1)

m1_sim = driver.execute_script('return PLAYOFF_DATA.ub_qf1;')
gf8_sim = driver.execute_script('return PLAYOFF_DATA.gf8;')
champ_sim = driver.execute_script('return document.getElementById("podiumChampionName")?.innerText;')
print(f"UB QF1 after sim: {m1_sim['team1']} vs {m1_sim['team2']} -> Winner: {m1_sim['winner']} ({m1_sim['s1']}-{m1_sim['s2']})")
print(f"GF8 after sim: {gf8_sim['team1']} vs {gf8_sim['team2']} -> Winner: {gf8_sim['winner']}")
print(f"Podium Champion: {champ_sim}")
assert m1_sim['winner'] is not None, "UB QF1 should have a winner"
assert gf8_sim['winner'] is not None, "GF8 should have a winner"

# 3. Test single match score reset cascading invalidation
print("\n--- TEST 3: Cascading Invalidation on Single Match Reset ---")
driver.execute_script('resetMatchScore("ub_qf1");')
time.sleep(0.5)

m1_after = driver.execute_script('return PLAYOFF_DATA.ub_qf1;')
ub_sf1_after = driver.execute_script('return PLAYOFF_DATA.ub_sf1;')
gf8_after = driver.execute_script('return PLAYOFF_DATA.gf8;')
champ_after = driver.execute_script('return document.getElementById("podiumChampionName")?.innerText;')

print(f"UB QF1 after reset: s1={m1_after['s1']}, s2={m1_after['s2']}, winner={m1_after['winner']}, games={m1_after.get('games')}")
print(f"UB SF1 after reset: team1={ub_sf1_after['team1']}, s1={ub_sf1_after['s1']}, s2={ub_sf1_after['s2']}, winner={ub_sf1_after['winner']}")
print(f"GF8 after reset: team1={gf8_after['team1']}, s1={gf8_after['s1']}, s2={gf8_after['s2']}, winner={gf8_after['winner']}")
print(f"Podium Champion after reset: {champ_after}")

assert m1_after['winner'] is None, "UB QF1 winner should be null"
assert m1_after['s1'] is None, "UB QF1 s1 should be null"
assert ub_sf1_after['team1'] is None, "UB SF1 team1 should be null because UB QF1 was reset"
assert ub_sf1_after['winner'] is None, "UB SF1 winner should be null because team1 is missing"
assert ub_sf1_after['s1'] is None, "UB SF1 s1 should be null"
assert gf8_after['winner'] is None, "GF8 winner should be null because upstream bracket was reset"
print("Cascading invalidation verified successfully!")

# 4. Test Table Marshal permission for resetMatchScore
print("\n--- TEST 4: Table Marshal Permission for resetMatchScore ---")
# Re-simulate to have scores
driver.execute_script('currentUserRole = "admin"; simulateDoubleElimination();')
time.sleep(0.5)
# Switch to marshal
driver.execute_script('currentUserRole = "marshal"; updateAdminUI();')
driver.execute_script('resetMatchScore("ub_qf2");')
time.sleep(0.5)
m2_marshal = driver.execute_script('return PLAYOFF_DATA.ub_qf2;')
print(f"UB QF2 after marshal reset: s1={m2_marshal['s1']}, s2={m2_marshal['s2']}, winner={m2_marshal['winner']}")
assert m2_marshal['winner'] is None, "Table Marshal should be able to reset match score"
print("Table Marshal reset verified successfully!")

# 5. Test Spectator calling resetMatchScore prompts login modal
print("\n--- TEST 5: Viewer Prompted to Log In on Reset ---")
driver.execute_script('currentUserRole = "viewer"; updateAdminUI();')
driver.execute_script('resetMatchScore("ub_qf3");')
time.sleep(0.5)
login_modal_open = driver.execute_script('return !document.getElementById("adminLoginModal").classList.contains("hidden");')
toast_text = driver.execute_script('return document.getElementById("floatingToast")?.innerText || "";')
print(f"Login modal open after viewer reset: {login_modal_open}")
print(f"Toast message: {toast_text}")
assert login_modal_open, "Admin login modal should open when viewer tries to reset"
driver.execute_script('closeAdminLoginModal();')

# 6. Test Tournament-wide Reset Scores
print("\n--- TEST 6: Tournament-wide Reset Scores as Admin ---")
driver.execute_script('currentUserRole = "admin"; updateAdminUI(); simulateDoubleElimination();')
time.sleep(0.5)
# Check all matches scored
scored_before = driver.execute_script('return Object.values(PLAYOFF_DATA).filter(m => m.s1 !== null).length;')
print(f"Scored matches before resetTournamentScores: {scored_before}")
assert scored_before > 0, "Should have scored matches"

# Run resetTournamentScores
driver.execute_script('resetTournamentScores();')
time.sleep(0.5)
scored_after = driver.execute_script('return Object.values(PLAYOFF_DATA).filter(m => m.s1 !== null).length;')
games_after = driver.execute_script('return Object.values(PLAYOFF_DATA).filter(m => Boolean(m.games)).length;')
print(f"Scored matches after resetTournamentScores: {scored_after}")
print(f"Matches with lingering games after reset: {games_after}")
assert scored_after == 0, f"Expected 0 scored matches, got {scored_after}"
assert games_after == 0, f"Expected 0 lingering games, got {games_after}"

# 7. Test persistence across page reload
print("\n--- TEST 7: Persistence Across Page Reload ---")
driver.refresh()
time.sleep(1.5)
driver.execute_script('openEsportDashboard("codm");')
time.sleep(1)
scored_reload = driver.execute_script('return Object.values(PLAYOFF_DATA).filter(m => m.s1 !== null).length;')
print(f"Scored matches after reload: {scored_reload}")
assert scored_reload == 0, f"Expected 0 scored matches after reload, got {scored_reload}"
print("Persistence after reload verified!")

# 8. Test Modal Blank / Reset Preset
print("\n--- TEST 8: Score Edit Modal Blank / Reset Preset ---")
driver.execute_script('currentUserRole = "admin"; updateAdminUI();')
# Score match 1
driver.execute_script('setPlayoffScore("ub_qf1", 2, 0);')
time.sleep(0.5)
print("UB QF1 scored 2-0:", driver.execute_script('return PLAYOFF_DATA.ub_qf1.winner;'))
# Open modal
driver.execute_script('openScoreModal("ub_qf1");')
time.sleep(0.5)
# Click Blank / Reset preset
driver.execute_script('setModalScorePreset(null, null);')
s1_val = driver.execute_script('return document.getElementById("modalScore1").value;')
s2_val = driver.execute_script('return document.getElementById("modalScore2").value;')
banner_text = driver.execute_script('return document.getElementById("modalStatusBanner").innerText;')
print(f"Modal inputs after Blank preset: s1='{s1_val}', s2='{s2_val}'")
print(f"Modal banner text: {banner_text}")
assert s1_val == '', "Score 1 should be empty"
assert s2_val == '', "Score 2 should be empty"
# Save modal score with blanks (triggers reset)
driver.execute_script('saveModalScore();')
time.sleep(0.5)
m1_modal_reset = driver.execute_script('return PLAYOFF_DATA.ub_qf1;')
print(f"UB QF1 after saving blank modal score: s1={m1_modal_reset['s1']}, winner={m1_modal_reset['winner']}")
assert m1_modal_reset['s1'] is None, "UB QF1 s1 should be null"
assert m1_modal_reset['winner'] is None, "UB QF1 winner should be null"

# Save screenshot of clean reset bracket
artifacts_dir = r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055"
screenshot_path = os.path.join(artifacts_dir, "verified_reset_score_working.png")
driver.save_screenshot(screenshot_path)
print(f"Screenshot saved to: {screenshot_path}")

driver.quit()
print("\nALL 8 TESTS PASSED SUCCESSFULLY!")
