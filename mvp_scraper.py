import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


url = 'https://www.basketball-reference.com/awards/mvp.html'
output_file = "mvp_winners.csv"
csv_fields = ['season', 'player_id', 'age', 'Tm','G','MP','PTS','TRB','AST','STL','BLK','FG%','3P%','FT%','WS','WS/48']

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
        column_names_regex = r'(?<=data-stat=\")\w+?(?=\")'
        columns = re.findall(column_regex, row)
        column_names = re.findall(column_names_regex, row)
        try:
            season = re.findall(r'<a[^>]*>(\d{4}-\d{2})</a>', row)[0]
            player_id = re.findall(r'(?<=a href=\"/players/).+?(?=.html)', columns[1])[0]
            age = re.findall(r'(\d*\.?\d+)?(?=</td>)', columns[3])[0]
            Tm = re.findall(r'\w+?(?=</a></td>)', columns[4])[0]
            other_numeric_values = [re.findall(r'(\d*\.?\d+)?(?=</td>)', col)[0] for col in columns[5:]]
            records.append([season, player_id, age, Tm, *other_numeric_values])
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