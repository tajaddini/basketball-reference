import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


url = 'https://www.basketball-reference.com/awards/mvp.html'
output_file = "mvp_winners.csv"
csv_fields = ['season_id', 'player_id']

def init_driver():
    options = Options()
    driver = webdriver.Firefox(options=options)
    return driver

def scrape_mvp_table(driver, url):
    driver.get(url)
    table_selector = 'table#mvp_NBA'
    try:
        table_element = driver.find_element(By.CSS_SELECTOR, table_selector)
        return table_element.get_attribute('innerHTML')
    except Exception as e:
        print(f"Error finding table: {e}")
        return None

def parse_html_to_records(html_content):
    rows_regex = r'<tr data-row=\"\d+\">.*?</tr>'
    rows = re.findall(rows_regex, html_content)
    
    records = []
    for row in rows:
        column_regex = r'<td.*?</td>'
        columns = re.findall(column_regex, row)
        try:
            season_id = re.findall(r'(?<=a href=\"/leagues/).+?(?=.html)', columns[0])[0]
            player_id = re.findall(r'(?<=a href=\"/players/./).+?(?=.html)', columns[1])[0]
            records.append([season_id, player_id])
        except Exception as e:
            print(f"Error extracting record data: {e}")
            return None                
    return records

def save_to_csv(filename, fields, data):
    df = pd.DataFrame(data, columns=fields)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f'{filename} successfully saved!')

def main():
    driver = init_driver()  
    try:
        html = scrape_mvp_table(driver, url)
        records = parse_html_to_records(html)
        save_to_csv(output_file, csv_fields, records)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()