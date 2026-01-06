import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

url = 'https://www.basketball-reference.com/awards/dpoy.html'
output_file = "dpoy_winners.csv"

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--headless')
options.add_argument('--log-level=3')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

def init_driver():
    os.environ['WDM_LOG'] = '0'
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(120)
    return driver

def get_dpoy_winners_data(driver, url):
    driver.get(url)
    
    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.ID, "dpoy_NBA")))
    
    records = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table#dpoy_NBA tbody tr")
    
    for row in rows:
        row_class = row.get_attribute('class')
        if 'thead' in str(row_class):
            continue

        season_elem = row.find_elements(By.CSS_SELECTOR, 'th[data-stat="season"]')
        if not season_elem:
            continue

        season = season_elem[0].text.strip()
        if not season or season == 'season':
            continue

        player_id = ""
        player_name = ""

        player_link_elem = row.find_elements(By.CSS_SELECTOR, 'td[data-stat="player"] a')
        if player_link_elem:
            player_name = player_link_elem[0].text.strip()
            href = player_link_elem[0].get_attribute('href')
            if href:
                if '/players/' in href:
                    player_id = href.split('/players/')[1].replace('.html', '')
        else:
            player_elem = row.find_elements(By.CSS_SELECTOR, 'td[data-stat="player"]')
            if player_elem:
                player_name = player_elem[0].text.strip()

        def safe_get(selector):
            try:
                elem = row.find_element(By.CSS_SELECTOR, selector)
                return elem.text.strip()
            except Exception as e:
                print(f"An error occurred: {e}")

        lg = safe_get('td[data-stat="lg_id"]')
        age = safe_get('td[data-stat="age"]')
        tm = safe_get('td[data-stat="team_id"]')
        stl = safe_get('td[data-stat="stl_per_g"]')
        blk = safe_get('td[data-stat="blk_per_g"]')

        if player_name:
            records.append({
                'player_id': player_id,
                'season': season,
                'league': lg,
                'player_name': player_name,
                'player_age': age,
                'team': tm,
                'stl': stl,
                'blk': blk
            })

    if len(records) == 0:
        raise Exception("No data found!")

    return records


def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f'{filename} successfully saved!')


def main():
    
    driver = init_driver()
    try:
        data = get_dpoy_winners_data(driver, url)
        save_to_csv(data, output_file)
        
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()