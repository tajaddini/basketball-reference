import os
import requests
import pandas
from lxml import html
import datetime
import re
from random import randint
from time import sleep

class PlayerScraper():
    def __init__(self, verbose=True):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.basketball-reference.com/players/',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document'
        }
        self.xpaths = {
            'name':  '//h1',
            'pos':   '//p[contains(., "Position:")]',
            'birthday': '//*[@data-birth]',
            'death': '//*[@data-death]',
            'age': '//p[span[contains(text(), "Age")]]',
            'hw': '//p[contains(., "cm,")]',
            'career': '//p[contains(., "Career Length:")]',
            'experience': '//p[contains(., "Experience:")]',
            'hall_of_fame': '//li[@class="important special"]',
            'all_star': '//li[@class="all_star"]',
            'stats': '//span/following-sibling::p/following-sibling::p'
        }
        self.verbose = verbose
        self.columns = [
            'id',
            'name',
            'pos',
            'shoots',
            'age',
            'is_alive',
            'height',
            'weight',
            'career length',
            'is_active',
            'has_hall_of_fame',
            'count_allstar',
            'stat_games',
            'stat_points',
            'stat_total_rebounds',
            'stat_assists',
            'stat_field_goal_pct',
            'stat_three_point_field_goal_pct',
            'stat_effective_field_goal_pct',
            'stat_free_throw_pct',
            'stat_efficiency_rating',
            'stat_win_shares'
            ]
        self.df_players = pandas.DataFrame(columns=self.columns)
        self.df_salaries = pandas.DataFrame(columns=['player_id', 'season', 'salary'])
        self._check_structure()
        
    def _print_msg(self, msg, end='\n'):
        if self.verbose:
            print(msg, end=end)
    
    def _check_structure(self):
        # save to file to avoid sending too many requests
        # set up structure
        try:
            os.mkdir('./data')
            os.mkdir('./data/players')
            self._print_msg('cache is set up\n')
        except FileExistsError:
            self._print_msg('cache structure detected\n')

    def _fetch_player(self, player_id):
        try:
            response = requests.get(f'https://www.basketball-reference.com/players/{player_id}.html', headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                self._print_msg(f'could not fetch player data - status: {response.status_code}')
        except Exception as e:
            print(f'caught an exception:\n{e}')
            
    def _get_player(self, player_id):
        fp = f'./data/players/{player_id.replace("/", "-")}'
        if not os.path.exists(fp):
            self._print_msg('getting data from site...', end=' ')
            data = self._fetch_player(player_id)
            if data:
                self._print_msg('OK')
                with open(fp, mode='w', encoding='utf-8') as f:
                    f.write(data)
                return data, 'live'
        else:
            with open(fp, mode='r', encoding='utf-8') as f:
                self._print_msg('reading data from cache')
                data = f.read()
                return data, 'cached'

    def _process_player_name(self, tree):
        try:
            return tree.xpath(self.xpaths['name'])[0].text_content().strip()
        except Exception as e:
            print(f'could not retrieve player name - error : {e}')

    def _process_player_pos_shoots(self, tree):
        try:
            p = tree.xpath(self.xpaths['pos'])[0].text_content().split('▪')
            pos = p[0].strip().splitlines()[-1].strip()
            shoots = p[1].strip().splitlines()[-1].strip()
            return pos, shoots
        except Exception as e:
            print(f'could not retrieve player position, shoots - error : {e}')

    def _process_player_age(self, tree):
        try:
            birthday = tree.xpath(self.xpaths['birthday'])[0].get('data-birth')
            death = tree.xpath(self.xpaths['death'])
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d').date()
            if death:
                death = datetime.datetime.strptime(death[0].get('data-death'), '%Y-%m-%d').date()
                return (death - birthday).days / 365, False
            else:
                return (datetime.datetime.today().date() - birthday).days / 365, True
        except Exception as e:
            print(f'could not retrieve player age - error : {e}')

    def _process_player_height_weight(self, tree):
        try:
            parts = tree.xpath(self.xpaths['hw'])[0].text_content().strip().split('(')[-1].split(',')
            height = int(parts[0].strip().replace('cm', ''))
            weight = int(parts[1].strip().replace('kg)', ''))
            return height, weight
        except Exception as e:
            print(f'could not retrieve player height, weight - error : {e}')

    def _process_player_career(self, tree):
        try:
            career = tree.xpath(self.xpaths['career'])
            if career:
                return int(tree.xpath(self.xpaths['career'])[0].text_content().replace('Career Length:', '').replace('year', '').replace('s', '').strip()), False
            else:
                return int(tree.xpath(self.xpaths['experience'])[0].text_content().replace('Experience:', '').replace('year', '').replace('s', '').strip()), True
        except Exception as e:
            print(f'could not retrieve player career/experience - error : {e}')

    def _process_player_hall_of_fame(self, tree):
        try:
            return True if tree.xpath(self.xpaths['hall_of_fame']) else False
        except Exception as e:
            print(f'could not check hall of fame status - error : {e}')
    
    def _process_player_all_star(self, tree):
        try:
            s = tree.xpath(self.xpaths['all_star'])
            if s:
                return int(s[0].text_content().split('x')[0].strip())
            else:
                return 0
        except Exception as e:
            print(f'could not check all star count - error : {e}')
    
    def _process_player_stats(self, tree):
        def safe_convert(what):
            try:
                return float(what.text_content().strip())
            except Exception as _:
                return None
            
        try:
            s = tree.xpath(self.xpaths['stats'])
            return dict(
                games = safe_convert(s[1]),
                points = safe_convert(s[2]),
                total_rebounds = safe_convert(s[3]),
                assists = safe_convert(s[4]),
                field_goal_pct = safe_convert(s[5]),
                three_point_field_goal_pct = safe_convert(s[6]),
                effective_field_goal_pct = safe_convert(s[7]),
                free_throw_pct = safe_convert(s[8]),
                efficiency_rating = safe_convert(s[9]),
                win_shares = safe_convert(s[10])
            )
        except Exception as e:
            print(f'could not retrieve player stats - error : {e}')

    def _process_player_salaries(self, player_id, data):
        try:
            pattern = r'<th scope="row" class="left " data-stat="season"\s\>(\d{4}-\d{2})<\/th><td class="left " data-stat="team_name" >'
            seasons = [s for s in re.findall(pattern, data)]
            salaries = [int(s) for s in re.findall(r'data-stat="salary" csk="(\d+)', data)]
            df = pandas.DataFrame({'player_id': [player_id] * len(seasons), 'season': seasons, 'salary': salaries})
            if len(self.df_salaries) == 0:
                self.df_salaries = df
            else:
                self.df_salaries = pandas.concat([self.df_salaries, df], ignore_index=True)
            
        except Exception as e:
            print(f'could not retrieve player salaries - error : {e}')
    
    def process_player(self, player_id):
        self._print_msg(f'processing player {player_id} ...')
        data, source = self._get_player(player_id)
        html_tree = html.fromstring(data)
        # getting the data
        name = self._process_player_name(html_tree)
        pos, shoots = self._process_player_pos_shoots(html_tree)
        age, is_alive = self._process_player_age(html_tree)
        height, weight = self._process_player_height_weight(html_tree)
        career, is_active = self._process_player_career(html_tree)
        hall_of_fame = self._process_player_hall_of_fame(html_tree)
        all_star = self._process_player_all_star(html_tree)
        stats = self._process_player_stats(html_tree)
        # process salaries
        self._process_player_salaries(player_id, data)
        # df data
        data=[
            player_id,
            name,
            pos,
            shoots,
            age,
            is_alive,
            height,
            weight,
            career,
            is_active,
            hall_of_fame,
            all_star,
            *stats.values()]
        
        # new player info
        player = pandas.DataFrame([data], columns=self.columns)
        # append data
        if len(self.df_players):
            self.df_players = pandas.concat([self.df_players, player], ignore_index=True)
        else:
            self.df_players = player
        
        return source    
    
    def batch_process(self, players, show=False):
        for player in players:
            source = self.process_player(player)
            if source == 'live':
                self.save()
                sleep(3 + randint(1,5))
        self.save()
        if show:
            print(self.df_players)
            print(self.df_salaries)
    
    def save(self, output='csv'):
        if output == 'csv':
            self.df_players.to_csv('./players.csv')
            self.df_salaries.to_csv('./salaries.csv')
        elif output == 'excel':
            self.df_players.to_excel('./players.xlsx')
            self.df_salaries.to_excel('./salaries.xlsx')
        else:
            print('bad output type')
    
    def players_data(self):
        return self.df_players

    def salaries(self):
        return self.df_salaries


scraper = PlayerScraper()
players = [
    'b/bryanko01',
    'a/abdulka01',
    'g/gilgesh01'
]
scraper.batch_process(players)
