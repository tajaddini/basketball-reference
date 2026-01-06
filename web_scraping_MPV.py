import re
import csv
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

url = 'https://www.basketball-reference.com/awards/mvp.html'

browser = webdriver.Firefox()
browser.get(url)

table_CSS_SELECTOR = 'table#mvp_NBA'
table = browser.find_element(
    By.CSS_SELECTOR,
    table_CSS_SELECTOR
    ).get_attribute('innerHTML')
    
rows_regex = r'<tr data-row=\"\d+\">.*?</tr>'
rows = re.findall(rows_regex, table)

fields = ['season_id', 'player_id']
records = []
for row in rows:
    column_regex = r'<td.*?</td>'
    columns = re.findall(column_regex, row)
    season_id = re.findall(r'(?<=a href=\"/leagues/).+?(?=.html)', columns[0])[0]
    player_id = re.findall(r'(?<=a href=\"/players/./).+?(?=.html)', columns[1])[0]
    records.append([season_id, player_id])

filename = "MVP_winners.csv"
with open(filename, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)        # Create writer object
    csvwriter.writerow(fields)             # Write header
    csvwriter.writerows(records)              # Write multiple rows

browser.quit()  