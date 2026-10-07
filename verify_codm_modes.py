import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def main():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1600,1200')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--enable-unsafe-swiftshader')

    driver = webdriver.Chrome(options=options)
    artifacts_dir = r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055"
    file_path = os.path.abspath("index.html")
    file_url = f"file:///{file_path.replace(os.sep, '/')}"

    print(f"Loading URL: {file_url}")
    driver.get(file_url)
    time.sleep(2)

    # 1. Check Console Logs
    logs = driver.get_log('browser')
    severe_errors = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Severe console errors on load: {len(severe_errors)}")
    for err in severe_errors:
        print(" Console Error:", err['message'])
    assert len(severe_errors) == 0, f"Found severe console errors: {severe_errors}"

    # Take screenshot of Landing Hub
    driver.save_screenshot(os.path.join(artifacts_dir, "verified_landing_hub_codm_modes.png"))
    print("Saved Landing Hub screenshot.")

    # 2. Select CODM Multi-Player from Landing Hub
    print("Opening CODM Dashboard...")
    driver.execute_script("openEsportDashboard('codm');")
    time.sleep(1.5)

    current_esport = driver.execute_script("return currentEsport;")
    print(f"Active esport: {current_esport}")
    assert current_esport == 'codm', f"Expected currentEsport to be 'codm', got {current_esport}"

    # Set Admin role for simulation and scoring
    driver.execute_script("currentUserRole = 'admin'; updateAdminUI();")

    # 3. Fast Sim / Simulate Tournament
    print("Simulating Double Elimination Bracket...")
    driver.execute_script("simulateDoubleElimination();")
    time.sleep(1.5)

    # 4. Check matches in PLAYOFF_DATA
    playoff_data = driver.execute_script("return PLAYOFF_DATA;")
    print(f"Total matches in PLAYOFF_DATA: {len(playoff_data)}")

    # Check finals bestOf and scores
    finals_keys = ['ub_f', 'lb_f', 'gf8']
    for fk in finals_keys:
        m = playoff_data.get(fk)
        best_of = driver.execute_script(f"return getMatchBestOf('{fk}', PLAYOFF_DATA['{fk}']);")
        s1 = m.get('s1')
        s2 = m.get('s2')
        winner = m.get('winner')
        games = m.get('games', [])
        print(f"Match {fk}: label='{m.get('label')}', bestOf={best_of}, score={s1}-{s2}, winner={winner}, games_count={len(games)}")
        assert best_of == 3, f"Expected {fk} bestOf to be 3 in CODM, got {best_of}"
        assert max(s1, s2) == 2, f"Expected winning score to be 2 for BO3 in {fk}, got {s1}-{s2}"
        assert len(games) == 3, f"Expected 3 games in match.games, got {len(games)}"
        assert games[0]['mode'] == 'Search and Destroy', f"Game 1 should be S&D, got {games[0]['mode']}"
        assert games[1]['mode'] == 'Control', f"Game 2 should be Control, got {games[1]['mode']}"
        assert games[2]['mode'] == 'Hardpoint', f"Game 3 should be Hardpoint, got {games[2]['mode']}"

    # Take screenshot of simulated CODM Double Elim Bracket
    driver.save_screenshot(os.path.join(artifacts_dir, "verified_codm_simulated_bracket.png"))
    print("Saved simulated CODM bracket screenshot.")

    # 5. Switch to Match Schedule list tab
    print("Switching to Match Schedule tab...")
    driver.execute_script("switchTab('matches');")
    time.sleep(1)
    driver.save_screenshot(os.path.join(artifacts_dir, "verified_codm_match_schedule.png"))
    print("Saved CODM match schedule screenshot.")

    # 6. Open Score Modal on UB QF 1
    print("Testing Score Modal on ub_qf1...")
    driver.execute_script("openScoreModal('ub_qf1');")
    time.sleep(1)

    modal_visible = driver.execute_script("return !document.getElementById('scoreEditModal').classList.contains('hidden');")
    modes_container_visible = driver.execute_script("return !document.getElementById('modalCodmModesContainer').classList.contains('hidden');")
    print(f"Score modal visible: {modal_visible}, Modes container visible: {modes_container_visible}")
    assert modal_visible, "Score modal should be visible"
    assert modes_container_visible, "modalCodmModesContainer should be visible for CODM"

    # Test clicking game mode winner in modal
    driver.execute_script("setModalCodmGameWinner(0, 1);") # G1 to team 1
    driver.execute_script("setModalCodmGameWinner(1, 1);") # G2 to team 1
    time.sleep(0.5)

    s1_val = driver.execute_script("return document.getElementById('modalScore1').value;")
    s2_val = driver.execute_script("return document.getElementById('modalScore2').value;")
    print(f"Modal score after G1 and G2 wins: {s1_val} - {s2_val}")
    assert s1_val == '2' and s2_val == '0', f"Expected score 2-0, got {s1_val}-{s2_val}"

    # Take screenshot of Score Modal with CODM Modes
    driver.save_screenshot(os.path.join(artifacts_dir, "verified_codm_score_modal_modes.png"))
    print("Saved CODM score modal screenshot.")

    # Save modal score
    driver.execute_script("saveModalScore();")
    time.sleep(1)

    # 7. Check MLBB non-regression
    print("Checking MLBB non-regression...")
    driver.execute_script("openEsportDashboard('mlbb');")
    time.sleep(1.5)
    mlbb_esport = driver.execute_script("return currentEsport;")
    mlbb_gf_bo = driver.execute_script("return getMatchBestOf('gf8', PLAYOFF_DATA['gf8']);")
    print(f"Switched to MLBB. Active esport: {mlbb_esport}, Grand Finals bestOf: {mlbb_gf_bo}")
    assert mlbb_esport == 'mlbb', f"Expected MLBB, got {mlbb_esport}"
    assert mlbb_gf_bo == 7, f"Expected MLBB Grand Finals to be BO7, got {mlbb_gf_bo}"

    driver.save_screenshot(os.path.join(artifacts_dir, "verified_mlbb_non_regression.png"))
    print("Saved MLBB non-regression screenshot.")

    # 8. Return to Esport Hub
    print("Returning to Hub...")
    driver.execute_script("returnToEsportHub();")
    time.sleep(1)
    driver.save_screenshot(os.path.join(artifacts_dir, "verified_hub_returned.png"))
    print("Saved returned hub screenshot.")

    # 9. Mobile viewport check on CODM
    print("Checking Mobile viewport...")
    driver.set_window_size(390, 844)
    driver.execute_script("openEsportDashboard('codm');")
    time.sleep(1)
    driver.save_screenshot(os.path.join(artifacts_dir, "verified_codm_mobile_bracket.png"))
    print("Saved CODM mobile bracket screenshot.")

    # Final console error check
    logs = driver.get_log('browser')
    severe = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Total severe errors across session: {len(severe)}")
    for err in severe:
        print(" Error:", err['message'])
    assert len(severe) == 0, f"Found severe console errors: {severe}"

    driver.quit()
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    main()
