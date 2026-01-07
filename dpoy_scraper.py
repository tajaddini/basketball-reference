from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

print("Start :))")
url = 'https://www.basketball-reference.com/awards/dpoy.html'
output_file = "./scraped/dpoy_winners.csv"

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

def to_float(value):
    if not value or value == '':
        return None
    try:
        if value.startswith('.'):
            value = '0' + value
        return float(value)
    except:
        return None

def to_int(value):
    if not value or value == '':
        return None
    try:
        return int(value)
    except:
        return None

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.set_page_load_timeout(90)
    driver.get('https://www.basketball-reference.com/awards/dpoy.html')

    wait = WebDriverWait(driver, 30)

    data = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table#dpoy_NBA tbody tr")

    for row in rows:
        try:
            if 'thead' in str(row.get_attribute('class')):
                continue

            season_elem = row.find_elements(By.CSS_SELECTOR, 'th[data-stat="season"]')
            if not season_elem:
                continue

            season = season_elem[0].text.strip()
            if not season or season == 'Season':
                continue

            player_link_elem = row.find_elements(By.CSS_SELECTOR, 'td[data-stat="player"] a')
            if player_link_elem:
                player_name = player_link_elem[0].text.strip()
                href = player_link_elem[0].get_attribute('href')
                if href and '/players/' in href:
                    player_id = href.split('/players/')[1].replace('.html', '')
            else:
                player_elem = row.find_elements(By.CSS_SELECTOR, 'td[data-stat="player"]')
                if player_elem:
                    player_name = player_elem[0].text.strip()

            def safe_get(selector):
                try:
                    return row.find_element(By.CSS_SELECTOR, selector).text.strip()
                except:
                    return ""

            if player_name:
                data.append({
                    'award_type': 'DPOY',
                    'player_id': player_id,
                    'season': season,
                    'player_age': to_int(safe_get('td[data-stat="age"]')),
                    'team': safe_get('td[data-stat="team_id"]'),
                    'games': to_int(safe_get('td[data-stat="g"]')),
                    'minutes_per_game': to_float(safe_get('td[data-stat="mp_per_g"]')),
                    'points_per_game': to_float(safe_get('td[data-stat="pts_per_g"]')),
                    'total_rebounds_per_game': to_float(safe_get('td[data-stat="trb_per_g"]')),
                    'assists_per_game': to_float(safe_get('td[data-stat="ast_per_g"]')),
                    'steals_per_game': to_float(safe_get('td[data-stat="stl_per_g"]')),
                    'blocks_per_game': to_float(safe_get('td[data-stat="blk_per_g"]')),
                    'pct_field_goals': to_float(safe_get('td[data-stat="fg_pct"]')),
                    'pct_threeP_field_goals': to_float(safe_get('td[data-stat="fg3_pct"]')),
                    'pct_ft_field_goals': to_float(safe_get('td[data-stat="ft_pct"]')),
                    'win_shares': to_float(safe_get('td[data-stat="ws"]')),
                    'win_shares_48': to_float(safe_get('td[data-stat="ws_per_48"]'))
                })

        except:
            continue

    df = pd.DataFrame(data)
    output_file = 'basketball_dpoy.xlsx'

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='dpoy')
        worksheet = writer.sheets['dpoy']

        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 30)

        float_columns = ['I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'] 
        for col_letter in float_columns:
            for row_num in range(2, len(data) + 2):
                cell = worksheet[f'{col_letter}{row_num}']
                if cell.value is not None:
                    cell.number_format = '0.000'

    print(f"file saved: {output_file}")

except Exception as e:
    print(f"error: {e}")

finally:
    if driver:
            print("Done :)")
