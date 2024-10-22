import datetime
import html
import json
import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

import requests
from bs4 import BeautifulSoup

import asyncio

# from test import research_map_proceed_async
import id_to_name
import keys
from id_to_name import pro_teams
from keys import api_token_3, api_token_4, api_token_5, api_token_2, api_token_1, api_token_6, api_token_7,\
              api_token_8, api_token_9, api_token_10, api_token_11, api_token_12, api_token_13, api_token_14,\
              api_token_15, api_token_16, api_token_17, api_token_18

radiant_position_to_lane = {
    'pos1': 'bottomLaneOutcome',
    'pos2': 'midLaneOutcome',
    'pos3': 'topLaneOutcome',
    'pos4': 'topLaneOutcome',
    'pos5': 'bottomLaneOutcome'
}
dire_position_to_lane = {
    'pos1': 'topLaneOutcome',
    'pos2': 'midLaneOutcome',
    'pos3': 'bottomLaneOutcome',
    'pos4': 'bottomLaneOutcome',
    'pos5': 'topLaneOutcome'
}


def get_urls(url, target_datetime=0):
    headers = {
        'Host': 'dltv.org',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers'
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        live_matches_block = soup.find('div', class_='live__matches')
        live_matches = live_matches_block.find_all('div', class_='live__matches-item__body')

        live_matches_urls = set()
        for match in live_matches:
            url = match.find('a')['href']
            live_matches_urls.add(url)
        if not len(live_matches_urls):
            upcoming_matches = soup.find('div', class_="upcoming__matches-item")
            if upcoming_matches:
                target_datetime_str = upcoming_matches['data-matches-odd']
                target_datetime = datetime.datetime.strptime(target_datetime_str,
                                                             '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=2,
                                                                                                       minutes=54)
        if not len(live_matches_urls):
            live_matches_urls = None
        return live_matches_urls, target_datetime
    else:
        print(f'{response.status_code}')


def get_team_names(soup):
    tags_block = soup.find('div', class_='plus__stats-details desktop-none')
    tags = tags_block.find_all('span', class_='title')
    scores = soup.find('div', class_='score__scores live').find_all('span')
    score = [i.text.strip() for i in scores]
    radiant_team_name, dire_team_name = None, None
    for tag in tags:
        team_info = tag.text.strip().split('')
        if team_info[1].replace(' ', '').lower() == 'radiant':
            radiant_team_name = team_info[0].lower().replace(' ', '')
        else:
            dire_team_name = team_info[0].lower().replace(' ', '')
    return radiant_team_name, dire_team_name, score


def get_player_names_and_heroes(soup):
    radiant_players, dire_players = {}, {}
    radiant_block = soup.find('div', class_='picks__new-picks__picks radiant')
    dire_block = soup.find('div', class_='picks__new-picks__picks dire')
    if radiant_block is not None and dire_block is not None:
        radiant_heroes_block = radiant_block.find_all('div', class_='pick player')
        dire_heroes_block = dire_block.find_all('div', class_='pick player')
        for hero in radiant_heroes_block[0:5]:
            hero_name = hero.get('data-tippy-content').replace('Outworld Devourer', 'Outworld Destroyer')
            player_name = hero.find('span', class_='pick__player-title').text.lower()
            player_name = re.sub(r'[^\w\s\u4e00-\u9fff]+', '', player_name)
            radiant_players[player_name] = {'hero': hero_name}
        for hero in dire_heroes_block:
            hero_name = hero.get('data-tippy-content').replace('Outworld Devourer', 'Outworld Destroyer')
            player_name = hero.find('span', class_='pick__player-title').text.lower()
            player_name = re.sub(r'[^\w\s\u4e00-\u9fff]+', '', player_name)
            dire_players[player_name] = {'hero': hero_name}
        if len(radiant_players) == 5 and len(dire_players) == 5:
            return radiant_players, dire_players


def get_team_positions(url):
    response = requests.get(url)
    if response.status_code == 200:
        response_html = html.unescape(response.text)
        soup = BeautifulSoup(response_html, 'lxml')
        picks_item = soup.find_all('div', class_='picks-item with-match-players-tooltip')
        # picks_item = soup.find('div', class_='match-statistics--teams-players')

        heroes = []
        for hero_block in picks_item:
            for hero in list(id_to_name.translate.values()):
                if f'({hero})' in hero_block.text:
                    heroes.append(hero)
        radiant_heroes_and_pos = {}
        dire_heroes_and_pos = {}
        for i in range(5):
            for translate_hero_id in id_to_name.translate:
                if id_to_name.translate[translate_hero_id] == heroes[i]:
                    hero_id = translate_hero_id
                    radiant_heroes_and_pos[f'pos{i + 1}'] = {'hero_id': hero_id, 'hero_name': heroes[i]}
        c = 0
        for i in range(5, 10):
            for translate_hero_id in id_to_name.translate:
                if id_to_name.translate[translate_hero_id] == heroes[i]:
                    hero_id = translate_hero_id
                    dire_heroes_and_pos[f'pos{c + 1}'] = {'hero_id': hero_id, 'hero_name': heroes[i]}
                    c += 1

        return radiant_heroes_and_pos, dire_heroes_and_pos
    else:
        print('нету live матчей')


def analyze_draft(synergy, counterpick, pos1_vs_team, pos2_vs_team, pos3_vs_team,
                  sups, over45):
    radiant_predict, dire_predict = False, False
    values = {'synergy': synergy, 'counterpick': counterpick, 'pos 1_vs_team': pos1_vs_team,
              'pos 2_vs_team': pos2_vs_team, 'pos 3_vs_team': pos3_vs_team, 'sups': sups, 'over45': over45}
    other_values = {'synergy': synergy, 'counterpick': counterpick, 'sups': sups, 'over45': over45}
    values_nones = sum(1 for value in values.values() if value is None)
    other_values_nones = sum(1 for value in other_values.values() if value is None)
    nones = (values_nones <= 2) * (other_values_nones <= 1)
    if nones:
        all_positive_or_negative = all(value >= 0 for value in values.values() if value is not None) + all(
            value <= 0 for value in values.values() if value is not None)
        other_values_check = all(value >= 0 for value in other_values.values() if value is not None) + all(
            value <= 0 for value in other_values.values() if value is not None)
        synergy_or_counterpick = all(
            value >= 0 for value in [counterpick, synergy, values['over45']] if value is not None) + all(
            value <= 0 for value in [counterpick, synergy] if value is not None)
        both_over9 = all(value <= -9 for value in [counterpick, synergy] if value is not None) + all(
            value >= 9 for value in [counterpick, synergy] if value is not None)
        both_over5 = all(value <= -5 for value in [counterpick, synergy] if value is not None) + all(
            value >= 5 for value in [counterpick, synergy] if value is not None)
        any_over20 = (all(value > 0 for value in [counterpick, synergy] if value is not None) * any(
            value >= 20 for value in [counterpick, synergy] if value is not None)) + (
            all(value < 0 for value in [counterpick, synergy] if value is not None) * any(
                value <= -20 for value in [counterpick, synergy] if value is not None))
        any_over8 = (all(value > 0 for value in [counterpick, synergy] if value is not None) * any(
            value >= 8 for value in [counterpick, synergy] if value is not None)) + (
            all(value < 0 for value in [counterpick, synergy] if value is not None) * any(
                value <= -8 for value in [counterpick, synergy] if value is not None))
        if counterpick is not None:
            counterpick_over8 = (counterpick >= 8) + (counterpick <= -8)
        else:
            counterpick_over8 = False
        if other_values_check and both_over9:
            if counterpick > 0:
                radiant_predict = True
            elif counterpick < 0:
                dire_predict = True
            verdict = f'ОТЛИЧНАЯ СТАВКА 2 ФЛЕТА'
        elif (other_values_check and both_over5) or any_over20 or both_over9 or (both_over5 and any_over8):
            if counterpick > 0:
                radiant_predict = True
            elif counterpick < 0:
                dire_predict = True
            verdict = f'ХОРОШАЯ СТАВКА 1 ФЛЕТ'
        elif (synergy_or_counterpick and both_over5) or all_positive_or_negative\
                or other_values_check or counterpick_over8:
            if counterpick > 0:
                radiant_predict = True
            elif counterpick < 0:
                dire_predict = True
            verdict = f'РИСКОВАЯ СТАВКА ПОЛ ФЛЕТА'
        else:
            verdict = f'ПЛОХАЯ СТАВКА!!!'
    else:
        verdict = f'ПЛОХАЯ СТАВКА!!!'
    return verdict, radiant_predict, dire_predict


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_percentage(s1, s2):
    distance = levenshtein_distance(s1, s2)
    max_length = max(len(s1), len(s2))
    return (1 - distance / max_length) * 100


def are_similar(s1, s2, threshold=70):
    return similarity_percentage(s1, s2) >= threshold


def get_map_id(match):
    if match['team_dire'] is not None and match['team_radiant'] is not None\
            and 'Kobold' not in match['tournament']['name']:
        radiant_team_name = match['team_radiant']['name'].lower()
        dire_team_name = match['team_dire']['name'].lower()
        score = match['best_of_score']
        dic = {
            'fissure': 1,
            'riyadh': 1,
            'international': 1,
            'pgl': 1,
            'bb': 1,
            'epl': 2,
        }
        match_name = match['tournament']['name'].lower()
        tier = match['tournament']['tier']

        # Проверка наличия имени в словаре и обновление значения tier
        for name in dic:
            if name in match_name:
                tier = dic[name]
        if tier in [1, 2]:
            for karta in match['related_matches']:
                if karta['status'] == 'online':
                    map_id = karta['id']
                    url = f'https://cyberscore.live/en/matches/{map_id}/'
                    result = if_unique(url)
                    if result is not None:
                        return url, radiant_team_name, dire_team_name, score, tier


def if_unique(url):
    with open('map_id_check.txt', 'r+') as f:
        data = json.load(f)
        if url not in data:
            # data.append(url)
            # f.truncate()
            # f.seek(0)
            # json.dump(data, f)
            return True


def add_url(url):
    with open('map_id_check.txt', 'r+') as f:
        data = json.load(f)
        if url not in data:
            data.append(url)
            f.truncate()
            f.seek(0)
            json.dump(data, f)


def find_in_radiant(radiant_players, nick_name, translate, position, radiant_pick, radiant_lst):
    for radiant_player_name in radiant_players:
        if are_similar(radiant_player_name, nick_name, threshold=70):
            radiant_pick[translate[position]] = radiant_players[radiant_player_name]['hero']
            if position in radiant_lst:
                radiant_lst.remove(position)
                return radiant_lst, radiant_pick


def find_in_dire(dire_players, nick_name, translate, position, dire_pick, dire_lst):
    for dire_player_name in dire_players:
        if are_similar(dire_player_name, nick_name, threshold=70):
            dire_pick[translate[position]] = dire_players[dire_player_name]['hero']
            if position in dire_lst:
                dire_lst.remove(position)
                return dire_lst, dire_pick


def if_picks_are_done(soup):
    dire_block = soup.find('div', class_='picks__new-picks__picks dire')
    radiant_block = soup.find('div', class_='picks__new-picks__picks radiant')
    if radiant_block is not None and dire_block is not None:
        items_radiant = radiant_block.find('div', class_='items').find_all('div', class_='pick')
        items_dire = dire_block.find('div', class_='items').find_all('div', class_='pick')
        if len(items_dire) == 5 and len(items_radiant) == 5:
            return True


def clean_up(inp, length=0):
    if len(inp) > length:
        copy = inp.copy()
        for i in inp:
            if 53 >= i >= 47:
                copy.remove(i)
        if len(copy) < 3:
            return inp
        else:
            return copy
    else:
        return []


def send_message(message):
    bot_token = f'{keys.Token}'
    chat_id = f'{keys.Chat_id}'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, json=payload)


def str_to_json(input_data):
    text = input_data.replace(':', '":').replace('#', '').replace('{', '{"')
    data = re.sub(r",(?=[a-zA-Z])", ',"', text)
    data = re.sub(r'\.(\d{2})(\d{2})', r'\1.\2', data, flags=re.MULTILINE)
    data = re.sub(r'\.(\d{2})(\d1)', r'\1.\2', data, flags=re.MULTILINE)
    data = re.sub(r':0(?=[0-9])', ':', data)
    data = re.sub(r'[\x00-\x1F]+', '', data)

    def multiply_by_10(match):
        number = int(match.group(1))
        return ':' + str(number * 10) + ','

    data = re.sub(r':\.(\d1),', multiply_by_10, data).replace(':.', ':')
    data = re.sub(r':(0)([0-9])', r':\2', data, flags=re.MULTILINE)
    return data


def fetch_hero_data(hero_name):
    hero_url = hero_name.replace(' ', '%20')
    url = f'https://dota2protracker.com/hero/{hero_url}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Error fetching data for {hero_name}: {url}')
        return None
    soup = BeautifulSoup(response.text, 'lxml')
    stats = soup.find_all('script')
    matchups = re.search(r'matchups:(\[.*?])', stats[5].text, re.DOTALL)
    synergies = re.search(r'synergies:(\[.*?])', stats[5].text, re.DOTALL)
    matchups = json.loads(str_to_json(matchups.group(1)).strip())
    synergies = json.loads(str_to_json(synergies.group(1)).strip())
    return matchups, synergies


def process_synergy_data(position, synergies, team_positions):
    wr_list = []
    for synergy in synergies:
        tracker_position = synergy['position'].replace('pos ', 'pos')
        data_pos = synergy['other_pos'].replace('pos ', 'pos')
        data_hero = synergy['other_hero']
        data_wr = synergy['win_rate']
        if synergy['num_matches'] >= 15 and data_pos in team_positions and team_positions[data_pos][
                'hero_name'] == data_hero:
            if tracker_position == position:
                wr_list.append(data_wr)
    return wr_list


def process_matchup_data(position, matchups, opposing_team_positions):
    wr_list = []
    for matchup in matchups:
        tracker_position = matchup['position'].replace('pos ', 'pos')
        data_pos = matchup['other_pos'].replace('pos ', 'pos')
        data_hero = matchup['other_hero']
        data_wr = matchup['win_rate']
        if matchup['num_matches'] >= 15 and data_pos in opposing_team_positions and \
                opposing_team_positions[data_pos]['hero_name'] == data_hero:
            if tracker_position == position:
                wr_list.append(data_wr)
    return wr_list


def new_dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions):
    start_time = time.time()

    radiant_wr_with, dire_wr_with, radiant_wr_against, dire_wr_against = [], [], [], []

    hero_data_cache = {}

    # Fetch data concurrently
    with ThreadPoolExecutor() as executor:
        hero_futures = {pos: executor.submit(fetch_hero_data, radiant_heroes_and_positions[pos]['hero_name']) for
                        pos in radiant_heroes_and_positions if pos != 'pos5'}
        hero_futures.update(
            {pos: executor.submit(fetch_hero_data, dire_heroes_and_positions[pos]['hero_name']) for pos in
             dire_heroes_and_positions if pos != 'pos5'})

        for position, future in hero_futures.items():
            hero_data_cache[position] = future.result()

    # Process synergies and matchups
    for position in radiant_heroes_and_positions:
        if position != 'pos5' and hero_data_cache.get(position):
            matchups, synergies = hero_data_cache[position]
            radiant_wr_with.extend(process_synergy_data(position, synergies, radiant_heroes_and_positions))
            radiant_wr_against.extend(process_matchup_data(position, matchups, dire_heroes_and_positions))

    for position in dire_heroes_and_positions:
        if position != 'pos5' and hero_data_cache.get(position):
            matchups, synergies = hero_data_cache[position]
            dire_wr_with.extend(process_synergy_data(position, synergies, dire_heroes_and_positions))
            dire_wr_against.extend(process_matchup_data(position, matchups, radiant_heroes_and_positions))

    radiant_wr_with = clean_up(radiant_wr_with, 4)
    dire_wr_with = clean_up(dire_wr_with, 4)
    radiant_wr_against = clean_up(radiant_wr_against, 5)
    dire_wr_against = clean_up(dire_wr_against, 5)

    synergy = round((sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with)),
                    2) if radiant_wr_with and dire_wr_with else None
    counterpick = round(
        (sum(radiant_wr_against) / len(radiant_wr_against)) - (sum(dire_wr_against) / len(dire_wr_against)),
        2) if radiant_wr_against and dire_wr_against else None

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time Dota2protracker: {execution_time:.2f} seconds")

    return f'\nDota2protracker:\nSynergy: {synergy}\nCounterpick: {counterpick}\n'


def dota2protracker_old(radiant_heroes_and_positions, dire_heroes_and_positions, synergy=None,
                        counterpick=None):
    start_time = time.time()
    radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team,\
        dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
    radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against,\
        dire_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team,\
        radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [], [], [], [], [], [], [], None, None
    for position in radiant_heroes_and_positions:
        if position != 'pos5':
            hero_url = radiant_heroes_and_positions[position]['hero_name'].replace(' ', '%20')
            url = f'https://dota2protracker.com/hero/{hero_url}'
            response = requests.get(url)
            if response.status_code != 200:
                print(f'Ошибка dota2protracker\n{url}')
            soup = BeautifulSoup(response.text, 'lxml')
            stats = soup.find_all('script')
            matchups = re.search(r'matchups:(\[.*?])', stats[5].text, re.DOTALL)
            synergies = re.search(r'synergies:(\[.*?])', stats[5].text, re.DOTALL)
            matchups, synergies = json.loads(str_to_json(matchups.group(1)).strip()), json.loads(
                str_to_json(synergies.group(1)).strip())
            for synergy in synergies:
                tracker_position = synergy['position'].replace('pos ', 'pos')
                data_pos = synergy['other_pos'].replace('pos ', 'pos')
                data_hero = synergy['other_hero']
                data_wr = synergy['win_rate']
                if synergy['num_matches'] >= 15:
                    # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                    if position == 'pos1':
                        if 'pos2' in data_pos and data_hero == radiant_heroes_and_positions['pos2'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)
                        elif 'pos3' in data_pos and data_hero == radiant_heroes_and_positions['pos3'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)
                        elif 'pos4' in data_pos and data_hero == radiant_heroes_and_positions['pos4'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)
                        elif 'pos5' in data_pos and data_hero == radiant_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)

                    if position == 'pos2':
                        if 'pos3' in data_pos and data_hero == radiant_heroes_and_positions['pos3'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos2_with_team.append(data_wr)
                        elif 'pos4' in data_pos and data_hero == radiant_heroes_and_positions['pos4'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos2_with_team.append(data_wr)
                        elif 'pos5' in data_pos and data_hero == radiant_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos2_with_team.append(data_wr)

                    if position == 'pos3':
                        if 'pos4' in data_pos and data_hero == radiant_heroes_and_positions['pos4'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos3_with_team.append(data_wr)
                        elif 'pos5' in data_pos and data_hero == radiant_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos3_with_team.append(data_wr)
                    if position == 'pos4':
                        if radiant_pos4_with_pos5 is not None:
                            break
                        if 'pos5' in data_pos and data_hero == radiant_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            radiant_pos4_with_pos5 = data_wr
    if radiant_pos4_with_pos5 is not None:
        radiant_wr_with += [radiant_pos4_with_pos5]
    radiant_wr_with += radiant_pos3_with_team + radiant_pos2_with_team + radiant_pos1_with_team
    for position in dire_heroes_and_positions:

        if position != 'pos5':
            hero_url = dire_heroes_and_positions[position]['hero_name'].replace(' ', '%20')
            url = f'https://dota2protracker.com/hero/{hero_url}'
            response = requests.get(url)
            if response.status_code != 200:
                print(f'Ошибка dota2protracker\n{url}')
            soup = BeautifulSoup(response.text, 'lxml')
            stats = soup.find_all('script')
            matchups = re.search(r'matchups:(\[.*?])', stats[5].text, re.DOTALL)
            synergies = re.search(r'synergies:(\[.*?])', stats[5].text, re.DOTALL)
            matchups, synergies = json.loads(str_to_json(matchups.group(1)).strip()), json.loads(
                str_to_json(synergies.group(1)).strip())
            for synergy in synergies:
                tracker_position = synergy['position'].replace('pos ', 'pos')
                data_pos = synergy['other_pos'].replace('pos ', 'pos')
                data_hero = synergy['other_hero']
                data_wr = synergy['win_rate']
                if synergy['num_matches'] >= 15:
                    if position == 'pos1':
                        if 'pos2' in data_pos and data_hero == dire_heroes_and_positions['pos2'][
                                'hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)
                        elif 'pos3' in data_pos and data_hero == dire_heroes_and_positions['pos3'][
                                'hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)
                        elif 'pos4' in data_pos and data_hero == dire_heroes_and_positions['pos4'][
                                'hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)
                        elif 'pos5' in data_pos and data_hero == dire_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)

                    if position == 'pos2':
                        if 'pos3' in data_pos and data_hero == dire_heroes_and_positions['pos3'][
                                'hero_name'] and tracker_position == position:
                            dire_pos2_with_team.append(data_wr)
                        elif 'pos4' in data_pos and data_hero == dire_heroes_and_positions['pos4'][
                                'hero_name'] and tracker_position == position:
                            dire_pos2_with_team.append(data_wr)
                        elif 'pos5' in data_pos and data_hero == dire_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            dire_pos2_with_team.append(data_wr)

                    if position == 'pos3':
                        if 'pos4' in data_pos and data_hero == dire_heroes_and_positions['pos4'][
                                'hero_name'] and tracker_position == position:
                            dire_pos3_with_team.append(data_wr)
                        elif 'pos5' in data_pos and data_hero == dire_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            dire_pos3_with_team.append(data_wr)
                    if position == 'pos4':
                        if dire_pos4_with_pos5 is not None:
                            break
                        if 'pos5' in data_pos and data_hero == dire_heroes_and_positions['pos5'][
                                'hero_name'] and tracker_position == position:
                            dire_pos4_with_pos5 = data_wr
    if dire_pos4_with_pos5 is not None:
        dire_wr_with += [dire_pos4_with_pos5]
    dire_wr_with += dire_pos3_with_team + dire_pos2_with_team + dire_pos1_with_team
    for position in radiant_heroes_and_positions:

        hero_url = radiant_heroes_and_positions[position]['hero_name'].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка dota2protracker\n{url}')
        soup = BeautifulSoup(response.text, 'lxml')
        stats = soup.find_all('script')
        matchups = re.search(r'matchups:(\[.*?])', stats[5].text, re.DOTALL)
        synergies = re.search(r'synergies:(\[.*?])', stats[5].text, re.DOTALL)
        matchups, synergies = json.loads(str_to_json(matchups.group(1)).strip()), json.loads(
            str_to_json(synergies.group(1)).strip())
        for matchup in matchups:
            tracker_position = matchup['position'].replace('pos ', 'pos')
            data_pos = matchup['other_pos'].replace('pos ', 'pos')
            data_hero = matchup['other_hero']
            data_wr = matchup['win_rate']
            if matchup['num_matches'] >= 15 and data_pos in radiant_heroes_and_positions:
                if position == 'pos1' and tracker_position == 'pos1' and data_hero == \
                        dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_pos1_vs_team.append(data_wr)
                elif position == 'pos2' and tracker_position == 'pos2' and data_hero == \
                        dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_pos2_vs_team.append(data_wr)
                elif position == 'pos3' and tracker_position == 'pos3' and data_hero == \
                        dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_pos3_vs_team.append(data_wr)
                elif position == 'pos4' and tracker_position == 'pos4' and data_hero == \
                        dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_wr_against.append(data_wr)
                elif position == 'pos5' and tracker_position == 'pos5' and data_hero == \
                        dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_wr_against.append(data_wr)

                if 'pos1' in data_pos and data_hero == dire_heroes_and_positions['pos1'][
                        'hero_name'] and tracker_position == position:
                    dire_pos1_vs_team.append(100 - data_wr)
                elif 'pos2' in data_pos and data_hero == dire_heroes_and_positions['pos2'][
                        'hero_name'] and tracker_position == position:
                    dire_pos2_vs_team.append(100 - data_wr)
                elif 'pos3' in data_pos and data_hero == dire_heroes_and_positions['pos3'][
                        'hero_name'] and tracker_position == position:
                    dire_pos3_vs_team.append(100 - data_wr)
    radiant_wr_against += radiant_pos3_vs_team + radiant_pos2_vs_team + radiant_pos1_vs_team
    dire_wr_against += dire_pos3_vs_team + dire_pos2_vs_team + dire_pos1_vs_team
    if len(radiant_wr_with) > 0 and len(dire_wr_with) > 0:
        synergy = round((sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with)), 2)
    if len(radiant_wr_against) > 0:
        counterpick = round((sum(radiant_wr_against) / len(radiant_wr_against)) - (
                sum(dire_wr_against) / len(dire_wr_against)), 2)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'dota2protracker_old time: {execution_time}s')
    return f'\ndota2protracker_old:\nSynergy: {synergy}\nCounterpick: {counterpick}\n'


def some_func():
    with open('teams_stat_dict.txt', 'r') as f:
        data = json.load(f)
        data_copy = data.copy()
        for team in data_copy:
            odd = data[team]['kills'] / data[team]['time']
            data.setdefault(team, {}).setdefault('odd', odd)
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1]["odd"]))
    with open('teams_stat_dict.txt', 'w') as f:
        json.dump(sorted_data, f, indent=4)


def get_pro_players_ids(counter=0):
    bottle, pro_ids = set(), set()
    for name in pro_teams:
        counter += 1
        print(f'{counter}/{len(pro_teams)}')
        bottle.add(pro_teams[name]['id'])
        if len(bottle) == 5 or counter == len(pro_teams):
            query = '''
                    {teams(teamIds: %s){
                        members{
                            lastMatchDateTime
                        steamAccount{
                          id
                          name

                        }
                        team {
                          id
                          name
                        }
                      }
                    }}''' % list(bottle)
            headers = {"Authorization": f"Bearer {api_token_5}"}
            response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
            teams = json.loads(response.text)['data']['teams']
            for team in teams:
                last_date = 0
                for member in team['members']:
                    if last_date < member['lastMatchDateTime']:
                        last_date = member['lastMatchDateTime']
                for member in team['members']:
                    if member['lastMatchDateTime'] == last_date:
                        pro_ids.add(member['steamAccount']['id'])
            bottle = set()
    return pro_ids


def get_maps_new(game_mods, maps_to_save, ids,
                 show_prints=None, skip=0, count=0, only_in_ids=False):
    tokens = [api_token_3, api_token_4, api_token_5, api_token_2, api_token_1, api_token_6, api_token_7,
              api_token_8, api_token_9, api_token_10, api_token_11, api_token_12, api_token_13, api_token_14,
              api_token_15, api_token_16, api_token_17, api_token_18]
    api_token = api_token_16
    ids_to_graph, total_map_ids, output_data = [], [], []
    for check_id in set(ids):
        count += 1
        ids_to_graph.append(check_id)

        if show_prints:
            print(f'{count}/{len(ids)}')

        if len(ids_to_graph) == 5 or count == len(ids):
            api_token, tokens = proceed_get_maps(ids=ids, skip=skip, game_mods=game_mods, only_in_ids=only_in_ids,
                                   output_data=output_data, ids_to_graph=ids_to_graph, tokens=tokens, api_token=api_token)
            ids_to_graph = []  # Очистка после обработки

    if len(output_data) > 0:
        with open(f'{maps_to_save}.txt', 'r+') as f:
            data = json.load(f)
            f.truncate()
            f.seek(0)
            out = list(set(output_data + data))
            json.dump(out, f)


def proceed_get_maps(skip, ids, only_in_ids, output_data, tokens, api_token, ids_to_graph=None, game_mods=None, check=True):
    while check:
        if game_mods == [2, 22]:
            query = '''
            {
              players(steamAccountIds: %s) {
                steamAccountId
                matchesFirstPeriod: matches(request: {startDateTime: 1727827200,
                 take: 100, skip: %s, gameModeIds: %s}) {
                  id
              }}
            }''' % (ids_to_graph, skip, game_mods)
        else:
            query = '''
            {
              teams(teamIds: %s) {
                matches(request: {startDateTime: 1716336000, take: 100, skip: %s}) {
                  id
                  radiantTeam {
                    name
                    id
                  }
                  direTeam {
                    name
                    id
                  }
                }
              }
            }''' % (ids_to_graph, skip)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": "https://api.stratz.com",
            "Referer": "https://api.stratz.com/graphiql",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {api_token}"
        }
        try:
            response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
            data = json.loads(response.text)
            if game_mods == [2, 22]:
                if any(player['matchesFirstPeriod'] for player in data['data']['players']):
                    for player in data['data']['players']:
                        for match in player['matchesFirstPeriod']:
                            output_data.append(match['id'])
                        skip += 100
                else:
                    check = False
            else:
                for team in data['data']['teams']:
                    for match in team['matches']:
                        if only_in_ids:
                            if match['radiantTeam']['id'] in ids and match['direTeam']['id'] in ids:
                                output_data.append(match['id'])
                        else:
                            output_data.append(match['id'])
                        check = False
        except Exception as e:
            print(f"Unexpected error: {e}")
            if tokens:
                api_token = tokens.pop(0)
                print('меняю токен')

            else:
                tokens = [api_token_3, api_token_4, api_token_5, api_token_2, api_token_1, api_token_6, api_token_7,
                          api_token_8, api_token_9, api_token_10, api_token_11, api_token_12, api_token_13,
                          api_token_14,
                          api_token_15, api_token_16, api_token_17]
                api_token = tokens.pop(0)
                print('обновляю токены')
    return api_token, tokens


def eat_temp_files(mkdir, file_data, file_name):
    folder_path = f"./{mkdir}/temp_files"
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'r') as f:
                data = json.load(f)
                for map_id in data:
                    if map_id not in file_data:
                        file_data[map_id] = data[map_id]
        with open(f'./{mkdir}/{file_name}_new.txt', 'w') as f:
            json.dump(file_data, f)
        os.remove(f'./{mkdir}/{file_name}.txt')
        os.rename(f'./{mkdir}/{file_name}_new.txt', f'./{mkdir}/{file_name}.txt')
        shutil.rmtree(f'./{mkdir}/temp_files')
        return file_data


def research_map_proceed(maps_to_explore, file_data, file_name, mkdir, counter=0, another_counter=0,
                         show_prints=None):
    tokens = [api_token_3, api_token_4, api_token_5, api_token_2, api_token_1, api_token_6, api_token_7,
              api_token_8, api_token_9, api_token_10, api_token_11, api_token_12, api_token_13, api_token_14,
              api_token_15, api_token_16, api_token_17]
    api_token = tokens.pop()
    new_data, error_maps = {}, set()
    # Попытка загрузить временные данные
    answer = eat_temp_files(mkdir, file_data, file_name)
    if answer is not None:
        file_data = answer

    new_maps = [map_id for map_id in maps_to_explore if str(map_id) not in file_data]
    # Основной цикл по картам
    for map_id in new_maps:
        # Проверка, если данные по карте уже есть
        another_counter += 1
        if show_prints:
            print(f'{another_counter}/{len(new_maps)}')
        # Сохраняем данные каждые 300 итераций
        if another_counter % 300 == 0:
            save_temp_file(new_data, mkdir, another_counter)
            new_data = {}

        try:
            query = '''
            {
              match(id:%s){
                startDateTime
                league{
                  id
                  tier
                  region
                  basePrizePool
                  prizePool
                  tournamentUrl
                  displayName
                }
                direTeam{
                  id
                  name
                }
                radiantTeam{
                  id
                  name
                }
                id
                direKills
                radiantKills
                bottomLaneOutcome
                topLaneOutcome
                midLaneOutcome
                radiantNetworthLeads
                didRadiantWin
                durationSeconds
                players{
                  steamAccount{
                    id
                    isAnonymous
                  }
                  imp
                  position
                  isRadiant
                  hero{
                    id
                  }
                }
              }
            }''' % map_id

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Origin": "https://api.stratz.com",
                "Referer": "https://api.stratz.com/graphiql",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Authorization": f"Bearer {api_token}"
            }
            response = requests.post('https://api.stratz.com/graphql', json={"query": query},
                                     headers=headers, timeout=5)
            if 'data' in response.json():
                data = response.json()['data']['match']

            else:
                raise requests.exceptions.RequestException
            if data['direKills'] is not None:
                new_data[map_id] = data  # Сохраняем данные карты
        except Exception as e:
            print(f"Unexpected error: {e}")
            if tokens:
                api_token = tokens.pop(0)
                print('меняю токен')

            else:
                tokens = [api_token_3, api_token_4, api_token_5, api_token_2, api_token_1, api_token_6, api_token_7,
                          api_token_8, api_token_9, api_token_10, api_token_11, api_token_12, api_token_13,
                          api_token_14,
                          api_token_15, api_token_16, api_token_17]
                api_token = tokens.pop(0)
                print('обновляю токены')
    eat_temp_files(mkdir, file_data, file_name)

def save_temp_file(new_data, mkdir, another_counter):
    print('Сохраняю результат')
    # Создание папки для временных файлов
    temp_folder = f"./{mkdir}/temp_files"
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)

    path = f'{temp_folder}/{another_counter}.txt'

    # Генерация уникального имени файла
    while os.path.isfile(path):
        another_counter += 1
        path = f'{temp_folder}/{another_counter}.txt'

    # Сохранение данных во временный файл
    with open(path, 'w') as f:
        json.dump(new_data, f)


def save_final_file(file_data, mkdir, file_name):
    # Сохранение финальных данных в файл
    final_path = f'./{mkdir}/{file_name}.txt'
    with open(final_path, 'w') as f:
        json.dump(file_data, f)


def research_maps(maps_to_explore, file_name, mkdir, show_prints=None):
    path = f'./{mkdir}/{maps_to_explore}.txt'
    with open(path, 'r+') as f:
        maps_to_explore = json.load(f)
    with open(f'./{mkdir}/{file_name}.txt', 'r+') as f:
        file_data = json.load(f)
    research_map_proceed(
        maps_to_explore=maps_to_explore, file_data=file_data,
        file_name='1722505765_top600_output', mkdir='1722505765_top600_heroes_data', show_prints=True)



def update_2v1_lanes(dire_heroes_and_pos, radiant_heroes_and_pos, match, lane_dict):
    lane_data = [
        (match.get('bottomLaneOutcome'), [
            f'{radiant_heroes_and_pos.get("pos1")},{radiant_heroes_and_pos.get("pos5")}_vs_'
            f'{dire_heroes_and_pos.get("pos3")}',
            f'{radiant_heroes_and_pos.get("pos1")},{radiant_heroes_and_pos.get("pos5")}_vs_'
            f'{dire_heroes_and_pos.get("pos4")}'
        ]),
        (match.get('topLaneOutcome'), [
            f'{radiant_heroes_and_pos.get("pos3")},{radiant_heroes_and_pos.get("pos4")}_vs_'
            f'{dire_heroes_and_pos.get("pos1")}',
            f'{radiant_heroes_and_pos.get("pos3")},{radiant_heroes_and_pos.get("pos4")}_vs_'
            f'{dire_heroes_and_pos.get("pos5")}'
        ]),
        (match.get('midLaneOutcome'), [
            f'{radiant_heroes_and_pos.get("pos2")}_vs_{dire_heroes_and_pos.get("pos2")}'
        ])
    ]

    for lane_outcome, matchup_keys in lane_data:
        if lane_outcome is None:
            continue

        radiant_won = 'RADIANT' in lane_outcome
        dire_won = 'DIRE' in lane_outcome
        outcome_radiant = 1 if radiant_won else (0 if dire_won else 2)
        outcome_dire = 0 if radiant_won else (1 if dire_won else 2)

        for matchup_key in matchup_keys:
            lane_dict.setdefault('2v1_lanes', {}).setdefault(matchup_key, {}).setdefault('value', []).append(
                outcome_radiant)
            lane_dict.setdefault('2v1_lanes', {}).setdefault(matchup_key, {}).setdefault('value', []).append(
                outcome_dire)

    return lane_dict


def new_proceed_map(match, map_id, players_imp_data, lane_dict, synergy_and_counterpick_dict,
                    total_time_kills_dict, over45_dict, over35_dict, total_time_kills_dict_teams=None,
                    radiant_team_name=None, dire_team_name=None):
    radiant_heroes_and_pos = {}
    dire_heroes_and_pos = {}

    # Заполняем позиции для героев Radiant и Dire
    for player in match.get('players', []):
        hero_id = player.get('hero', {}).get('id')
        position = player.get('position')

        if hero_id is None or position is None:
            continue

        position_key = f'pos{position[-1]}'
        if player.get('isRadiant'):
            radiant_heroes_and_pos[position_key] = hero_id
        else:
            dire_heroes_and_pos[position_key] = hero_id

    # Обновление информации о линиях
    lane_dict = update_2v1_lanes(dire_heroes_and_pos, radiant_heroes_and_pos, match, lane_dict)

    # Обработка игроков в матче
    radiant_win = match.get('didRadiantWin', False)

    for player in match.get('players', []):
        hero_id = str(player.get('hero', {}).get('id'))
        steam_id = str(player.get('steamAccount', {}).get('id'))
        position = player.get('position', '').replace('POSITION_', 'pos')
        is_radiant = player.get('isRadiant')

        if not hero_id or not steam_id or not position:
            continue

        if map_id not in players_imp_data.get('used_maps', []):
            if player.get('steamAccount', {}).get('isAnonymous', False):
                players_imp_data.setdefault('value', {}).setdefault(steam_id, {}).setdefault(hero_id, {}).setdefault(
                    position, []).append(player.get('imp'))
                players_imp_data.setdefault('used_maps', []).append(map_id)

        for another_player in match.get('players', []):
            another_hero_id = str(another_player.get('hero', {}).get('id'))
            if not another_hero_id or another_hero_id == hero_id:
                continue

            another_position = another_player.get('position', '').replace('POSITION_', 'pos')
            another_is_radiant = another_player.get('isRadiant')

            # Контрпики и синергия
            to_be_appended = 1 if (is_radiant and radiant_win) or (not is_radiant and not radiant_win) else 0
            if is_radiant != another_is_radiant:
                synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                      ['counterpick_duo', another_hero_id,
                                                                       another_position, 'value'],
                                                                      synergy_and_counterpick_dict)

            if is_radiant == another_is_radiant:
                synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                      ['synergy_duo', another_hero_id, another_position,
                                                                       'value'],
                                                                      synergy_and_counterpick_dict)

                # Обработка данных для матчей свыше 35 и 45 минут
                if match.get('durationSeconds', 0) / 60 >= 35:
                    over35_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                         ['over35_duo', another_hero_id, another_position, 'value'],
                                                         over35_dict)
                if match.get('durationSeconds', 0) / 60 >= 45:
                    over45_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                         ['over45_duo', another_hero_id, another_position, 'value'],
                                                         over45_dict)

                # Убийства и время
                total_kills = sum(match.get('direKills', [])) + sum(match.get('radiantKills', []))
                total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                               ['total_kills_duo', another_hero_id, another_position,
                                                                'value'],
                                                               total_time_kills_dict)
                total_time_kills_dict = distribute_heroes_data(hero_id, position, match.get('durationSeconds'),
                                                               ['total_time_duo', another_hero_id, another_position,
                                                                'value'],
                                                               total_time_kills_dict)

                # Командные данные
                if total_time_kills_dict_teams is not None:
                    team_name = radiant_team_name if is_radiant else dire_team_name
                    total_time_kills_dict_teams = distribute_heroes_data(hero_id, position, total_kills,
                                                                         ['total_kills_duo', another_hero_id,
                                                                          another_position, 'value'],
                                                                         total_time_kills_dict_teams,
                                                                         team_name=team_name)
                    total_time_kills_dict_teams = distribute_heroes_data(hero_id, position,
                                                                         match.get('durationSeconds'),
                                                                         ['total_time_duo', another_hero_id,
                                                                          another_position, 'value'],
                                                                         total_time_kills_dict_teams,
                                                                         team_name=team_name)

                # Тройки героев
                for third_player in match.get('players', []):
                    third_hero_id = str(third_player.get('hero', {}).get('id'))
                    third_position = third_player.get('position', '').replace('POSITION_', 'pos')
                    third_is_radiant = third_player.get('isRadiant')

                    if third_is_radiant == is_radiant == another_is_radiant and third_hero_id not in {hero_id,
                                                                                                      another_hero_id}:
                        synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                              ['synergy_duo', another_hero_id,
                                                                               another_position,
                                                                               'synergy_trio', third_hero_id,
                                                                               third_position, 'value'],
                                                                              synergy_and_counterpick_dict)

                        total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                       ['total_kills_duo', another_hero_id,
                                                                        another_position,
                                                                        'total_kills_trio', third_hero_id,
                                                                        third_position, 'value'],
                                                                       total_time_kills_dict)

                        total_time_kills_dict = distribute_heroes_data(hero_id, position, match.get('durationSeconds'),
                                                                       ['total_time_duo', another_hero_id,
                                                                        another_position,
                                                                        'total_time_trio', third_hero_id,
                                                                        third_position, 'value'],
                                                                       total_time_kills_dict)

    return lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict,\
        over45_dict, over35_dict, total_time_kills_dict_teams


def normalize_team_name(team_name):
    translate = {
        'g2 x ig': 'g2.invictus gaming',
        'lava esports ': 'lava uphone',
        'infinity': 'infinity esports',
        'fusion esports': 'fusion',
        'team hryvnia': 'passion.ua',
        'bocajuniors': 'team waska',
        'cuyes e-sports': 'cuyes esports',
        'boom esports': 'team waska',
        'entity': 'cloud9',
        'tea': 'avulus',
        'team tea': 'avulus',
        'wbg.xg': 'xtreme gaming',
        'talon': 'talon esports',
    }
    return translate.get(team_name.lower(), team_name.lower())


def process_pro_game(match, map_id, players_imp_data, lane_dict, synergy_and_counterpick_dict,
                     total_time_kills_dict, over45_dict, over35_dict, total_time_kills_dict_teams, team_stat_dict, count):
    radiant_team_name = normalize_team_name(match['radiantTeam']['name'])
    dire_team_name = normalize_team_name(match['direTeam']['name'])

    result = new_proceed_map(
        match=match, map_id=map_id, players_imp_data=players_imp_data,
        lane_dict=lane_dict, synergy_and_counterpick_dict=synergy_and_counterpick_dict,
        total_time_kills_dict=total_time_kills_dict, over45_dict=over45_dict,
        over35_dict=over35_dict, total_time_kills_dict_teams=total_time_kills_dict_teams,
        radiant_team_name=radiant_team_name, dire_team_name=dire_team_name)

    lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, \
        over35_dict, over45_dict, total_time_kills_dict_teams = result

    update_team_stats(team_stat_dict, radiant_team_name, match['radiantTeam']['id'], match)
    update_team_stats(team_stat_dict, dire_team_name, match['direTeam']['id'], match)

    return lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, \
        over35_dict, over45_dict, total_time_kills_dict_teams


def process_regular_game(match, map_id, players_imp_data, lane_dict, synergy_and_counterpick_dict,
                         total_time_kills_dict, over45_dict, over35_dict, total_time_kills_dict_teams, count):
    if (match['durationSeconds'] / 60) >= 21:
        result = new_proceed_map(
            match=match, map_id=map_id, players_imp_data=players_imp_data,
            lane_dict=lane_dict, synergy_and_counterpick_dict=synergy_and_counterpick_dict,
            total_time_kills_dict=total_time_kills_dict, over45_dict=over45_dict,
            over35_dict=over35_dict, total_time_kills_dict_teams=total_time_kills_dict_teams)

        lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, \
            over35_dict, over45_dict, total_time_kills_dict_teams = result
        print(f'{count}')
        return lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, \
            over35_dict, over45_dict, total_time_kills_dict_teams


def update_team_stats(team_stat_dict, team_name, team_id, match):
    team_stat_dict.setdefault(team_name, {}).setdefault('kills', []).append(
        sum(match['direKills']) + sum(match['radiantKills']))
    team_stat_dict.setdefault(team_name, {}).setdefault('time', []).append(match['durationSeconds'] / 60)
    team_stat_dict.setdefault(team_name, {}).setdefault('id', team_id)


def analyze_database(database, players_imp_data, over45_dict, used_maps=None,
                     total_time_kills_dict=None, pro=False,
                     over35_dict=None, synergy_and_counterpick_dict=None, lane_dict=None, show_prints=None,
                     count=0, total_time_kills_dict_teams=None):
    total, team_stat_dict = len(database), {}
    new_maps = [str(map_id) for map_id in database if str(map_id) not in used_maps]

    # Инициализируем итоговые словари для накопления данных

    for count, map_id in enumerate(new_maps, start=1):
        match = database[map_id]

        if pro:
            if all(name in match and match[name] is not None for name in ['direTeam', 'radiantTeam']):
                process_pro_game(match, map_id, players_imp_data, lane_dict,
                                         synergy_and_counterpick_dict, total_time_kills_dict, over45_dict,
                                         over35_dict, total_time_kills_dict_teams, team_stat_dict, count)
        else:
            if all(player['position'] is not None for player in match['players']):
                process_regular_game(match, map_id, players_imp_data, lane_dict,
                                         synergy_and_counterpick_dict, total_time_kills_dict, over45_dict,
                                         over35_dict, total_time_kills_dict_teams, count)

    if count > 0:
        used_maps = new_maps
        return players_imp_data, total_time_kills_dict, over35_dict, over45_dict, synergy_and_counterpick_dict, \
            lane_dict, team_stat_dict, total_time_kills_dict_teams, used_maps


def merge_dicts(dict1, dict2):
    """
    Функция для объединения двух словарей. Если ключи пересекаются, значения объединяются.
    Если ключ уникален, он просто добавляется.
    """
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict) and isinstance(dict1[key], dict):
                dict1[key] = merge_dicts(dict1[key], value)
            elif isinstance(value, list) and isinstance(dict1[key], list):
                dict1[key].extend(value)
            else:
                dict1[key] += value
        else:
            dict1[key] = value
    return dict1


def load_json_file(filepath, default):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)


def load_and_process_json_files(mkdir, **kwargs):
    result = {}
    for key, flag in kwargs.items():
        if flag:
            result[key] = load_json_file(f'./{mkdir}/{key}', {})
        else:
            result[key] = {}
    return result


def explore_database(mkdir, file_name, pro=False, show_prints=None, lane=None,
                     over45=None, over35=None, protracker=None, total_time_kills_teams=None, time_kills=None):
    database = load_json_file(f'./{mkdir}/{file_name}.txt', {})
    players_imp_data = load_json_file(f'./egb/players_imp_data.txt', {'used_maps': []})

    # Загрузка всех необходимых файлов
    data_files = load_and_process_json_files(
        mkdir, total_time_kills_dict=time_kills,
        over35_dict=over35, over45_dict=over45, synergy_and_counterpick_dict=protracker,
        lane_dict=lane, total_time_kills_dict_teams=total_time_kills_teams)

    used_maps = load_json_file(f'./{mkdir}/used_maps', [])

    result = analyze_database(
        database=database, players_imp_data=players_imp_data,
        total_time_kills_dict=data_files['total_time_kills_dict'], over45_dict=data_files['over45_dict'],
        synergy_and_counterpick_dict=data_files['synergy_and_counterpick_dict'],
        lane_dict=data_files['lane_dict'], pro=pro, used_maps=used_maps, over35_dict=data_files['over35_dict'],
        show_prints=show_prints, total_time_kills_dict_teams=data_files['total_time_kills_dict_teams'])

    if result is not None:
        players_imp_data, total_time_kills_dict, over35_dict, over45_dict, synergy_and_counterpick_dict, \
            lane_dict, team_stat_dict, total_time_kills_dict_teams, used_maps = result

        print('Сохранение обновленных данных')
        if protracker:
            save_json_file(f'./{mkdir}/synergy_and_counterpick_dict.txt', synergy_and_counterpick_dict)
        if over35:
            save_json_file(f'./{mkdir}/over35_dict.txt', over35_dict)
        if time_kills:
            save_json_file(f'./{mkdir}/total_time_kills_dict.txt', total_time_kills_dict)
        save_json_file(f'./egb/players_imp_data.txt', players_imp_data)
        if lane:
            save_json_file(f'./{mkdir}/lane_dict.txt', lane_dict)
        if over45:
            save_json_file(f'./{mkdir}/over45_dict.txt', over45_dict)
        if total_time_kills_teams:
            save_json_file(f'./{mkdir}/total_time_kills_dict_teams.txt', total_time_kills_dict_teams)
        save_json_file(f'./{mkdir}/used_maps.txt', used_maps)
        save_json_file(f'./{mkdir}/team_stats_dict.txt', team_stat_dict)


def distribute_heroes_data(hero_id, position, to_be_appended, path, heroes_data, team_name=None):
    # Определяем индекс массива на основе hero_id
    if team_name is not None:
        current_dict = heroes_data.setdefault('teams', {}).setdefault(team_name, {}).setdefault(hero_id, {}).setdefault(
            position, {})
    else:
        current_dict = heroes_data.setdefault('value', {}).setdefault(hero_id, {}).setdefault(position, {})
    for key in path[:-1]:
        current_dict = current_dict.setdefault(key, {})
        # Обрабатываем последний ключ, добавляя к списку нужное значение
    current_dict.setdefault(path[-1], []).append(to_be_appended)
    return heroes_data


def calculate_average(values):
    return sum(values) / len(values) if len(values) else None


def synergy_team(heroes_and_pos, enemy_heroes_and_pos, output, mkdir, data):
    unique_combinations = set()
    for pos in heroes_and_pos:
        hero_id = str(heroes_and_pos[pos]['hero_id'])
        hero_data = data.get(hero_id, {}).get(pos, {}).get('synergy_duo', {})
        for second_pos in heroes_and_pos:
            if pos == second_pos:
                continue
            second_hero_id = str(heroes_and_pos[second_pos]['hero_id'])
            duo_data = hero_data.get(second_hero_id, {}).get(second_pos, {})
            if len(duo_data.get('value', {})) >= 30:
                combo = tuple(sorted([hero_id, second_hero_id]))
                if combo not in unique_combinations:
                    unique_combinations.add(combo)
                    value = duo_data['value'].count(1) / (
                            duo_data['value'].count(1) + duo_data['value'].count(0))
                    if value > 0.52 or value < 0.48:
                        output[f'{mkdir}_duo'].append(value)
            for third_pos in heroes_and_pos:
                if third_pos not in [pos, second_pos]:
                    third_hero_id = str(heroes_and_pos[third_pos]['hero_id'])
                    trio_data = duo_data.get('synergy_trio', {}).get(third_hero_id, {}).get(third_pos, {})
                    if len(trio_data.get('value', {})) >= 15:
                        combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                        if combo not in unique_combinations:
                            unique_combinations.add(combo)
                            value = trio_data['value'].count(1) / (
                                    trio_data['value'].count(1) + trio_data['value'].count(0))
                            if value > 0.52 or value < 0.48:
                                output[f'{mkdir}_trio'].append(value)
            for enemy_third_pos in enemy_heroes_and_pos:
                third_hero_id = str(enemy_heroes_and_pos[enemy_third_pos]['hero_id'])
                trio_data = duo_data.get('2vs1', {}).get(third_hero_id, {}).get(enemy_third_pos, {})
                if len(trio_data.get('value', {})) >= 10:
                    combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                    if combo not in unique_combinations:
                        unique_combinations.add(combo)
                        value = trio_data['value'].count(1) / (
                                trio_data['value'].count(1) + trio_data['value'].count(0))
                        if value > 0.52 or value < 0.48:
                            output[f'{mkdir}_2vs1'].append(value)

    return output


def counterpick_team(heroes_and_pos, heroes_and_pos_opposite, output, mkdir, data):
    unique_combinations = set()
    for pos in heroes_and_pos:
        hero_id = str(heroes_and_pos[pos]['hero_id'])
        hero_data = data.get(hero_id, {}).get(pos, {}).get('counterpick_duo', {})
        for second_pos in heroes_and_pos_opposite:
            second_hero_id = str(heroes_and_pos_opposite[second_pos]['hero_id'])
            duo_data = hero_data.get(second_hero_id, {}).get(second_pos, {})
            if len(duo_data.get('value', {})) >= 15:
                combo = tuple(sorted([hero_id, second_hero_id]))
                if combo not in unique_combinations:
                    unique_combinations.add(combo)
                    value = duo_data['value'].count(1) / (
                            duo_data['value'].count(1) + duo_data['value'].count(0))
                    if value > 0.52 or value < 0.48:
                        output[f'{mkdir}_duo'].append(value)
    return output


def synergy_and_counterpick_new(radiant_heroes_and_pos, dire_heroes_and_pos):
    start_time = time.time()
    output = {'radiant_synergy_duo': [], 'dire_synergy_duo': [], 'radiant_synergy_trio': [], 'dire_synergy_trio': [],
              'radiant_counterpick_duo': [], 'dire_counterpick_duo': [], 'radiant_synergy_2vs1': [],
              'dire_synergy_2vs1': []}
    with open('./1722505765_top600_heroes_data/synergy_and_counterpick_dict.txt', 'r') as f:
        data = json.load(f)['value']
    # Process Radiant heroes
    output = synergy_team(radiant_heroes_and_pos, dire_heroes_and_pos, output, 'radiant_synergy', data)

    # Process Dire heroes
    output = synergy_team(dire_heroes_and_pos, radiant_heroes_and_pos, output, 'dire_synergy', data)
    output = counterpick_team(radiant_heroes_and_pos, dire_heroes_and_pos, output,
                              'radiant_counterpick', data)
    output = counterpick_team(dire_heroes_and_pos, radiant_heroes_and_pos, output,
                              'dire_counterpick', data)
    counterpick_duo = (sum(output['radiant_counterpick_duo']) / len(output['radiant_counterpick_duo']) - sum(output['dire_counterpick_duo']) / len(output['dire_counterpick_duo']))*100
    if len(output['radiant_synergy_2vs1']) > 0 and len(output['dire_synergy_2vs1']) > 0:
        counterpick2vs1 = (sum(output['radiant_synergy_2vs1']) / len(
            output['radiant_synergy_2vs1'])) / 2 - (sum(output['dire_synergy_2vs1']) / len(
            output['dire_synergy_2vs1'])) / 2
    synergy_duo = (sum(output['radiant_synergy_duo']) / len(output['radiant_synergy_duo']) - sum(output['dire_synergy_duo']) / len(output['dire_synergy_duo']))*100
    if len(output['dire_synergy_trio']) > 0 and len(output['radiant_synergy_trio']) > 0:
        synergy_trio = (((sum(output['radiant_synergy_trio']) / len(
            output['radiant_synergy_trio'])) / 2) - ((sum(output['dire_synergy_trio']) / len(output['dire_synergy_trio'])) / 2))*100
    else:
        synergy_trio = None
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'synergy_and_counterpick_new time: {execution_time}s')
    return f'\nsynergy_and_counterpick_new:\nSynergy_duo: {synergy_duo}\nSynergy_trio: {synergy_trio}\nCounterpick_duo: {counterpick_duo}\n'


def calculate_over45(radiant_heroes_and_pos, dire_heroes_and_pos):
    with open('./1722505765_top600_heroes_data/over45_dict.txt', 'r') as f:
        data = json.load(f)['value']
    radiant_over45 = avg_over45(radiant_heroes_and_pos, data)
    dire_over45 = avg_over45(dire_heroes_and_pos, data)
    if radiant_over45 is not None and dire_over45 is not None:
        over45 = (radiant_over45 - dire_over45) * 100
    else:
        over45 = None
    return f'Radiant после 45 минуты сильнее на: {over45}\n'


def avg_over45(heroes_and_positions, data):
    start_time = time.time()
    over45_duo, over45_trio, time_duo, kills_duo, kills_trio, time_trio, radiant_lane_report_unique_combinations,\
        dire_lane_report_unique_combinations = [], [], [], [], [], [], [], []
    over45_unique_combinations = set()
    positions = ['1', '2', '3', '4', '5']
    for pos in positions:
        hero_id = str(heroes_and_positions.get(('pos' + pos), {}).get('hero_id', {}))
        hero_data = data.get(hero_id, {}).get('pos' + pos, {}).get('over45_duo', {})
        for pos2, item in heroes_and_positions.items():
            second_hero_id = str(item['hero_id'])
            if second_hero_id == hero_id:
                continue
            duo_data = hero_data.get(second_hero_id, {}).get(pos2, {})
            combo = tuple(sorted([hero_id, second_hero_id]))
            if combo not in over45_unique_combinations:
                over45_unique_combinations.add(combo)
                if len(duo_data.get('value', {})) >= 15:
                    value = duo_data['value'].count(1)/(duo_data['value'].count(1)+duo_data['value'].count(0))
                    if value > 0.52 or value < 0.48:
                        over45_duo.append(value)
            # Третий герой
            for pos3, item3 in heroes_and_positions.items():
                third_hero_id = str(item3['hero_id'])
                if third_hero_id in [second_hero_id, hero_id]:
                    continue
                combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                if combo not in over45_unique_combinations:
                    over45_unique_combinations.add(combo)
                    trio_data = duo_data.get('over45_trio', {}).get(third_hero_id, {}).get(pos3, {}).get('value', {})
                    if len(trio_data) >= 10:
                        value = trio_data.count(1)/(trio_data.count(1) + trio_data.count(0))
                        if value > 0.52 or value < 0.48:
                            over45_trio.append(value)

    avg_over45_duo = calculate_average(over45_duo)
    avg_over45_trio = calculate_average(over45_trio)
    avg_over45 = (avg_over45_duo + avg_over45_trio) / 2 if avg_over45_trio is not None else avg_over45_duo
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'over45 time: {execution_time}s')
    return avg_over45


def calculate_lanes(radiant_heroes_and_pos, dire_heroes_and_pos):
    with open('./1722505765_top600_heroes_data/lane_dict.txt', 'r') as f:
        heroes_data = json.load(f)
    lane_2vs1(radiant_heroes_and_pos, radiant_heroes_and_pos, heroes_data)
    # radiant_lane_report = lane_report_def(my_team=radiant_heroes_and_pos, enemy_team=dire_heroes_and_pos,
    #                                       heroes_data=heroes_data)
    # dire_lane_report = lane_report_def(my_team=dire_heroes_and_pos, enemy_team=radiant_heroes_and_pos,
    #                                    heroes_data=heroes_data)
    # lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
    # return f'Radiant lanes до 10 минуты: {lane_report}\n'


def new_lane_report_def(radiant, dire, heroes_data):
    name = f"{radiant['pos1']['hero_id']},{radiant['pos5']['hero_id']}_vs_" \
           f"{dire['pos3']['hero_id']},{dire['pos4']['hero_id']}"
    data = heroes_data.get(name, {})
    if len(data) > 0:
        pass
    data = heroes_data.get(f"{radiant['pos3']['hero_id']},{radiant['pos4']['hero_id']}_vs_"
                           f"{dire['pos1']['hero_id']},{dire['pos5']['hero_id']}", {})
    if len(data) > 0:
        pass
    data = heroes_data.get(f"{radiant['pos2']['hero_id']}_vs_{dire['pos2']['hero_id']}", {})
    if len(data) > 0:
        pass
    pass


def lane_2vs1(radiant_heroes_and_pos, dire_heroes_and_pos, heroes_data):
    heroes_data = heroes_data['2v1_lanes']
    radiant, dire = [], []
    for key in [
            f'{radiant_heroes_and_pos["pos1"]["hero_id"]},{radiant_heroes_and_pos["pos5"]["hero_id"]}_vs_'
            f'{dire_heroes_and_pos["pos3"]["hero_id"]}', f'{radiant_heroes_and_pos["pos1"]["hero_id"]},'
            f'{radiant_heroes_and_pos["pos5"]["hero_id"]}_vs_{dire_heroes_and_pos["pos4"]["hero_id"]}',
            f'{radiant_heroes_and_pos["pos3"]["hero_id"]},{radiant_heroes_and_pos["pos4"]["hero_id"]}_vs_'
            f'{dire_heroes_and_pos["pos1"]["hero_id"]}', f'{radiant_heroes_and_pos["pos3"]["hero_id"]},'
            f'{radiant_heroes_and_pos["pos4"]["hero_id"]}_vs_{dire_heroes_and_pos["pos5"]["hero_id"]}']:

        value = heroes_data.get(key, {}).get('value', [])
        if len(value) > 5:
            radiant.append(value.count(1)/(value.count(1) + value.count(2) + value.count(0)))
    for key in [
            f'{dire_heroes_and_pos["pos1"]["hero_id"]},{dire_heroes_and_pos["pos5"]["hero_id"]}_vs_'
            f'{radiant_heroes_and_pos["pos3"]["hero_id"]}', f'{dire_heroes_and_pos["pos1"]["hero_id"]},'
            f'{dire_heroes_and_pos["pos5"]["hero_id"]}_vs_{radiant_heroes_and_pos["pos4"]["hero_id"]}',
            f'{dire_heroes_and_pos["pos3"]["hero_id"]},{dire_heroes_and_pos["pos4"]["hero_id"]}_vs_'
            f'{radiant_heroes_and_pos["pos1"]["hero_id"]}', f'{dire_heroes_and_pos["pos3"]["hero_id"]},'
            f'{dire_heroes_and_pos["pos4"]["hero_id"]}_vs_{radiant_heroes_and_pos["pos5"]["hero_id"]}']:

        value = heroes_data.get(key, {}).get('value', [])
        if len(value) > 5:
            dire.append(value.count(1) / (value.count(1) + value.count(2) + value.count(0)))
    pass


def lane_report_def(my_team, enemy_team, heroes_data):
    heroes_data = heroes_data['value']
    # print('lane_report')
    start_time = time.time()
    avg_kills, avg_time, team_line_report, over45, over40, over45, over50, over55 = [], [], [], [], [], [], [], []
    copy_team_pos_and_heroes = {data['hero_id']: pos for pos, data in my_team.items()}
    for hero_id in copy_team_pos_and_heroes:
        pos = copy_team_pos_and_heroes[hero_id]
        data = heroes_data[str(hero_id)]
        if pos in data:
            if pos == 'pos1':
                try:
                    team_mate_hero_id = str(my_team['pos5']['hero_id'])
                    team_mate_data = data[pos]['lane_report']['with_hero'][team_mate_hero_id]['pos5']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                value = team_mate_data.count(1) / (
                        team_mate_data.count(1) + team_mate_data.count(0))
                if value > 0.52 or value < 0.48:
                    team_line_report.append(value)
            elif pos == 'pos3':
                try:
                    team_mate_hero_id = str(my_team['pos4']['hero_id'])
                    team_mate_data = \
                        data[pos]['lane_report']['with_hero'][team_mate_hero_id]['pos4']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                value = team_mate_data.count(1) / (
                        team_mate_data.count(1) + team_mate_data.count(0))
                if value > 0.52 or value < 0.48:
                    team_line_report.append(value)
            elif pos == 'pos2':
                try:
                    team_mate_hero_id = str(enemy_team['pos2']['hero_id'])
                    team_mate_data = data[pos]['lane_report']['against_hero'][team_mate_hero_id]
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                value = team_mate_data.count(1) / (
                        team_mate_data.count(1) + team_mate_data.count(0))
                if value > 0.52 or value < 0.48:
                    team_line_report.append(value)
    team_avg_lanes = sum(team_line_report) / len(team_line_report)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f'lanes time: {execution_time}s')
    return round(team_avg_lanes, 2)


def tm_kills(radiant_heroes_and_positions, dire_heroes_and_positions):
    output_data = {'dire_kills_duo': [], 'dire_kills_trio': [], 'dire_time_duo': [], 'dire_time_trio': [],
                   'radiant_kills_duo': [], 'radiant_kills_trio': [], 'radiant_time_duo': [], 'radiant_time_trio': []}
    # print('tm_kills')
    positions = ['1', '2', '3', '4', '5']
    radiant_time_unique_combinations, radiant_kills_unique_combinations, dire_kills_unique_combinations, \
        dire_time_unique_combinations = set(), set(), set(), set()
    with open('./pro_heroes_data/total_time_kills_dict.txt', 'r') as f:
        data = json.load(f)['value']
    for pos in positions:
        # radiant_synergy
        hero_id = str(radiant_heroes_and_positions['pos' + pos]['hero_id'])
        time_data = data.get(hero_id, {}).get('pos' + pos, {}).get('total_time_duo', {})
        kills_data = data.get(hero_id, {}).get('pos' + pos, {}).get('total_kills_duo', {})
        for hero_data in [time_data, kills_data]:
            for pos2, item in radiant_heroes_and_positions.items():
                second_hero_id = str(item['hero_id'])
                if second_hero_id == hero_id:
                    continue
                duo_data = hero_data.get(second_hero_id, {}).get(pos2, {})
                if len(duo_data.get('value', {})) >= 2:
                    combo = tuple(sorted([hero_id, second_hero_id]))
                    if hero_data == time_data:
                        if combo not in radiant_time_unique_combinations:
                            radiant_time_unique_combinations.add(combo)
                            value = (sum(duo_data['value']) / len(duo_data['value'])) / 60
                            output_data['radiant_time_duo'].append(value)
                    elif hero_data == kills_data:
                        if combo not in radiant_kills_unique_combinations:
                            radiant_kills_unique_combinations.add(combo)
                            value = sum(duo_data['value']) / len(duo_data['value'])
                            output_data['radiant_kills_duo'].append(value)
                    # Третий герой
                    for pos3, item3 in radiant_heroes_and_positions.items():
                        third_hero_id = str(item3['hero_id'])
                        if third_hero_id not in [second_hero_id, hero_id]:
                            # Создаём отсортированный кортеж идентификаторов героев для уникальности
                            combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                            if hero_data == time_data:
                                if combo not in radiant_time_unique_combinations:
                                    radiant_time_unique_combinations.add(combo)
                                    trio_data = duo_data.get('total_time_trio', {}).get(third_hero_id, {}).get(pos3,
                                                                                                               {}).get(
                                        'value', {})
                                    if len(trio_data):
                                        value = (sum(trio_data) / len(trio_data)) / 60
                                        output_data['radiant_time_trio'].append(value)
                            elif hero_data == kills_data:
                                if combo not in radiant_kills_unique_combinations:
                                    radiant_kills_unique_combinations.add(combo)
                                    trio_data = duo_data.get('total_kills_trio', {}).get(third_hero_id, {}).get(pos3,
                                                                                                                {}).get(
                                        'value', {})
                                    if len(trio_data):
                                        value = sum(trio_data) / len(trio_data)
                                        output_data['radiant_kills_trio'].append(value)
        # dire_synergy
        hero_id = str(dire_heroes_and_positions['pos' + pos]['hero_id'])
        time_data = data.get(hero_id, {}).get('pos' + pos, {}).get('total_time_duo', {})
        kills_data = data.get(hero_id, {}).get('pos' + pos, {}).get('total_kills_duo', {})
        for hero_data in [time_data, kills_data]:
            for pos2, item in dire_heroes_and_positions.items():
                second_hero_id = str(item['hero_id'])
                if second_hero_id == hero_id:
                    continue
                duo_data = hero_data.get(second_hero_id, {}).get(pos2, {})
                if len(duo_data.get('value', {})) >= 2:
                    combo = tuple(sorted([hero_id, second_hero_id]))
                    if hero_data == time_data:
                        if combo not in dire_time_unique_combinations:
                            dire_time_unique_combinations.add(combo)
                            value = (sum(duo_data['value']) / len(duo_data['value'])) / 60
                            output_data['dire_time_duo'].append(value)
                    elif hero_data == kills_data:
                        if combo not in dire_kills_unique_combinations:
                            dire_kills_unique_combinations.add(combo)
                            value = sum(duo_data['value']) / len(duo_data['value'])
                            output_data['dire_kills_duo'].append(value)
                    # third_hero
                    for pos3, item3 in dire_heroes_and_positions.items():
                        third_hero_id = str(item3['hero_id'])
                        if third_hero_id not in [second_hero_id, hero_id]:
                            combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                            if hero_data == time_data:
                                if combo not in dire_time_unique_combinations:
                                    dire_time_unique_combinations.add(combo)
                                    trio_data = duo_data.get('total_time_trio', {}).get(third_hero_id, {}).get(pos3,
                                                                                                               {}).get(
                                        'value', {})
                                    if len(trio_data):
                                        value = (sum(trio_data) / len(trio_data)) / 60
                                        output_data['dire_time_trio'].append(value)
                            elif hero_data == kills_data:
                                if combo not in dire_kills_unique_combinations:
                                    dire_kills_unique_combinations.add(combo)
                                    trio_data = duo_data.get('total_kills_trio', {}).get(third_hero_id, {}).get(pos3,
                                                                                                                {}).get(
                                        'value', {})
                                    if len(trio_data):
                                        value = sum(trio_data) / len(trio_data)
                                        output_data['dire_kills_trio'].append(value)

    avg_time_trio = calculate_average(output_data['radiant_time_trio'] + output_data['dire_time_trio'])
    avg_kills_trio = calculate_average(output_data['radiant_kills_trio'] + output_data['dire_kills_trio'])
    avg_time_duo = calculate_average(output_data['radiant_time_duo'] + output_data['dire_time_duo'])
    avg_kills_duo = calculate_average(output_data['radiant_kills_duo'] + output_data['dire_kills_duo'])

    avg_kills = (avg_kills_trio + avg_kills_duo) / 2 if avg_kills_trio and avg_kills_duo else avg_kills_duo
    avg_time = (avg_time_duo + avg_time_trio) / 2 if avg_time_trio and avg_time_duo else avg_time_duo

    return round(avg_kills, 2), round(avg_time, 2)


def tm_kills_teams(radiant_heroes_and_pos, dire_heroes_and_pos, radiant_team_name, dire_team_name, min_len):
    # print('tm_kills')

    output_data = {'dire_kills_duo': [], 'dire_kills_trio': [], 'dire_time_duo': [], 'dire_time_trio': [],
                   'radiant_kills_duo': [], 'radiant_kills_trio': [], 'radiant_time_duo': [], 'radiant_time_trio': []}
    positions = ['1', '2', '3', '4', '5']
    radiant_time_unique_combinations, radiant_kills_unique_combinations, dire_kills_unique_combinations,\
        dire_time_unique_combinations = set(), set(), set(), set()
    with open('./all_teams/total_time_kills_dict_teams.txt', 'r') as f:
        data = json.load(f)['teams']
    if radiant_team_name in data and dire_team_name in data:
        work_data = data[radiant_team_name]
        for pos in positions:
            # radiant_synergy
            hero_id = str(radiant_heroes_and_pos['pos' + pos]['hero_id'])
            time_data = work_data.get(hero_id, {}).get('pos' + pos, {}).get('total_time_duo', {})
            kills_data = work_data.get(hero_id, {}).get('pos' + pos, {}).get('total_kills_duo', {})
            for hero_data in [time_data, kills_data]:
                for pos2, item in radiant_heroes_and_pos.items():
                    second_hero_id = str(item['hero_id'])
                    if second_hero_id == hero_id:
                        continue
                    duo_data = hero_data.get(second_hero_id, {}).get(pos2, {})
                    if len(duo_data.get('value', {})) >= min_len:
                        combo = tuple(sorted([hero_id, second_hero_id]))
                        if hero_data == time_data:
                            if combo not in radiant_time_unique_combinations:
                                radiant_time_unique_combinations.add(combo)
                                value = (sum(duo_data['value']) / len(duo_data['value'])) / 60
                                output_data['radiant_time_duo'].append(value)
                        elif hero_data == kills_data:
                            if combo not in radiant_kills_unique_combinations:
                                radiant_kills_unique_combinations.add(combo)
                                value = sum(duo_data['value']) / len(duo_data['value'])
                                output_data['radiant_kills_duo'].append(value)
                        # Третий герой
                        for pos3, item3 in radiant_heroes_and_pos.items():
                            third_hero_id = str(item3['hero_id'])
                            if third_hero_id not in [second_hero_id, hero_id]:
                                # Создаём отсортированный кортеж идентификаторов героев для уникальности
                                combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                if hero_data == time_data:
                                    if combo not in radiant_time_unique_combinations:
                                        radiant_time_unique_combinations.add(combo)
                                        trio_data = duo_data.get('total_time_trio', {}).get(third_hero_id, {}).\
                                            get(pos3, {}).get('value', {})
                                        if len(trio_data):
                                            value = (sum(trio_data) / len(trio_data)) / 60
                                            output_data['radiant_time_trio'].append(value)
                                elif hero_data == kills_data:
                                    if combo not in radiant_kills_unique_combinations:
                                        radiant_kills_unique_combinations.add(combo)
                                        trio_data = duo_data.get('total_kills_trio', {}).get(third_hero_id, {}).get(
                                            pos3, {}).get('value', {})
                                        if len(trio_data):
                                            value = sum(trio_data) / len(trio_data)
                                            output_data['radiant_kills_trio'].append(value)

        # dire_synergy
        dire_team_name.replace('g2.invictus gaming', 'g2 x ig')
        work_data = data[dire_team_name]
        for pos in positions:
            hero_id = str(dire_heroes_and_pos['pos' + pos]['hero_id'])
            time_data = work_data.get(hero_id, {}).get('pos' + pos, {}).get('total_time_duo', {})
            kills_data = work_data.get(hero_id, {}).get('pos' + pos, {}).get('total_kills_duo', {})
            for hero_data in [time_data, kills_data]:
                for pos2, item in dire_heroes_and_pos.items():
                    second_hero_id = str(item['hero_id'])
                    if second_hero_id != hero_id:
                        duo_data = hero_data.get(second_hero_id, {}).get(pos2, {})
                        if len(duo_data.get('value', {})) >= min_len:
                            combo = tuple(sorted([hero_id, second_hero_id]))
                            if hero_data == time_data:
                                if combo not in dire_time_unique_combinations:
                                    dire_time_unique_combinations.add(combo)
                                    value = (sum(duo_data['value']) / len(duo_data['value'])) / 60
                                    output_data['dire_time_duo'].append(value)
                            elif hero_data == kills_data:
                                if combo not in dire_kills_unique_combinations:
                                    dire_kills_unique_combinations.add(combo)
                                    value = sum(duo_data['value']) / len(duo_data['value'])
                                    output_data['dire_kills_duo'].append(value)
                            # third_hero
                            for pos3, item3 in dire_heroes_and_pos.items():
                                third_hero_id = str(item3['hero_id'])
                                if third_hero_id not in [second_hero_id, hero_id]:
                                    combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                    if hero_data == time_data:
                                        if combo not in dire_time_unique_combinations:
                                            dire_time_unique_combinations.add(combo)
                                            trio_data = duo_data.get('total_time_trio', {}).get(third_hero_id, {}).get(
                                                pos3, {}).get('value', {})
                                            if len(trio_data):
                                                value = (sum(trio_data) / len(trio_data)) / 60
                                                output_data['dire_time_trio'].append(value)
                                    elif hero_data == kills_data:
                                        if combo not in dire_kills_unique_combinations:
                                            dire_kills_unique_combinations.add(combo)
                                            trio_data = duo_data.get('total_kills_trio', {}).get(third_hero_id, {}).get(
                                                pos3, {}).get('value', {})
                                            if len(trio_data):
                                                value = sum(trio_data) / len(trio_data)
                                                output_data['dire_kills_trio'].append(value)

        avg_time_trio = calculate_average(output_data['radiant_time_trio'] + output_data['dire_time_trio'])
        avg_kills_trio = calculate_average(output_data['radiant_kills_trio'] + output_data['dire_kills_trio'])
        avg_time_duo = calculate_average(output_data['radiant_time_duo'] + output_data['dire_time_duo'])
        avg_kills_duo = calculate_average(output_data['radiant_kills_duo'] + output_data['dire_kills_duo'])

        avg_kills = (avg_kills_trio + avg_kills_duo) / 2 if avg_kills_trio and avg_kills_duo else avg_kills_duo
        avg_time = (avg_time_duo + avg_time_trio) / 2 if avg_time_trio and avg_time_duo else avg_time_duo
        if (len(output_data['dire_kills_duo']) > 0 and len(output_data['radiant_kills_duo']) > 0)\
                or len(output_data['dire_kills_duo'] + output_data['radiant_kills_duo']) > 3:
            return round(avg_kills, 2), round(avg_time, 2)
        else:
            raise TypeError
    else:
        if radiant_team_name not in data:
            print(f'{radiant_team_name} not in team list')
        if dire_team_name not in data:
            print(f'{dire_team_name} not in team list')
