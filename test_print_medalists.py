import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_tests():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    
    file_path = os.path.abspath("index.html")
    file_url = f"file:///{file_path.replace(os.sep, '/')}"

    print(f"Loading {file_url}...")
    driver.get(file_url)
    time.sleep(2)

    # Check for console errors
    logs = driver.get_log("browser")
    severe_errors = [l for l in logs if l['level'] == 'SEVERE']
    print(f"Console SEVERE errors on load: {len(severe_errors)}")
    for err in severe_errors:
        print(f"  [ERROR] {err['message']}")

    # 1. Setup mock data for MLBB, CODM MP, and CODM BR
    print("\n--- Testing Data Extraction for all 3 categories ---")
    driver.execute_script("""
        // Mock MLBB Playoff Data with Champion, Runner-up, Bronze
        const mlbbData = createInitialPlayoffTemplate();
        mlbbData.gf8.team1 = 'CIT';
        mlbbData.gf8.team2 = 'CBA';
        mlbbData.gf8.s1 = 3;
        mlbbData.gf8.s2 = 1;
        mlbbData.gf8.winner = 'CIT';
        mlbbData.gf8.loser = 'CBA';
        mlbbData.lb_f.team1 = 'CBA';
        mlbbData.lb_f.team2 = 'CCJPS';
        mlbbData.lb_f.s1 = 2;
        mlbbData.lb_f.s2 = 0;
        mlbbData.lb_f.winner = 'CBA';
        mlbbData.lb_f.loser = 'CCJPS';
        mlbbData.lb_sf.loser = 'CAS';
        localStorage.setItem('mlbb_playoff_data_v9', JSON.stringify(mlbbData));
        localStorage.setItem('mlbb_tournament_mode_v9', 'double_elim');

        // Mock CODM MP Playoff Data
        const codmData = createInitialPlayoffTemplate();
        codmData.gf8.team1 = 'CBA';
        codmData.gf8.team2 = 'CHM';
        codmData.gf8.s1 = 3;
        codmData.gf8.s2 = 2;
        codmData.gf8.winner = 'CBA';
        codmData.gf8.loser = 'CHM';
        codmData.lb_f.team1 = 'CHM';
        codmData.lb_f.team2 = 'CAS';
        codmData.lb_f.s1 = 2;
        codmData.lb_f.s2 = 1;
        codmData.lb_f.winner = 'CHM';
        codmData.lb_f.loser = 'CAS';
        codmData.lb_sf.loser = 'COED';
        localStorage.setItem('codm_playoff_data_v9', JSON.stringify(codmData));
        localStorage.setItem('codm_tournament_mode_v9', 'double_elim');

        // Mock CODM BR Data with completed rounds
        CODM_BR_DATA = getDefaultBrData();
        for (let r = 1; r <= 8; r++) {
            CODM_BR_DATA.rounds[r].status = 'completed';
            CODM_BR_DATA.rounds[r].results['CIT'] = { team: 'CIT', placement: 1, kills: 12 };
            CODM_BR_DATA.rounds[r].results['CCJPS'] = { team: 'CCJPS', placement: 2, kills: 8 };
            CODM_BR_DATA.rounds[r].results['COED'] = { team: 'COED', placement: 3, kills: 6 };
            CODM_BR_DATA.rounds[r].results['CAS'] = { team: 'CAS', placement: 4, kills: 4 };
            CODM_BR_DATA.rounds[r].results['CBA'] = { team: 'CBA', placement: 5, kills: 2 };
            CODM_BR_DATA.rounds[r].results['CHM'] = { team: 'CHM', placement: 6, kills: 1 };
            CODM_BR_DATA.rounds[r].results['CLIS'] = { team: 'CLIS', placement: 7, kills: 0 };
        }
        saveBrDataToStorage();

        // Refresh active MLBB
        PLAYOFF_DATA = mlbbData;
    """)

    # Verify getCategoryMedalists
    mlbb_med = driver.execute_script("return getCategoryMedalists('mlbb');")
    codm_med = driver.execute_script("return getCategoryMedalists('codm_mp');")
    br_med = driver.execute_script("return getCategoryMedalists('codm_br');")

    print(f"MLBB Medalists: Gold={mlbb_med['gold']}, Silver={mlbb_med['silver']}, Bronze={mlbb_med['bronze']}")
    assert mlbb_med['gold'] == 'CIT', f"Expected CIT, got {mlbb_med['gold']}"
    assert mlbb_med['silver'] == 'CBA', f"Expected CBA, got {mlbb_med['silver']}"
    assert mlbb_med['bronze'] == 'CCJPS', f"Expected CCJPS, got {mlbb_med['bronze']}"

    print(f"CODM MP Medalists: Gold={codm_med['gold']}, Silver={codm_med['silver']}, Bronze={codm_med['bronze']}")
    assert codm_med['gold'] == 'CBA', f"Expected CBA, got {codm_med['gold']}"
    assert codm_med['silver'] == 'CHM', f"Expected CHM, got {codm_med['silver']}"
    assert codm_med['bronze'] == 'CAS', f"Expected CAS, got {codm_med['bronze']}"

    print(f"CODM BR Medalists: Gold={br_med['gold']}, Silver={br_med['silver']}, Bronze={br_med['bronze']}")
    assert br_med['gold'] == 'CIT', f"Expected CIT, got {br_med['gold']}"
    assert br_med['silver'] == 'CCJPS', f"Expected CCJPS, got {br_med['silver']}"
    assert br_med['bronze'] == 'COED', f"Expected COED, got {br_med['bronze']}"

    # Verify Overall Medal Tally
    print("\n--- Testing Overall Medal Tally Calculation ---")
    tally = driver.execute_script("return calculateOverallMedalTally();")
    for t in tally[:4]:
        print(f"Rank {t['rank']}: {t['name']} - Gold: {t['gold']}, Silver: {t['silver']}, Bronze: {t['bronze']}, Total: {t['totalMedals']}, Points: {t['points']}")
    
    assert tally[0]['name'] == 'CIT', "CIT should be #1 with 2 Golds"
    assert tally[0]['gold'] == 2
    assert tally[1]['name'] == 'CBA', "CBA should be #2 with 1 Gold and 1 Silver"

    # Test printPodiumMedalists execution and iframe generation
    print("\n--- Testing printPodiumMedalists('all') generation ---")
    driver.execute_script("printPodiumMedalists('all', 'folio', 'landscape');")
    time.sleep(1)

    iframe_content = driver.execute_script("""
        const iframe = document.getElementById('bracketPrintIframe');
        if (!iframe || !iframe.contentDocument) return null;
        return iframe.contentDocument.body.innerHTML;
    """)

    assert iframe_content is not None, "Print iframe content should not be null!"
    assert "TAGOLOAN COMMUNITY COLLEGE" in iframe_content
    assert "Mobile Legends: Bang Bang" in iframe_content
    assert "Call of Duty: Mobile" in iframe_content
    assert "Battle Royale" in iframe_content
    assert "Official Aggregate College Esports Medal Tally" in iframe_content
    assert "Esports Tournament Director" in iframe_content
    print("SUCCESS: Print iframe received full 3-category printable document with logos, medalists, and medal tally!")

    # Test Print Modal integration
    print("\n--- Testing Print Modal UI ---")
    driver.execute_script("openPrintMedalistsModal('all');")
    time.sleep(0.5)

    modal = driver.find_element(By.ID, "printSeriesModal")
    assert not "hidden" in modal.get_attribute("class"), "Modal should be visible!"

    format_radio = driver.find_element(By.CSS_SELECTOR, "input[name='printFormatRadio'][value='medalists']")
    assert format_radio.is_selected(), "Medalists radio option should be selected!"

    medal_scope_container = driver.find_element(By.ID, "printMedalScopeContainer")
    assert not "hidden" in medal_scope_container.get_attribute("class"), "Medal scope container should be visible!"

    # Trigger print from modal
    driver.execute_script("applyPrintSeriesFromModal();")
    time.sleep(1)
    assert "hidden" in modal.get_attribute("class"), "Modal should close after applying print!"
    print("SUCCESS: Print modal interaction and dispatch works properly!")

    # Test renderPodium header buttons
    print("\n--- Testing Podium Banner Print Action Buttons ---")
    driver.execute_script("renderPodium();")
    time.sleep(0.5)
    podium_banner = driver.find_element(By.ID, "podiumBannerContainer")
    banner_html = podium_banner.get_attribute("innerHTML")
    assert "Print All Categories (Gold, Silver, Bronze)" in banner_html
    assert "Print Current Podium" in banner_html
    print("SUCCESS: Podium banner displays direct print buttons!")

    print("\nAll tests passed successfully!")
    driver.quit()

if __name__ == "__main__":
    run_tests()
