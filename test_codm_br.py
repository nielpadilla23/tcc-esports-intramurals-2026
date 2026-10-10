import os
import sys
import time

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
options.add_argument('--window-size=1366,950')

driver = webdriver.Chrome(options=options)

def assert_true(cond, msg):
    if not cond:
        print(f"❌ FAILED: {msg}")
        sys.exit(1)
    else:
        print(f"✅ PASS: {msg}")

try:
    print("--- 1. LOAD INDEX.HTML AND NAVIGATE TO CODM BATTLE ROYALE ---")
    driver.get('file:///' + html_path)
    time.sleep(0.5)

    # Clear previous local storage and disable background cloud sync for deterministic test
    driver.execute_script("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('tcc_firebase_disabled_v1', 'true');")
    driver.get('file:///' + html_path)
    time.sleep(1)
    driver.execute_script("initAdminAuth();")

    # Navigate to CODM Battle Royale directly from Landing Hub
    driver.execute_script("openEsportDashboard('codm', 'br');")
    time.sleep(0.5)

    curr_esport = driver.execute_script("return currentEsport;")
    curr_mode = driver.execute_script("return codmMode;")
    assert_true(curr_esport == 'codm', "Active esport is CODM")
    assert_true(curr_mode == 'br', "Active CODM mode is 'br' (Battle Royale)")

    # Check container visibility
    mode_bar_visible = not driver.execute_script("return document.getElementById('codmModeBar').classList.contains('hidden');")
    br_container_visible = not driver.execute_script("return document.getElementById('codmBattleRoyaleContainer').classList.contains('hidden');")
    mp_container_hidden = driver.execute_script("return document.getElementById('mainMpTournamentContainer').classList.contains('hidden');")
    assert_true(mode_bar_visible, "#codmModeBar is visible")
    assert_true(br_container_visible, "#codmBattleRoyaleContainer is visible")
    assert_true(mp_container_hidden, "#mainMpTournamentContainer is hidden in BR mode")

    screenshot_overview = os.path.join(artifacts_dir, "codm_br_dashboard_overview.png")
    driver.save_screenshot(screenshot_overview)
    print(f"Screenshot saved: {screenshot_overview}")

    print("\n--- 2. TEST DUAL MODE SWITCHING (MP <-> BR) ---")
    # Switch to MP
    driver.execute_script("switchCodmMode('mp');")
    time.sleep(0.3)
    assert_true(driver.execute_script("return codmMode === 'mp';"), "Mode switched to MP")
    assert_true(not driver.execute_script("return document.getElementById('mainMpTournamentContainer').classList.contains('hidden');"), "#mainMpTournamentContainer is now visible")
    assert_true(driver.execute_script("return document.getElementById('codmBattleRoyaleContainer').classList.contains('hidden');"), "#codmBattleRoyaleContainer is now hidden")

    # Switch back to BR
    driver.execute_script("switchCodmMode('br');")
    time.sleep(0.3)
    assert_true(driver.execute_script("return codmMode === 'br';"), "Mode switched back to BR")
    assert_true(not driver.execute_script("return document.getElementById('codmBattleRoyaleContainer').classList.contains('hidden');"), "#codmBattleRoyaleContainer is visible again")
    assert_true(driver.execute_script("return document.getElementById('mainMpTournamentContainer').classList.contains('hidden');"), "#mainMpTournamentContainer is hidden again")

    print("\n--- 3. TEST RBAC AUTH GUARD FOR BR SCORE ENTRY ---")
    # As viewer, attempt to open score modal should trigger auth toast and modal
    driver.execute_script("openBrScoreModal(1);")
    time.sleep(0.3)
    login_modal_opened = not driver.execute_script("return document.getElementById('adminLoginModal').classList.contains('hidden');")
    assert_true(login_modal_opened, "Auth required modal shown when viewer tries to edit BR scores")
    driver.execute_script("closeAdminLoginModal();")

    # Log in as CODM Table Marshal using PIN 'codm2026'
    driver.execute_script("submitAdminPin('codm2026');")
    time.sleep(0.3)
    assert_true(driver.execute_script("return canScore('codm');"), "CODM Marshal canScore('codm') is True")

    print("\n--- 4. TEST BR SCORE ENTRY MODAL & SCORING CALCULATIONS (ROUND 1) ---")
    driver.execute_script("openBrScoreModal(1);")
    time.sleep(0.3)
    br_modal_open = not driver.execute_script("return document.getElementById('codmBrScoreModal').classList.contains('hidden');")
    assert_true(br_modal_open, "#codmBrScoreModal is open")

    # Check 7 college teams in modal
    teams_count = driver.execute_script("return CODM_BR_TEAMS.length;")
    assert_true(teams_count == 7, "7 Competing Colleges in CODM BR")

    # Assign Placements and Kills for Round 1:
    # CCJPS: 1st (10 pts) + 5 kills = 15 pts
    # CBA:   2nd (8 pts)  + 4 kills = 12 pts
    # CHM:   3rd (6 pts)  + 3 kills = 9 pts
    # CLIS:  4th (5 pts)  + 2 kills = 7 pts
    # CIT:   5th (4 pts)  + 1 kill  = 5 pts
    # COED:  6th (3 pts)  + 0 kills = 3 pts
    # CAS:   7th (2 pts)  + 0 kills = 2 pts
    driver.execute_script("""
      document.getElementById('brPlacement_CCJPS').value = '1';
      document.getElementById('brKills_CCJPS').value = '5';

      document.getElementById('brPlacement_CBA').value = '2';
      document.getElementById('brKills_CBA').value = '4';

      document.getElementById('brPlacement_CHM').value = '3';
      document.getElementById('brKills_CHM').value = '3';

      document.getElementById('brPlacement_CLIS').value = '4';
      document.getElementById('brKills_CLIS').value = '2';

      document.getElementById('brPlacement_CIT').value = '5';
      document.getElementById('brKills_CIT').value = '1';

      document.getElementById('brPlacement_COED').value = '6';
      document.getElementById('brKills_COED').value = '0';

      document.getElementById('brPlacement_CAS').value = '7';
      document.getElementById('brKills_CAS').value = '0';

      updateBrModalCalculations();
    """)
    time.sleep(0.3)

    # Check calculated point badges in modal
    ccjps_pts_badge = driver.execute_script("return document.getElementById('brPts_CCJPS').innerText;")
    assert_true(ccjps_pts_badge == "15 pts", f"CCJPS points badge is 15 pts (got {ccjps_pts_badge})")

    cba_pts_badge = driver.execute_script("return document.getElementById('brPts_CBA').innerText;")
    assert_true(cba_pts_badge == "12 pts", f"CBA points badge is 12 pts (got {cba_pts_badge})")

    # Test squad kills clamping for 28-player lobby (max 24 enemy eliminations per round)
    driver.execute_script("""
      document.getElementById('brKills_CCJPS').value = '50';
      updateBrModalCalculations();
    """)
    clamped_val = driver.execute_script("return document.getElementById('brKills_CCJPS').value;")
    assert_true(clamped_val == '24', f"Manual kill input clamped to 24 for 28-player lobby (got {clamped_val})")

    driver.execute_script("stepBrKills('CCJPS', 5);")
    stepped_val = driver.execute_script("return document.getElementById('brKills_CCJPS').value;")
    assert_true(stepped_val == '24', f"Stepping kills beyond 24 clamped to 24 (got {stepped_val})")

    # Reset CCJPS kills back to 5 for Round 1 test
    driver.execute_script("""
      document.getElementById('brKills_CCJPS').value = '5';
      updateBrModalCalculations();
    """)

    # Check duplicate detection validation alert
    driver.execute_script("""
      document.getElementById('brPlacement_CAS').value = '1';
      updateBrModalCalculations();
    """)
    dup_alert = driver.execute_script("return document.getElementById('brModalValidationAlert').innerText;")
    assert_true("Duplicate placement" in dup_alert, f"Duplicate placement warning shown: {dup_alert}")

    # Restore CAS to 7th
    driver.execute_script("""
      document.getElementById('brPlacement_CAS').value = '7';
      updateBrModalCalculations();
    """)
    valid_alert = driver.execute_script("return document.getElementById('brModalValidationAlert').innerText;")
    assert_true("All 7 placements" in valid_alert, "All 7 placements uniquely assigned validated")

    screenshot_modal = os.path.join(artifacts_dir, "codm_br_score_editor_modal.png")
    driver.save_screenshot(screenshot_modal)
    print(f"Modal screenshot saved: {screenshot_modal}")

    # Trigger Save Round 1 -> Verify confirmation message to proceed is prompted
    driver.execute_script("saveBrRoundFromModal();")
    time.sleep(0.4)

    confirm_visible = driver.execute_script("return !document.getElementById('actionConfirmModal').classList.contains('hidden');")
    assert_true(confirm_visible, "Action confirmation modal displayed before saving BR scores")

    confirm_title = driver.execute_script("return document.getElementById('confirmModalTitle').innerText;")
    confirm_msg = driver.execute_script("return document.getElementById('confirmModalMessage').innerText;")
    confirm_btn = driver.execute_script("return document.getElementById('confirmModalBtnText').innerText;")

    assert_true("round 1" in confirm_title.lower() or "br" in confirm_title.lower(), f"Confirmation title specifies round: {confirm_title}")
    assert_true("proceed" in confirm_msg.lower(), f"Confirmation message contains 'proceed': {confirm_msg}")
    assert_true("proceed" in confirm_btn.lower(), f"Confirmation button contains 'proceed': {confirm_btn}")

    screenshot_confirm = os.path.join(artifacts_dir, "codm_br_save_confirm_modal.png")
    driver.save_screenshot(screenshot_confirm)
    print(f"Confirmation modal screenshot saved: {screenshot_confirm}")

    # Test Cancel first
    driver.execute_script("closeActionConfirmModal();")
    time.sleep(0.3)
    confirm_closed = driver.execute_script("return document.getElementById('actionConfirmModal').classList.contains('hidden');")
    score_still_open = driver.execute_script("return !document.getElementById('codmBrScoreModal').classList.contains('hidden');")
    assert_true(confirm_closed and score_still_open, "Canceling confirmation keeps score editor open with inputs preserved")

    # Trigger Save again and confirm proceed
    driver.execute_script("""
      saveBrRoundFromModal();
      executePendingConfirmedAction();
    """)
    time.sleep(0.5)
    assert_true(driver.execute_script("return document.getElementById('codmBrScoreModal').classList.contains('hidden');"), "Score modal closed after confirmed save")

    # Verify Round 1 status is completed
    r1_status = driver.execute_script("return CODM_BR_DATA.rounds[1].status;")
    assert_true(r1_status == 'completed', "Round 1 status is completed")

    # Verify Leaderboard standings after Round 1
    standings = driver.execute_script("return calculateBrStandings();")
    assert_true(standings[0]['id'] == 'CCJPS' and standings[0]['totalPoints'] == 15, f"Rank 1 is CCJPS with 15 pts")
    assert_true(standings[1]['id'] == 'CBA' and standings[1]['totalPoints'] == 12, f"Rank 2 is CBA with 12 pts")
    assert_true(standings[2]['id'] == 'CHM' and standings[2]['totalPoints'] == 9, f"Rank 3 is CHM with 9 pts")
    assert_true(standings[6]['id'] == 'CAS' and standings[6]['totalPoints'] == 2, f"Rank 7 is CAS with 2 pts")
    # Verify Podium cards in DOM after 1 round (in-progress)
    podium_r1_html = driver.execute_script("return document.getElementById('brPodiumContainer').innerHTML;")
    assert_true("1st" in podium_r1_html, "1st place shown in podium when rounds are in progress")
    assert_true("2nd" in podium_r1_html, "2nd place shown in podium when rounds are in progress")
    assert_true("3rd" in podium_r1_html, "3rd place shown in podium when rounds are in progress")
    assert_true("Champion (Gold)" not in podium_r1_html, "Champion (Gold) not shown yet while rounds are in progress")
    assert_true("1st Runner Up" not in podium_r1_html, "1st Runner Up not shown")
    assert_true("2nd Runner Up" not in podium_r1_html, "2nd Runner Up not shown")

    # Verify Podium container is strictly hidden in Marshal mode
    podium_hidden_for_marshal = driver.execute_script("return window.getComputedStyle(document.getElementById('brPodiumContainer')).display === 'none';")
    assert_true(podium_hidden_for_marshal, "#brPodiumContainer is hidden in Marshal view (.marshal-hide)")

    # Verify Standings table headers and columns after Round 1 (only done rounds and total points)
    table_head_html = driver.execute_script("return document.getElementById('brStandingsTableHead').innerHTML;")
    assert_true("R1" in table_head_html, "R1 column header is present in standings table")
    assert_true("R2" not in table_head_html, "R2 column header is NOT shown when only Round 1 is done")
    assert_true("R8" not in table_head_html, "R8 column header is NOT shown when only Round 1 is done")
    assert_true("Kills" not in table_head_html, "Separate Kills column is omitted for cleaner design")
    assert_true("Place Pts" not in table_head_html, "Separate Place Pts column is omitted for cleaner design")
    assert_true("Total Pts" in table_head_html, "Total Pts column header is present")

    screenshot_r1 = os.path.join(artifacts_dir, "codm_br_round1_clean_leaderboard.png")
    driver.save_screenshot(screenshot_r1)
    print(f"Round 1 clean leaderboard screenshot saved: {screenshot_r1}")

    print("\n--- 5. TEST FAST SIMULATION OF ALL 8 ROUNDS ---")
    # Log in as Tournament Director (Super Admin)
    driver.execute_script("submitAdminPin('admin2026');")
    time.sleep(0.3)
    assert_true(driver.execute_script("return isAdmin();"), "Super Admin isAdmin() is True")
    podium_visible_for_admin = driver.execute_script("return window.getComputedStyle(document.getElementById('brPodiumContainer')).display !== 'none';")
    assert_true(podium_visible_for_admin, "#brPodiumContainer is visible in Admin view")

    # Run tournament simulation
    driver.execute_script("simulateCodmBrTournament();")
    time.sleep(0.5)

    # Verify all 8 rounds are completed
    completed_rounds = driver.execute_script("""
      return Object.values(CODM_BR_DATA.rounds).filter(r => r.status === 'completed').length;
    """)
    assert_true(completed_rounds == 8, f"All 8 rounds completed (got {completed_rounds})")

    # Verify realistic 28-player lobby simulation constraints across all 8 rounds (7 squads of 4 players)
    round_kills_data = driver.execute_script("""
      const data = [];
      for (let r = 1; r <= 8; r++) {
        const rnd = CODM_BR_DATA.rounds[r];
        const killsList = Object.values(rnd.results).map(res => res.kills);
        const placementsList = Object.values(rnd.results).map(res => res.placement);
        const totalRoundKills = killsList.reduce((a, b) => a + b, 0);
        data.push({
          round: r,
          killsList: killsList,
          placementsList: placementsList,
          totalRoundKills: totalRoundKills
        });
      }
      return data;
    """)

    for rnd_info in round_kills_data:
        r_num = rnd_info['round']
        tot_k = rnd_info['totalRoundKills']
        k_list = rnd_info['killsList']
        p_list = rnd_info['placementsList']
        assert_true(20 <= tot_k <= 24, f"Round {r_num} total kills is {tot_k} (calibrated between 20 and 24 enemy eliminations for 28-player lobby)")
        assert_true(all(0 <= k <= 24 for k in k_list), f"Round {r_num} all squad kills are between 0 and 24: {k_list}")
        assert_true(sorted(p_list) == [1, 2, 3, 4, 5, 6, 7], f"Round {r_num} has unique placements 1st-7th: {sorted(p_list)}")

    # Verify progress badge
    badge_text = driver.execute_script("return document.getElementById('brProgressBadge').innerText;")
    assert_true("8 of 8 Complete" in badge_text or "Champion Decided" in badge_text, f"Progress badge shows completion: {badge_text}")

    # Verify standings mathematical integrity across all 8 rounds
    standings_sim = driver.execute_script("return calculateBrStandings();")
    for s in standings_sim:
        sum_kills = sum(rh['kills'] for rh in s['roundHistory'])
        sum_plc_pts = sum(rh['placementPoints'] for rh in s['roundHistory'])
        sum_total = sum(rh['totalPoints'] for rh in s['roundHistory'])
        assert_true(s['totalKills'] == sum_kills, f"Team {s['id']} total kills match sum")
        assert_true(s['totalPlacementPoints'] == sum_plc_pts, f"Team {s['id']} placement pts match sum")
        assert_true(s['totalPoints'] == sum_total, f"Team {s['id']} total points match sum ({s['totalPoints']} == {sum_total})")

    # Verify strictly descending order of total points
    for i in range(len(standings_sim) - 1):
        assert_true(standings_sim[i]['totalPoints'] >= standings_sim[i+1]['totalPoints'],
                    f"Rank {i+1} ({standings_sim[i]['totalPoints']}) >= Rank {i+2} ({standings_sim[i+1]['totalPoints']})")

    print(f"Simulated Champion: {standings_sim[0]['name']} ({standings_sim[0]['mascot']}) with {standings_sim[0]['totalPoints']} PTS ({standings_sim[0]['totalKills']} Kills)!")

    # Verify Podium cards in DOM when all 8 rounds are complete
    podium_html = driver.execute_script("return document.getElementById('brPodiumContainer').innerHTML;")
    assert_true("Champion (Gold)" in podium_html, "Champion (Gold) marked in podium when all 8 rounds completed")
    assert_true("Silver" in podium_html, "Silver marked in podium when all 8 rounds completed")
    assert_true("Bronze" in podium_html, "Bronze marked in podium when all 8 rounds completed")

    # Verify Standings table headers when all 8 rounds are complete
    table_head_all_html = driver.execute_script("return document.getElementById('brStandingsTableHead').innerHTML;")
    assert_true("R1" in table_head_all_html and "R8" in table_head_all_html, "All 8 round columns present when tournament concludes")
    assert_true("Kills" not in table_head_all_html, "Kills column remains omitted")
    assert_true("Place Pts" not in table_head_all_html, "Place Pts column remains omitted")
    assert_true("Total Pts" in table_head_all_html, "Total Pts column present")

    screenshot_sim = os.path.join(artifacts_dir, "codm_br_simulated_leaderboard.png")
    driver.save_screenshot(screenshot_sim)
    print(f"Simulated leaderboard screenshot saved: {screenshot_sim}")

    print("\n--- 6. TEST ROUND TABS SELECTION & TAB NAVIGATION ---")
    driver.execute_script("selectBrRound(5);")
    time.sleep(0.3)
    curr_selected = driver.execute_script("return selectedBrRound;")
    assert_true(curr_selected == 5, "Selected round is Round 5")
    btn_edit_text = driver.execute_script("return document.getElementById('btnEditSelectedRoundText').innerText;")
    assert_true(btn_edit_text == "Edit Round 5", f"Edit button reflects Round 5: {btn_edit_text}")

    print("\n--- 7. TEST RESET OF BR SCORES ---")
    driver.execute_script("resetCodmBrScores();")
    time.sleep(0.3)
    reset_completed = driver.execute_script("""
      return Object.values(CODM_BR_DATA.rounds).filter(r => r.status === 'completed').length;
    """)
    assert_true(reset_completed == 0, "Completed rounds reset to 0")
    badge_reset = driver.execute_script("return document.getElementById('brProgressBadge').innerText;")
    assert_true("Round 0 of 8 Complete" in badge_reset, f"Progress badge reset: {badge_reset}")

    print("\n🎉 ALL 7 TEST SUITES PASSED FLAWLESSLY!")

except Exception as e:
    print(f"\n❌ UNHANDLED EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    driver.quit()
