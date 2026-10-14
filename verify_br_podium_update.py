import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

html_path = os.path.abspath('index.html').replace('\\', '/')
artifacts_dir = r"C:\Users\User\.gemini\antigravity\brain\b9d9bb4a-656b-44b4-86c7-d911586ab055"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1600,1050')

driver = webdriver.Chrome(options=options)

try:
    print("1. Opening index.html directly into CODM BR view...")
    driver.get('file:///' + html_path + '#game=codm&mode=br')
    time.sleep(1.5)

    # Ensure official data is loaded in storage and rendered
    driver.execute_script("""
      CODM_BR_DATA = getDefaultBrData();
      saveBrDataToStorage();
      renderCodmBattleRoyale();
    """)
    time.sleep(0.5)

    # Screenshot 1: CODM BR Tab with Official Podium (CHM Gold, CIT Silver, CCJPS Bronze)
    ss_podium = os.path.join(artifacts_dir, "codm_br_podium_chm_gold_cit_silver_ccjps_bronze.png")
    driver.save_screenshot(ss_podium)
    print(f"Saved: {ss_podium}")

    # Check medalists
    med = driver.execute_script("return getCategoryMedalists('codm_br');")
    print(f"CODM BR Medalists: Gold={med['gold']}, Silver={med['silver']}, Bronze={med['bronze']}")
    assert med['gold'] == 'CHM', f"Expected CHM, got {med['gold']}"
    assert med['silver'] == 'CIT', f"Expected CIT, got {med['silver']}"
    assert med['bronze'] == 'CCJPS', f"Expected CCJPS, got {med['bronze']}"

    # Screenshot 2: Print Medalists Certificate modal
    driver.execute_script("openPrintMedalistsModal('codm_br');")
    time.sleep(0.5)
    ss_modal = os.path.join(artifacts_dir, "codm_br_print_modal_chm_gold.png")
    driver.save_screenshot(ss_modal)
    print(f"Saved: {ss_modal}")
    driver.execute_script("closePrintSeriesModal();")

    # Screenshot 3: Open BR Live Stage (Theater Mode)
    driver.execute_script("openBrLiveStage();")
    time.sleep(0.8)
    ss_stage = os.path.join(artifacts_dir, "codm_br_live_stage_chm_champion.png")
    driver.save_screenshot(ss_stage)
    print(f"Saved: {ss_stage}")

    print("ALL VERIFICATIONS & SCREENSHOTS COMPLETED SUCCESSFULLY!")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
finally:
    driver.quit()
