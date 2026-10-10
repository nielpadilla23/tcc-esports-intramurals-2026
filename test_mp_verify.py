import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_mp_stage():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("http://localhost:8080/index.html")
        time.sleep(2)

        # 1. Start CODM MP mode in double elimination
        driver.execute_script("""
            currentEsport = 'codm';
            codmMode = 'mp';
            tournamentMode = 'double_elim';
            if (typeof updateCodmModeUI === 'function') updateCodmModeUI();
            openTheaterMode(true);
        """)
        time.sleep(1)

        slides = driver.execute_script("return getActiveTheaterSlides().map(s => s.id);")
        print(f"Active initial slides in MP: {slides}")

        # Check each initial slide at 1920x1080
        for i, s_id in enumerate(slides):
            driver.execute_script(f"setTheaterSlide({i});")
            time.sleep(0.5)
            metrics = driver.execute_script("""
                const body = document.getElementById('theaterSlideBody');
                return {
                    clientH: body.clientHeight,
                    scrollH: body.scrollHeight,
                    clientW: body.clientWidth,
                    scrollW: body.scrollWidth
                };
            """)
            print(f"Initial Slide {i} ({s_id}): clientH={metrics['clientH']}, scrollH={metrics['scrollH']}, clientW={metrics['clientW']}, scrollW={metrics['scrollW']}")
            assert metrics['scrollH'] <= metrics['clientH'] + 2, f"Slide {s_id} vertical scroll overflow!"
            assert metrics['scrollW'] <= metrics['clientW'] + 2, f"Slide {s_id} horizontal scroll overflow!"
            driver.save_screenshot(f"C:/Users/User/.gemini/antigravity/brain/b9d9bb4a-656b-44b4-86c7-d911586ab055/mp_slide_{i}_{s_id}_new.png")

        # 2. Test Live Match with an active in-progress match (CBA vs CHM Game 3 Underway)
        print("\n--- Testing Live Match In-Progress State ---")
        driver.execute_script("""
            // UB Quarterfinal 2 is active: CBA 1 - 1 CHM
            PLAYOFF_DATA.ub_qf1.winner = 'CCJPS'; PLAYOFF_DATA.ub_qf1.s1 = 2; PLAYOFF_DATA.ub_qf1.s2 = 0;
            PLAYOFF_DATA.ub_qf2.s1 = 1; PLAYOFF_DATA.ub_qf2.s2 = 1; PLAYOFF_DATA.ub_qf2.winner = null;
            setTheaterSlide(2); // live match slide
        """)
        time.sleep(1)
        driver.save_screenshot("C:/Users/User/.gemini/antigravity/brain/b9d9bb4a-656b-44b4-86c7-d911586ab055/mp_live_match_in_progress.png")
        live_metrics = driver.execute_script("""
            const body = document.getElementById('theaterSlideBody');
            return {
                clientH: body.clientHeight,
                scrollH: body.scrollHeight
            };
        """)
        print(f"Live match in-progress metrics: {live_metrics}")
        assert live_metrics['scrollH'] <= live_metrics['clientH'] + 2, "Live match in-progress vertically overflows!"

        # 3. Test Podium slide when tournament concluded
        print("\n--- Testing Podium Slide ---")
        driver.execute_script("""
            PLAYOFF_DATA.ub_qf1.winner = 'CCJPS'; PLAYOFF_DATA.ub_qf1.s1 = 2; PLAYOFF_DATA.ub_qf1.s2 = 0;
            PLAYOFF_DATA.ub_qf2.winner = 'CBA'; PLAYOFF_DATA.ub_qf2.s1 = 2; PLAYOFF_DATA.ub_qf2.s2 = 1;
            PLAYOFF_DATA.ub_qf3.winner = 'CLIS'; PLAYOFF_DATA.ub_qf3.s1 = 2; PLAYOFF_DATA.ub_qf3.s2 = 0;
            PLAYOFF_DATA.ub_qf4.winner = 'COED'; PLAYOFF_DATA.ub_qf4.s1 = 2; PLAYOFF_DATA.ub_qf4.s2 = 1;
            PLAYOFF_DATA.ub_sf1.winner = 'CCJPS'; PLAYOFF_DATA.ub_sf1.s1 = 2; PLAYOFF_DATA.ub_sf1.s2 = 0;
            PLAYOFF_DATA.ub_sf2.winner = 'CLIS'; PLAYOFF_DATA.ub_sf2.s1 = 2; PLAYOFF_DATA.ub_sf2.s2 = 1;
            PLAYOFF_DATA.ub_f.winner = 'CCJPS'; PLAYOFF_DATA.ub_f.s1 = 3; PLAYOFF_DATA.ub_f.s2 = 1;
            PLAYOFF_DATA.lb_r1_1.winner = 'CHM'; PLAYOFF_DATA.lb_r1_1.s1 = 2; PLAYOFF_DATA.lb_r1_1.s2 = 0;
            PLAYOFF_DATA.lb_r1_2.winner = 'CIT'; PLAYOFF_DATA.lb_r1_2.s1 = 2; PLAYOFF_DATA.lb_r1_2.s2 = 1;
            PLAYOFF_DATA.lb_qf1.winner = 'COED'; PLAYOFF_DATA.lb_qf1.s1 = 2; PLAYOFF_DATA.lb_qf1.s2 = 0;
            PLAYOFF_DATA.lb_qf2.winner = 'CBA'; PLAYOFF_DATA.lb_qf2.s1 = 2; PLAYOFF_DATA.lb_qf2.s2 = 1;
            PLAYOFF_DATA.lb_sf.winner = 'CBA'; PLAYOFF_DATA.lb_sf.s1 = 2; PLAYOFF_DATA.lb_sf.s2 = 1;
            PLAYOFF_DATA.lb_f.winner = 'CLIS'; PLAYOFF_DATA.lb_f.s1 = 3; PLAYOFF_DATA.lb_f.s2 = 2;
            PLAYOFF_DATA.gf8.winner = 'CCJPS'; PLAYOFF_DATA.gf8.s1 = 3; PLAYOFF_DATA.gf8.s2 = 1;
            
            setTheaterSlide(1); // Podium is slide 1
        """)
        time.sleep(1)
        podium_metrics = driver.execute_script("""
            const body = document.getElementById('theaterSlideBody');
            return {
                clientH: body.clientHeight,
                scrollH: body.scrollHeight
            };
        """)
        print(f"Podium metrics: {podium_metrics}")
        assert podium_metrics['scrollH'] <= podium_metrics['clientH'] + 2, "Podium vertically overflows!"
        driver.save_screenshot("C:/Users/User/.gemini/antigravity/brain/b9d9bb4a-656b-44b4-86c7-d911586ab055/mp_slide_4_podium_new.png")

        # 4. Test MLBB mode
        print("\n--- Testing MLBB Mode ---")
        driver.execute_script("""
            currentEsport = 'mlbb';
            tournamentMode = 'double_elim';
            if (typeof updateTournamentInfoBanner === 'function') updateTournamentInfoBanner();
            openTheaterMode(true);
            setTheaterSlide(0);
        """)
        time.sleep(1)
        mlbb_metrics = driver.execute_script("""
            const body = document.getElementById('theaterSlideBody');
            return {
                clientH: body.clientHeight,
                scrollH: body.scrollHeight
            };
        """)
        print(f"MLBB Stage metrics: {mlbb_metrics}")
        assert mlbb_metrics['scrollH'] <= mlbb_metrics['clientH'] + 2, "MLBB stage vertically overflows!"

        print("\nALL MULTIPLAYER LIVE STAGE TESTS PASSED WITH ZERO SCROLLING!")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_mp_stage()
