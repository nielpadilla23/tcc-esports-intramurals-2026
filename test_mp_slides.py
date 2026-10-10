import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def run_test():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("http://localhost:8080/index.html")
        time.sleep(2)

        driver.execute_script("""
            currentEsport = 'codm';
            codmMode = 'mp';
            tournamentMode = 'double_elim';
            if (typeof updateCodmModeUI === 'function') updateCodmModeUI();
            openTheaterMode(true);
        """)
        time.sleep(1)

        slides = driver.execute_script("return getActiveTheaterSlides().map(s => s.id);")
        print(f"Active slides: {slides}")
        for i, s_id in enumerate(slides):
            driver.execute_script(f"setTheaterSlide({i});")
            time.sleep(0.3)
            metrics = driver.execute_script("""
                const body = document.getElementById('theaterSlideBody');
                return {
                    clientH: body.clientHeight,
                    scrollH: body.scrollHeight,
                    clientW: body.clientWidth,
                    scrollW: body.scrollWidth
                };
            """)
            print(f"Slide {i} ({s_id}): {metrics}")

        # Concluded test
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
            setTheaterSlide(0);
        """)
        time.sleep(0.5)
        concluded_slides = driver.execute_script("return getActiveTheaterSlides().map(s => s.id);")
        for i, s_id in enumerate(concluded_slides):
            driver.execute_script(f"setTheaterSlide({i});")
            time.sleep(0.3)
            metrics = driver.execute_script("""
                const body = document.getElementById('theaterSlideBody');
                return {
                    clientH: body.clientHeight,
                    scrollH: body.scrollHeight,
                    clientW: body.clientWidth,
                    scrollW: body.scrollWidth
                };
            """)
            print(f"Concluded Slide {i} ({s_id}): {metrics}")

    finally:
        driver.quit()

if __name__ == "__main__":
    run_test()
