from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import re


driver = webdriver.Chrome()

years = ["2020", "2021", "2022", "2023", "2024"]

all_players_info = []

for year in years:
    totals_url = f"https://www.basketball-reference.com/leagues/NBA_{year}_totals.html"
    driver.get(totals_url)

    rows = driver.find_elements(
        By.CSS_SELECTOR, "table.stats_table tbody tr:not(.thead):not(.partial_table)")
    for row in rows:
        rank = row.find_element(
            By.CSS_SELECTOR, "th[data-stat='ranker']").text
        player = row.find_element(
            By.CSS_SELECTOR, "td[data-stat='name_display'] a")

        player_href = player.get_attribute("href")
        x = re.search(
            r'/players/([a-z]/[^/]+)\.html', player_href)
        player_id = x.group(1)
        player_age = row.find_element(
            By.CSS_SELECTOR, "td[data-stat='age']").text
        player_team = row.find_element(
            By.CSS_SELECTOR, "td[data-stat='team_name_abbr']").text
        player_position = row.find_element(
            By.CSS_SELECTOR, "td[data-stat='pos']").text
        points = row.find_element(
            By.CSS_SELECTOR, "td[data-stat='pts']").text

        players_info = {'season': f'{int(year) - 1}-{year}',
                        'rank': rank,
                        'player_id': player_id,
                        'won_at_age': player_age,
                        'team_name': player_team,
                        'player_position': player_position,
                        'points': points}
        if int(rank) <= 50:
            all_players_info.append(players_info)
        else:
            break

driver.quit()
top_50_players_table = pd.DataFrame(all_players_info)
top_50_players_table.to_csv("./scraped/top50players.csv", encoding='utf-8-sig')
