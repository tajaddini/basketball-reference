import httpx
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.basketball-reference.com"
leagues_url = f"{base_url}/leagues/"
output_file = "./scraped/champions.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def get_champions_soup(client):
    response = client.get(leagues_url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def parse_champions(soup):
    champions_data = []
    
    table = soup.find("table", id="stats")
    rows = table.find_all("tr")
    for row in rows:
        if row.find_parent("thead"):
            continue
            
        season_cell = row.find("th", {"data-stat": "season"})
        champion_cell = row.find("td", {"data-stat": "champion"})
        
        if season_cell and champion_cell:
            season = season_cell.get_text(strip=True)
            link = champion_cell.find("a")
            
            if link:
                champion_name = link.get_text(strip=True)
                href = link.get("href")
                parts = href.split("/")
                team_id = parts[2]
                    
                champions_data.append({
                    "Season": season,
                    "Champion": champion_name,
                    "Team_ID": team_id
                })
    return champions_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f'{filename} successfully saved!')

def main():
    with httpx.Client(headers=headers) as client:
        try:
            soup = get_champions_soup(client)
            data = parse_champions(soup)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            save_to_csv(data, output_file)

if __name__ == "__main__":
    main()