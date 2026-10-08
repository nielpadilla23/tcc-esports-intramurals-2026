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
options.add_argument('--window-size=1400,980')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"❌ FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

try:
    print("=================================================================")
    print("--- 1. LOAD INDEX.HTML AND INITIALIZE RESULTS DATABASE ---")
    print("=================================================================")
    driver.get('file:///' + html_path)
    time.sleep(1)

    # Clear storage and initialize clean state
    driver.execute_script("localStorage.clear(); sessionStorage.clear();")
    driver.get('file:///' + html_path)
    time.sleep(1)

    db_defined = driver.execute_script("return typeof TournamentResultsDB !== 'undefined';")
    assert_true(db_defined, "TournamentResultsDB module is globally defined")

    tables_ready = driver.execute_script("return Boolean(TournamentResultsDB.tables && TournamentResultsDB.tables.matches && TournamentResultsDB.tables.codm_br_scores && TournamentResultsDB.tables.college_standings && TournamentResultsDB.tables.audit_logs);")
    assert_true(tables_ready, "All relational tables (matches, codm_br_scores, college_standings, audit_logs) are ready")

    print("\n=================================================================")
    print("--- 2. TEST SAVING MLBB SCORES & IMMEDIATE DB PERSISTENCE ---")
    print("=================================================================")
    # Login as admin to score
    driver.execute_script("setRole('admin', false);")
    time.sleep(0.5)

    # Switch to MLBB
    driver.execute_script("openEsportDashboard('mlbb');")
    time.sleep(0.5)

    # Seed the bracket
    driver.execute_script("populateSeedsToBracket(false);")
    time.sleep(0.5)

    # Save MLBB match score: UB QF1 -> 2 - 0
    driver.execute_script("setPlayoffScore('ub_qf1', 2, 0);")
    time.sleep(0.3)

    m1 = driver.execute_script("return TournamentResultsDB.tables.matches['mlbb_ub_qf1'];")
    assert_true(m1 is not None, "mlbb_ub_qf1 committed into results database")
    assert_true(m1['score1'] == 2 and m1['score2'] == 0, f"mlbb_ub_qf1 scores are 2 - 0 (actual: {m1['score1']} - {m1['score2']})")
    assert_true(m1['status'] == 'completed', "mlbb_ub_qf1 status is 'completed'")
    assert_true(m1['winner'] == 'CIT', f"mlbb_ub_qf1 winner is CIT (actual: {m1['winner']})")

    # Save another MLBB match: UB QF2 -> CCJPS 2 - 1 CAS
    driver.execute_script("setPlayoffScore('ub_qf2', 2, 1);")
    time.sleep(0.3)

    m2 = driver.execute_script("return TournamentResultsDB.tables.matches['mlbb_ub_qf2'];")
    assert_true(m2 is not None, "mlbb_ub_qf2 committed into results database")
    assert_true(m2['winner'] == m2['team1'], f"mlbb_ub_qf2 winner is team1 ({m2['winner']})")

    # Check audit log contains entries
    audit_len = driver.execute_script("return TournamentResultsDB.tables.audit_logs.length;")
    assert_true(audit_len >= 2, f"Audit log contains {audit_len} entries for MLBB match scoring")

    # Check college standings updated
    cit_wins = driver.execute_script("return TournamentResultsDB.tables.college_standings['CIT'] ? TournamentResultsDB.tables.college_standings['CIT'].mlbb_wins : 0;")
    assert_true(cit_wins == 1, f"CIT has {cit_wins} MLBB series win in database standings")

    print("\n=================================================================")
    print("--- 3. TEST CODM 5v5 MULTIPLAYER SCORING & DB COMMIT ---")
    print("=================================================================")
    # Switch to CODM MP
    driver.execute_script("openEsportDashboard('codm', 'mp');")
    time.sleep(0.5)

    # Seed CODM bracket & score UB QF2
    driver.execute_script("populateSeedsToBracket(false);")
    time.sleep(0.3)
    driver.execute_script("setPlayoffScore('ub_qf2', 2, 0);")
    time.sleep(0.3)

    codm_m1 = driver.execute_script("return TournamentResultsDB.tables.matches['codm_ub_qf2'];")
    assert_true(codm_m1 is not None, "codm_ub_qf2 committed into results database")
    assert_true(codm_m1['score1'] == 2 and codm_m1['score2'] == 0, "CODM score recorded as 2 - 0")
    assert_true(codm_m1['esport'] == 'codm', "Record esport is 'codm'")

    print("\n=================================================================")
    print("--- 4. TEST CODM BATTLE ROYALE ROUNDS & FULL TOURNAMENT SIMULATION ---")
    print("=================================================================")
    driver.execute_script("switchCodmMode('br');")
    time.sleep(0.5)

    # Simulate all 8 rounds
    driver.execute_script("simulateCodmBrTournament();")
    time.sleep(0.5)

    br_scores_count = driver.execute_script("return Object.keys(TournamentResultsDB.tables.codm_br_scores).length;")
    assert_true(br_scores_count == 56, f"CODM BR scores has {br_scores_count} total entries (8 rounds * 7 colleges)")

    r1_ccjps = driver.execute_script("return TournamentResultsDB.tables.codm_br_scores['br_r1_CCJPS'];")
    assert_true(r1_ccjps is not None, "br_r1_CCJPS exists in results database")
    assert_true(r1_ccjps['placement'] is not None, f"CCJPS Round 1 placement is {r1_ccjps['placement']}")
    assert_true(r1_ccjps['total_points'] > 0, f"CCJPS Round 1 total points is {r1_ccjps['total_points']}")

    # Verify overall aggregated standings
    standings_list = driver.execute_script("return Object.values(TournamentResultsDB.tables.college_standings);")
    assert_true(len(standings_list) == 8, "Aggregated college standings has 8 college departments")
    print(f"Standings computed: Top college is {standings_list[0]['name']} with {standings_list[0]['championship_points']} points")

    print("\n=================================================================")
    print("--- 5. TEST DEDICATED RESULTS DATABASE MODAL & SUB-TABS ---")
    print("=================================================================")
    driver.execute_script("openResultsDatabaseModal();")
    time.sleep(0.5)

    modal_open = not driver.execute_script("return document.getElementById('tournamentDatabaseModal').classList.contains('hidden');")
    assert_true(modal_open, "Results Database modal is open and visible")

    # Capture Modal Overview screenshot
    screenshot_modal = os.path.join(artifacts_dir, "results_database_modal_overview.png")
    driver.save_screenshot(screenshot_modal)
    print(f"Screenshot saved: {screenshot_modal}")

    # Switch to MLBB Sub-Tab
    driver.execute_script("TournamentResultsDB.setSubTab('mlbb');")
    time.sleep(0.3)
    active_tab = driver.execute_script("return TournamentResultsDB.activeSubTab;")
    assert_true(active_tab == 'mlbb', "Active subtab switched to 'mlbb'")

    screenshot_mlbb_tab = os.path.join(artifacts_dir, "results_database_mlbb_subtab.png")
    driver.save_screenshot(screenshot_mlbb_tab)
    print(f"Screenshot saved: {screenshot_mlbb_tab}")

    # Switch to CODM Battle Royale Sub-Tab
    driver.execute_script("TournamentResultsDB.setSubTab('codm_br');")
    time.sleep(0.3)
    active_tab = driver.execute_script("return TournamentResultsDB.activeSubTab;")
    assert_true(active_tab == 'codm_br', "Active subtab switched to 'codm_br'")

    screenshot_br_tab = os.path.join(artifacts_dir, "results_database_br_subtab.png")
    driver.save_screenshot(screenshot_br_tab)
    print(f"Screenshot saved: {screenshot_br_tab}")

    # Switch to Overall Standings Sub-Tab
    driver.execute_script("TournamentResultsDB.setSubTab('standings');")
    time.sleep(0.3)
    active_tab = driver.execute_script("return TournamentResultsDB.activeSubTab;")
    assert_true(active_tab == 'standings', "Active subtab switched to 'standings'")

    screenshot_standings_tab = os.path.join(artifacts_dir, "results_database_standings_subtab.png")
    driver.save_screenshot(screenshot_standings_tab)
    print(f"Screenshot saved: {screenshot_standings_tab}")

    # Close modal
    driver.execute_script("closeResultsDatabaseModal();")
    time.sleep(0.3)
    modal_closed = driver.execute_script("return document.getElementById('tournamentDatabaseModal').classList.contains('hidden');")
    assert_true(modal_closed, "Results Database modal closed cleanly")

    print("\n=================================================================")
    print("--- 6. TEST MAIN NAVIGATION TAB (INLINE RESULTS DATABASE) ---")
    print("=================================================================")
    driver.execute_script("switchTab('database');")
    time.sleep(0.5)

    view_db_visible = not driver.execute_script("return document.getElementById('view-database').classList.contains('hidden');")
    assert_true(view_db_visible, "#view-database is visible when database tab is active")

    screenshot_inline_view = os.path.join(artifacts_dir, "results_database_inline_view.png")
    driver.save_screenshot(screenshot_inline_view)
    print(f"Screenshot saved: {screenshot_inline_view}")

    print("\n=================================================================")
    print("--- 7. TEST FILTERING & SEARCH ENGINE ---")
    print("=================================================================")
    # Filter by college CCJPS
    driver.execute_script("TournamentResultsDB.setFilterCollege('CCJPS');")
    time.sleep(0.3)
    filtered_matches = driver.execute_script("return TournamentResultsDB.getFilteredMatches().length;")
    print(f"Matches matching CCJPS filter: {filtered_matches}")
    assert_true(filtered_matches >= 1, "Filter by college 'CCJPS' correctly returns matching matches")

    # Search query
    driver.execute_script("TournamentResultsDB.setFilterCollege('ALL'); TournamentResultsDB.setSearchQuery('CIT');")
    time.sleep(0.3)
    search_matches = driver.execute_script("return TournamentResultsDB.getFilteredMatches().length;")
    print(f"Matches matching search 'CIT': {search_matches}")
    assert_true(search_matches >= 1, "Search query 'CIT' correctly filters records")

    # Clear filters
    driver.execute_script("TournamentResultsDB.clearFilters();")
    time.sleep(0.3)
    assert_true(driver.execute_script("return TournamentResultsDB.filterCollege === 'ALL' && TournamentResultsDB.searchQuery === '';"), "Filters cleared successfully")

    print("\n=================================================================")
    print("--- 8. TEST SQL, CSV, AND JSON EXPORTS ---")
    print("=================================================================")
    # SQL export
    driver.execute_script("exportDatabaseAsSQL();")
    print("✅ exportDatabaseAsSQL() executed without exceptions")

    # CSV export
    driver.execute_script("exportDatabaseAsCSV('matches');")
    driver.execute_script("exportDatabaseAsCSV('br_scores');")
    driver.execute_script("exportDatabaseAsCSV('standings');")
    print("✅ exportDatabaseAsCSV() executed for all 3 tables without exceptions")

    # JSON dump
    driver.execute_script("exportTournamentDatabaseJSON();")
    print("✅ exportTournamentDatabaseJSON() executed without exceptions")

    print("\n=================================================================")
    print("--- 9. TEST MATCH RESET DB AUDITING ---")
    print("=================================================================")
    driver.execute_script("openEsportDashboard('mlbb');")
    time.sleep(0.3)
    driver.execute_script("resetMatchScore('ub_qf1');")
    time.sleep(0.3)

    reset_m = driver.execute_script("return TournamentResultsDB.tables.matches['mlbb_ub_qf1'];")
    assert_true(reset_m['score1'] is None and reset_m['score2'] is None, "mlbb_ub_qf1 scores reset to null in database")
    assert_true(reset_m['status'] == 'scheduled', "mlbb_ub_qf1 status reverted to scheduled")

    last_audit = driver.execute_script("return TournamentResultsDB.tables.audit_logs[0];")
    assert_true('MATCH_RESET' in last_audit['action'], f"Audit log contains reset action: {last_audit['action']}")

    print("\n=================================================================")
    print("🎉 ALL 9 TEST SUITES PASSED FLAWLESSLY!")
    print("=================================================================")

finally:
    driver.quit()
