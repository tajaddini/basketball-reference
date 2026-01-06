import httpx
from bs4 import BeautifulSoup
import pandas as pd
import time

base_url = 'https://www.basketball-reference.com'
teams_url = f'{base_url}/teams/'
output_file = "roster_data.csv"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def get_teams(client):
    response = client.get(teams_url)
    response.raise_for_status()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='teams_active')
        clickable_rows = table.find_all('tr', class_='full_table')
        teams = []
        for row in clickable_rows:
            row_info = row.find('th', {'data-stat': 'franch_name'}).find('a')
            teams.append(
                {
                    'id': row_info['href'].split('/')[2],
                    'name': row_info.text,
                    'href': row_info['href']
                }     
            )
    return teams


def get_team_data_based_on_seasons(client, team_href, team_id, start_year=2015):
    url = base_url + team_href
    response = client.get(url)
    response.raise_for_status()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id=team_id)
        rows = table.find('tbody').find_all('tr')
        seasons = []
        for row in rows:
            season_cell = row.find('th', {'data-stat': 'season'})
            season = season_cell.get_text()
            if int(season.split('-')[0]) >= start_year:
                seasons.append(
                    {
                        'season': season,
                        'href': season_cell.find('a')['href']
                    }
                )        
    return seasons
    
def get_roster(client, season_href):
    response = client.get(base_url + season_href)
    response.raise_for_status()
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='roster')
        rows = table.find('tbody').find_all('tr')
        players = []
        for row in rows:
            player_info = row.find('td', {'data-stat': 'player'}).find('a')
            players.append(
                {
                    'id' : player_info['href'].split('/players/')[1].replace('.html', ''),
                    'position': row.find('td', {'data-stat':'pos'}).text
                    
                }
            )
    return players
    
    
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df = df.rename(columns={
        'id': 'player_id',
        'position': 'player_position'
    })
    column_order = ['team_name', 'season', 'player_id', 'player_position']
    df = df[column_order]
    
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f'{filename} successfully saved!')
    
def main():
    data = []   
    with httpx.Client(http2=True, headers=headers) as client:
        try:
            teams = get_teams(client)
            time.sleep(3.1)
            
            for team in teams:
                print(f'Scraping data for team: {team['name']}')
                seasons = get_team_data_based_on_seasons(client, team['href'], team['id'])
                time.sleep(3.1)
                
                for season in seasons:
                    roster = get_roster(client, season['href'])
                    
                    for player in roster:
                        player.update({
                                'team_name': team['name'],
                                'season': season['season']
                            })
                        data.append(player)

                    time.sleep(3.1)  
                    
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            save_to_csv(data, output_file)

if __name__ == "__main__":
    main()