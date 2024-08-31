import os
import shutil
import time
from id_to_name import pro_teams, pro_players, all_teams_ids
from keys import api_token, api_token_2
import datetime
import html
import json
import re

import requests
from bs4 import BeautifulSoup

import id_to_name
import keys


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


# Структура приложения: Анализ пиков + анализ игроков + анализ команды
# можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
# сверха прошлых матчей и прошлых встреч
# Отладка винрейта на старых матчах
# Проверка того что все правильно работает
# ранги неправильно работают



def get_urls(url, target_datetime=0):
    headers = {
        'Host': 'dltv.org',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cookie': '__locales_redirect=1; XSRF-TOKEN=CrRD7ES3D0bOZ9rCcCDqXjRDETjzT7rytDBsmfbF; dltv_session=VIa6gs6CP1ciQ98qtbhaVoX6uOMgNjxgb05zpcQy; cookie__accept=true; ___user_timezone=Europe%2FMoscow; ___user_results=all; ___user_theme=light; ___user_scoreboard=1; ___user_date_filter=0; comments-language=ru; cf_clearance=uBbl2syqVW4y5hDhHZFFkMIfWp9NMXI_UWukOGWnO.Q-1713899154-1.0.1.1-LnK08BCCVLFjL04pwXmh2HdwezwQVazx5TctcyX9NAr9pkhAkl3jWEWGt.UPz48tG5WT4BU_TrBkchn6Vl3tOA; banners_stats_1=3_1; banners_stats_6=107_1; banners_stats_2=112_1; banners_stats_4=92_1; banners_stats_3=99_1; banners_stats_0=79_1%3B94_1; banners_stats_5=113_1',
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
        heroes = []
        for hero_block in picks_item:
            for hero in list(id_to_name.translate.values()):
                if f'({hero})' in hero_block.text:
                    heroes.append(hero)
        radiant_heroes_and_pos = {}
        dire_heroes_and_pos = {}
        for i in range(5):
            for id in id_to_name.translate:
                try:
                    if id_to_name.translate[id] == heroes[i]:
                        hero_id = id
                        radiant_heroes_and_pos[f'pos{i + 1}'] = {'hero_id': hero_id, 'hero_name': heroes[i]}
                except:
                    pass
        c = 0
        for i in range(5, 10):
            for id in id_to_name.translate:
                if id_to_name.translate[id] == heroes[i]:
                    hero_id = id
                    dire_heroes_and_pos[f'pos{c + 1}'] = {'hero_id': hero_id, 'hero_name': heroes[i]}
                    c += 1

        return radiant_heroes_and_pos, dire_heroes_and_pos
    else:
        print('нету live матчей')


def analyze_draft(sinergy, counterpick, pos1_vs_team, core_matchup, pos2_vs_team, pos3_vs_team,
                  sups, over45):
    radiant_predict, dire_predict = False, False
    values = {'sinergy': sinergy, 'counterpick': counterpick, 'pos 1_vs_team': pos1_vs_team,
              'pos 2_vs_team': pos2_vs_team, 'pos 3_vs_team': pos3_vs_team, 'sups': sups, 'over45': over45}
    other_values = {'sinergy': sinergy, 'counterpick': counterpick, 'sups': sups, 'over45': over45}
    values_nones = sum(1 for value in values.values() if value is None)
    other_values_nones = sum(1 for value in other_values.values() if value is None)
    nones = (values_nones <= 2) * (other_values_nones <= 1)
    if nones:
        # values, other_values = [value for value in values if value is not None], [value for value in other_values if value is not None]
        all_positive_or_negative = all(value >= 0 for value in values.values() if value is not None) + all(
            value <= 0 for value in values.values() if value is not None)
        other_values_check = all(value >= 0 for value in other_values.values() if value is not None) + all(
            value <= 0 for value in other_values.values() if value is not None)
        singery_or_counterpick = all(
            value >= 0 for value in [counterpick, sinergy, values['over45']] if value is not None) + all(
            value <= 0 for value in [counterpick, sinergy] if value is not None)
        both_over9 = all(value <= -9 for value in [counterpick, sinergy] if value is not None) + all(
            value >= 9 for value in [counterpick, sinergy] if value is not None)
        both_over5 = all(value <= -5 for value in [counterpick, sinergy] if value is not None) + all(
            value >= 5 for value in [counterpick, sinergy] if value is not None)
        any_over20 = (all(value > 0 for value in [counterpick, sinergy] if value is not None) * any(
            value >= 20 for value in [counterpick, sinergy] if value is not None)) + (
                                 all(value < 0 for value in [counterpick, sinergy] if value is not None) * any(
                             value <= -20 for value in [counterpick, sinergy] if value is not None))
        any_over8 = (all(value > 0 for value in [counterpick, sinergy] if value is not None) * any(
            value >= 8 for value in [counterpick, sinergy] if value is not None)) + (
                            all(value < 0 for value in [counterpick, sinergy] if value is not None) * any(
                        value <= -8 for value in [counterpick, sinergy] if value is not None))
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
        elif (
                singery_or_counterpick and both_over5) or all_positive_or_negative or other_values_check or counterpick_over8:
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


def fill_players_position(rows, players):
    heroes_and_position = {}
    lst = ['Мидер', 'Сапорт 4', 'Керри', 'Сапорт 5', 'Оффлейнер']
    translate = {'Мидер': 'pos 2', 'Сапорт 4': 'pos 4', 'Керри': 'pos 1', 'Сапорт 5': 'pos 5', 'Оффлейнер': 'pos 3'}
    for row in rows:
        # Находим ячейку с никнеймом игрока
        player_nick = row.find('span', class_='team-player-nick')
        if player_nick is not None:
            player_nick = player_nick.text.strip().lower()
            player_nick = re.sub(r'[^\w\s\u4e00-\u9fff]+', '', player_nick)

            # Находим ячейку с позицией игрока
            player_position = row.find('td').find_next_sibling('td').text.strip()
            if player_position != '':
                for player_name in players:
                    if are_similar(player_name, player_nick, threshold=50):
                        if player_position == 'Сапорт 5':
                            players[player_name]['pos ition'] = player_position
                            lst.remove(player_position)
                            break
                        else:
                            players[player_name]['pos ition'] = player_position
                            lst.remove(player_position)
    if len(lst) == 1:
        for player in players:
            if len(players[player]) == 1:
                players[player]['pos ition'] = lst[0]

    for player in players:
        if 'pos ition' in players[player]:
            heroes_and_position[translate[players[player]['pos ition']]] = players[player]['hero']
        else:
            print('Не удалось узнать позицию, скорее всего команда новая')
            return None
    return heroes_and_position


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
    if match['team_dire'] is not None and match['team_radiant'] is not None and 'Kobold' not in match['tournament'][
        'name']:
        radiant_team_name = match['team_radiant']['name'].lower()
        dire_team_name = match['team_dire']['name'].lower()
        score = match['best_of_score']
        dic = {
            'fissure': 1,
            'riyadh': 1,
            'international': 1,
            'pgl': 1,
            'bb': 1,
            'epl':2,
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


def clean_up(inp, lenght=0):
    if len(inp) > lenght:
        copy = inp.copy()
        for i in inp:
            if i >= 47 and i <= 53:
                copy.remove(i)
        if len(copy) < 3:
            return inp
        else:
            return copy
    else:
        return []


def str_to_json(input_data):
    text = input_data.replace(':', '":').replace('#', '').replace('{', '{"')
    data = re.sub(r",(?=[a-zA-Z])", ',"', text)
    data = re.sub(r'\.(\d{2})(\d{2})', r'\1.\2', data, flags=re.MULTILINE)
    data = re.sub(r'\.(\d{2})(\d{1})', r'\1.\2', data, flags=re.MULTILINE)
    data = re.sub(r':0(?=[0-9])', ':', data)
    data = re.sub(r'[\x00-\x1F]+', '', data)

    def multiply_by_10(match):
        number = int(match.group(1))
        output = ':' + str(number * 10) + ','
        return output

    data = re.sub(r':\.(\d{1}),', multiply_by_10, data).replace(':.', ':')
    data = re.sub(r':(0)([0-9])', r':\2', data, flags=re.MULTILINE)
    return data


def send_message(message):
    bot_token = f'{keys.Token}'
    chat_id = f'{keys.Chat_id}'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, json=payload)


def dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, output_message='', sinergy=None, counterpick = None):
    radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team, dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
    radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, dire_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [], [], [], [], [], [], [], None, None
    for position in radiant_heroes_and_positions:
        if position != 'pos5':
            hero_url = radiant_heroes_and_positions[position]['hero_name'].replace(' ', '%20')
            url = f'https://dota2protracker.com/hero/{hero_url}'
            response = requests.get(url)
            if response.status_code != 200:
                print(f'Ошибка dota2protracekr\n{url}')
            soup = BeautifulSoup(response.text, 'lxml')
            stats = soup.find_all('script')
            matchups = re.search(r'matchups:(\[.*?\])', stats[5].text, re.DOTALL)
            synergies = re.search(r'synergies:(\[.*?\])', stats[5].text, re.DOTALL)
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
                print(f'Ошибка dota2protracekr\n{url}')
            soup = BeautifulSoup(response.text, 'lxml')
            stats = soup.find_all('script')
            matchups = re.search(r'matchups:(\[.*?\])', stats[5].text, re.DOTALL)
            synergies = re.search(r'synergies:(\[.*?\])', stats[5].text, re.DOTALL)
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
            print(f'Ошибка dota2protracekr\n{url}')
        soup = BeautifulSoup(response.text, 'lxml')
        stats = soup.find_all('script')
        matchups = re.search(r'matchups:(\[.*?\])', stats[5].text, re.DOTALL)
        synergies = re.search(r'synergies:(\[.*?\])', stats[5].text, re.DOTALL)
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
                    if data_pos == 'pos1':
                        core_matchup = data_wr
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
    dire_wr_with = clean_up(dire_wr_with, 4)
    radiant_wr_with = clean_up(radiant_wr_with, 4)
    radiant_wr_against = clean_up(radiant_wr_against, 5)

    if len(radiant_wr_with) > 0 and len(dire_wr_with) > 0:
        sinergy = round((sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with)), 2)
    if len(radiant_wr_against) > 0:
        counterpick = round((sum(radiant_wr_against) / len(radiant_wr_against)) - (
                sum(dire_wr_against) / len(dire_wr_against)), 2)

    return f'\nDota2protracker:\nSynergy: {sinergy}\nCounterpick: {counterpick}\n'



def load_json_file(filepath, default_value):
    try:
        with open(f'{filepath}.txt', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value


def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)



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


def get_pro_players_ids(last_date = 0, counter = 0):
    bottle,pro_ids = set(), set()
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
            headers = {"Authorization": f"Bearer {api_token}"}
            response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
            teams = json.loads(response.text)['data']['teams']
            try:
                for team in teams:
                    last_date = 0
                    for member in team['members']:
                        if last_date < member['lastMatchDateTime']:
                            last_date = member['lastMatchDateTime']
                    for member in team['members']:
                        if member['lastMatchDateTime'] == last_date:
                            pro_ids.add(member['steamAccount']['id'])
            except:
                pass
            bottle = set()
    return pro_ids


def proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count, team_ids, pro_query=None, check=True, skip=0):
    try:
        while check:
            if pro_query is None:
                query = '''
                                    {players(steamAccountIds:%s){
                                      steamAccountId
                                      matches(request:{startDateTime:%s, take:100, skip:%s, gameModeIds:%s}){
                                        id
                                      }
                                    }
                                    }
                                    ''' % (ids_to_graph, start_date_time, skip, game_mods)
            else:
                query = pro_query
            headers = {"Authorization": f"Bearer {api_token_2}"}
            response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
            if response.status_code == 200:
                data = json.loads(response.text)
                if pro_query is None:
                    if any(player['matches'] != [] for player in data['data']['players']):
                        for player in data['data']['players']:
                            for map_id in player['matches']:
                                if map_id['id'] not in file_data:
                                    file_data.append(map_id['id'])
                        skip += 100
                    else:
                        ids_to_graph = []
                        check = False
                else:
                    check = False
                    for team in data['data']['teams']:
                        for match in team['matches']:
                            if match['id'] not in file_data:
                                radiant_team_name = match['radiantTeam']['name'].lower()
                                dire_team_name = match['direTeam']['name'].lower()
                                if match['radiantTeam']['id'] in team_ids or match['direTeam']['id'] in team_ids:
                                    file_data.append(match['id'])
            else:
                print('ошибка с api, мож ключ limit словил')
    except Exception as e:
        print(f"Error {e}")
        time.sleep(5)
    count += 1
    return file_data


def get_maps(game_mods, start_date_time, maps_to_save, players_dict=None, show_prints=None, team_ids=None, team_names=None):
    ids_to_graph, total_map_ids, file_data, count ,unique = [], [], [], 0, set()
    if game_mods == [2]:
        if team_ids is not None:
            some_data = team_ids
        else:
            some_data = pro_teams
        for team_name in some_data:
            count += 1
            if show_prints:
                print(f'{count}/{len(some_data)}')
            if type(some_data) == dict:
                steam_id = some_data[team_name]['id']
            else:
                steam_id = team_name
            if len(ids_to_graph) != 5 and count != len(some_data):
                if steam_id not in unique:
                    ids_to_graph.append(steam_id)
                unique.add(steam_id)


            elif len(ids_to_graph) == 5 or count == len(some_data):
                if count == len(some_data):
                    ids_to_graph.append(steam_id)
                pro_query = '''
                            {teams(teamIds: %s){
                              matches(request:{startDateTime:%s, take:100, skip: 0}){
                                id
                                radiantTeam{
                                          name
                                          id
                                        }
                                        direTeam{
                                          name
                                          id
                                        }
                              }
                            }}''' % (ids_to_graph, start_date_time)
                file_data = proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count, team_ids, pro_query)
                ids_to_graph = [steam_id]

    else:
        # if type(players_dict) == dict:
        #     players_dict = set(list(players_dict) + pro_players)
        # else:
        #     players_dict = set(players_dict + pro_players)
        for steam_id in players_dict:
            count += 1
            if show_prints:
                print(f'{count}/{len(players_dict)}')
            if len(ids_to_graph) != 5:
                ids_to_graph.append(steam_id)
                if count == len(players_dict):
                    proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count, team_ids)
            else:
                proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count, team_ids)
                ids_to_graph = [steam_id]
    with open(f'{maps_to_save}.txt', 'w') as f:
        f.truncate()
        f.seek(0)
        json.dump(file_data, f)
    return True

def eat_temp_files(mkdir, file_data, output):
    folder_path = f"./{mkdir}/temp_files"
    if os.path.exists(folder_path):
        try:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r+') as f:
                    data = json.load(f)
                    for map in data:
                        if map not in file_data:
                            file_data[map] = data[map]
        except:
            pass
        with open(f'./{mkdir}/{output}.txt', 'w') as f:
            f.truncate()
            f.seek(0)
            json.dump(file_data, f)
        shutil.rmtree(f'./{mkdir}/temp_files')


def research_map_proceed(maps_to_explore, file_data, output, mkdir, counter=0, another_counter=0, error_counter=0, show_prints=None):
    token = api_token_2
    eat_temp_files(mkdir, file_data, output)
    for map_id in maps_to_explore:
        # if map_id == 7913508802:
        #     pass
        counter += 1
        if show_prints:
            print(f'{counter}/{len(maps_to_explore)}')
        if error_counter >= 1:
            if token != api_token_2:
                token = api_token_2
            else:
                token = api_token
            error_counter = 0
        if str(map_id) not in file_data:
            another_counter += 1
            if another_counter % 300 == 0:
                if not os.path.isdir(f"./{mkdir}/temp_files"):
                    os.mkdir(f"./{mkdir}/temp_files")
                another_counter += 1
                path = f'./{mkdir}/temp_files/{another_counter}.txt'
                if os.path.isfile(path):
                    while os.path.isfile(path):
                        another_counter += 1
                with open(path, 'w') as f:
                    f.truncate()
                    f.seek(0)
                    json.dump(file_data, f)
            try:
                query = '''
                {match(id:%s){
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
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
                data = json.loads(response.text)['data']['match']
                if data['direKills'] is not None:
                    file_data[map_id] = data
            except Exception as e:
                error_counter += 1
                if show_prints:
                    print(f"Error processing map ID {map_id}: {e}")
    eat_temp_files(mkdir, file_data, output)
    if another_counter > 0:
        with open(f'./{mkdir}/{output}.txt', 'r+') as f:
            f.truncate()
            f.seek(0)
            json.dump(file_data, f)


def research_maps(maps_to_explore, output, mkdir, show_prints=None):
    path = f'./{mkdir}/{maps_to_explore}.txt'
    with open(path, 'r+') as f:
        maps_to_explore = set(json.load(f))
    try:
        with open(f'./{mkdir}/{output}.txt', 'r+') as f:
            file_data = json.load(f)
    except:
        with open(f'./{mkdir}/{output}.txt', 'w') as f:
            file_data = {}

    research_map_proceed(maps_to_explore=maps_to_explore, file_data=file_data, output=output,
                         mkdir=mkdir, show_prints=show_prints)
    # except (FileExistsError, FileNotFoundError):
    # with open(f'./{mkdir}/{output}.txt', 'w') as f:
    #     file_data = {}


def proceed_map(match, map_id, players_imp_data, used_maps, lane_dict, synergy_and_counterpick_dict,
                total_time_kills_dict, over45_dict, over35_dict, radiant_team_name=None, dire_team_name=None):
    for player in match['players']:
        radiant_win = match['didRadiantWin']
        position = player['position'].replace('POSITION_', 'pos')
        hero_id = str(player['hero']['id'])
        isradiant = player['isRadiant']
        steam_id = str(player['steamAccount']['id'])
        if map_id not in players_imp_data['used_maps']:
            if (player['steamAccount']['isAnonymous']):
                players_imp_data.setdefault('value', {}).setdefault(steam_id, {}).setdefault(hero_id, {}).setdefault(
                    position, []).append(
                    player['imp'])
                players_imp_data.setdefault('used_maps', []).append(map_id)
        if isradiant:
            if radiant_win:
                to_be_appended = 1
            else:
                to_be_appended = 0
        else:
            if radiant_win:
                to_be_appended = 0
            else:
                to_be_appended = 1
        synergy_and_counterpick_dict.setdefault('value', {}).setdefault(hero_id, {}).setdefault(position,
                                                                                                {}).setdefault(
            'winrate', []).append(to_be_appended)
        # time, kills, and other shit

        if player['isRadiant'] is True:
            outcome = match[radiant_position_to_lane[position]]
            if 'RADIANT' in outcome:
                to_be_appended = 1
            elif 'DIRE' in outcome:
                to_be_appended = 0
            else:
                # ничья
                to_be_appended = 2
        else:
            outcome = match[dire_position_to_lane[position]]
            if 'RADIANT' in outcome:
                to_be_appended = 0
            elif 'DIRE' in outcome:
                to_be_appended = 1
            else:
                # ничья
                to_be_appended = 2
        lane_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                           ['lane_report', 'solo', 'value'],
                                           lane_dict)

        for another_player in match['players']:
            another_player_hero_id = str(another_player['hero']['id'])
            if another_player_hero_id != hero_id:
                another_player_position = another_player['position'].replace('POSITION_', 'pos')
                another_isradiant = another_player['isRadiant']
                # lane
                if player['isRadiant'] is True:
                    if 'RADIANT' in outcome:
                        to_be_appended = 1
                    elif 'DIRE' in outcome:
                        to_be_appended = 0
                    else:
                        to_be_appended = 2
                else:
                    if 'RADIANT' in outcome:
                        to_be_appended = 0
                    elif 'DIRE' in outcome:
                        to_be_appended = 1
                    else:
                        to_be_appended = 2
                if ((position in ['pos5', 'pos1']) and (another_player_position in ['pos1', 'pos5']) or (
                        position in ['pos3', 'pos4']) and (
                            another_player_position in ['pos3', 'pos4'])) and (isradiant == another_isradiant) and (
                        position != another_player_position):
                    lane_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                       ['lane_report', 'with_hero', another_player_hero_id,
                                                        another_player_position], lane_dict)

                elif (position == 'pos2') and (another_player_position == 'pos2') and (
                        hero_id != another_player_hero_id):
                    lane_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                       ['lane_report', 'against_hero', another_player_hero_id],
                                                       lane_dict)
                # counterpick
                if isradiant:
                    if radiant_win:
                        to_be_appended = 1
                    else:
                        to_be_appended = 0
                else:
                    if radiant_win:
                        to_be_appended = 0
                    else:
                        to_be_appended = 1
                if isradiant != another_player['isRadiant']:
                    synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                          ['counterpick_duo',
                                                                           another_player_hero_id,
                                                                           another_player_position, 'value'],
                                                                          synergy_and_counterpick_dict)
                # synergy
                if (isradiant == another_player['isRadiant']) and (hero_id != another_player_hero_id):
                    synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position,
                                                                          to_be_appended,
                                                                          ['synergy_duo',
                                                                           another_player_hero_id,
                                                                           another_player_position,
                                                                           'value'],
                                                                          synergy_and_counterpick_dict)

                    total_kills = sum(match['direKills']) + sum(match['radiantKills'])
                    if match['durationSeconds'] / 60 >= 35:
                        over35_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                               ['over35_duo', another_player_hero_id,
                                                another_player_position, 'value'], over35_dict)
                    if match['durationSeconds'] / 60 >= 45:
                        over45_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                             ['over45_duo', another_player_hero_id,
                                                              another_player_position, 'value'], over45_dict)
                    if isradiant:
                        total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                       ['total_kills_duo', another_player_hero_id,
                                                                        another_player_position, 'value'],
                                                                       total_time_kills_dict,
                                                                       team_name=radiant_team_name)
                        total_time_kills_dict = distribute_heroes_data(hero_id, position, match['durationSeconds'],
                                                                       ['total_time_duo', another_player_hero_id,
                                                                        another_player_position, 'value'],
                                                                       total_time_kills_dict,
                                                                       team_name=radiant_team_name)
                    else:
                        total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                       ['total_kills_duo', another_player_hero_id,
                                                                        another_player_position, 'value'],
                                                                       total_time_kills_dict,
                                                                       team_name=dire_team_name)
                        total_time_kills_dict = distribute_heroes_data(hero_id, position, match['durationSeconds'],
                                                                       ['total_time_duo', another_player_hero_id,
                                                                        another_player_position, 'value'],
                                                                       total_time_kills_dict,
                                                                       team_name=dire_team_name)
                    total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                   ['total_kills_duo', another_player_hero_id,
                                                                    another_player_position, 'value'],
                                                                   total_time_kills_dict)

                    total_time_kills_dict = distribute_heroes_data(hero_id, position, match['durationSeconds'],
                                                                   ['total_time_duo', another_player_hero_id,
                                                                    another_player_position, 'value'],
                                                                   total_time_kills_dict)

                    for third_player in match['players']:
                        third_player_hero_id = str(third_player['hero']['id'])
                        third_player_position = third_player['position'].replace('POSITION_', 'pos')
                        third_isradiant = third_player['isRadiant']
                        if (isradiant == third_isradiant and third_isradiant == another_isradiant) and (
                                third_player_hero_id not in [hero_id, another_player_hero_id]):
                            if match['durationSeconds'] / 60 > 45:
                                over45_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                     ['over45_duo', another_player_hero_id,
                                                                      another_player_position, 'over45_trio',
                                                                      third_player_hero_id, third_player_position,
                                                                      'value'], over45_dict)
                            if match['durationSeconds'] / 60 > 35:
                                over35_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                     ['over35_duo', another_player_hero_id,
                                                                      another_player_position, 'over35_trio',
                                                                      third_player_hero_id, third_player_position,
                                                                      'value'], over35_dict)
                            synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position,
                                                                                  to_be_appended,
                                                                                  ['synergy_duo',
                                                                                   another_player_hero_id,
                                                                                   another_player_position,
                                                                                   'synergy_trio',
                                                                                   third_player_hero_id,
                                                                                   third_player_position, 'value'],
                                                                                  synergy_and_counterpick_dict)
                            if isradiant:
                                total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                               ['total_kills_duo',
                                                                                another_player_hero_id,
                                                                                another_player_position,
                                                                                'total_kills_trio',
                                                                                third_player_hero_id,
                                                                                third_player_position,
                                                                                'value'], total_time_kills_dict,
                                                                               team_name=radiant_team_name)
                                total_time_kills_dict = distribute_heroes_data(hero_id, position,
                                                                               match['durationSeconds'],
                                                                               ['total_time_duo',
                                                                                another_player_hero_id,
                                                                                another_player_position,
                                                                                'total_time_trio',
                                                                                third_player_hero_id,
                                                                                third_player_position,
                                                                                'value'], total_time_kills_dict,
                                                                               team_name=radiant_team_name)
                            else:
                                total_time_kills_dict = distribute_heroes_data(hero_id, position,
                                                                               total_kills,
                                                                               [
                                                                                   'total_kills_duo',
                                                                                   another_player_hero_id,
                                                                                   another_player_position,
                                                                                   'total_kills_trio',
                                                                                   third_player_hero_id,
                                                                                   third_player_position,
                                                                                   'value'],
                                                                               total_time_kills_dict,
                                                                               team_name=dire_team_name)
                                total_time_kills_dict = distribute_heroes_data(hero_id, position,
                                                                               match[
                                                                                   'durationSeconds'],
                                                                               ['total_time_duo',
                                                                                another_player_hero_id,
                                                                                another_player_position,
                                                                                'total_time_trio',
                                                                                third_player_hero_id,
                                                                                third_player_position,
                                                                                'value'],
                                                                               total_time_kills_dict,
                                                                               team_name=dire_team_name)
                            total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                           ['total_kills_duo',
                                                                            another_player_hero_id,
                                                                            another_player_position,
                                                                            'total_kills_trio',
                                                                            third_player_hero_id,
                                                                            third_player_position,
                                                                            'value'], total_time_kills_dict)

                            total_time_kills_dict = distribute_heroes_data(hero_id, position,
                                                                           match['durationSeconds'],
                                                                           ['total_time_duo',
                                                                            another_player_hero_id,
                                                                            another_player_position,
                                                                            'total_time_trio',
                                                                            third_player_hero_id,
                                                                            third_player_position,
                                                                            'value'], total_time_kills_dict)
                        elif third_isradiant != isradiant and third_isradiant != another_isradiant:
                            path = ['synergy_duo',another_player_hero_id, another_player_position,
                                    '2vs1', third_player_hero_id, third_player_position, 'value']
                            if isradiant:
                                to_be_appended = 1
                            else:
                                to_be_appended = 0
                            synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position,
                                                                                  to_be_appended,
                                                                                  path,
                                                                                  synergy_and_counterpick_dict)
    return lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, over45_dict


def analyze_database(database, start_date_time, players_imp_data, over35_dict, used_maps=None, total_time_kills_dict=None, pro=False,
                     over45_dict=None, synergy_and_counterpick_dict=None, lane_dict=None, count=0, show_prints=None, counter = 0, team_ids = None):
    total, team_stat_dict = len(database), {}
    new_maps = [str(map_id) for map_id in database if str(map_id) not in used_maps]
    for map_id in new_maps:
        count += 1
        if show_prints:
            print(f'{count}/{total}')
        match = database[map_id]
        if match['direKills'] != None and ('startDateTime' in match) and (match['startDateTime'] >= start_date_time):
            counter += 1
            if all(name in match and match[name] is not None for name in ['direTeam', 'radiantTeam']):
                dire_team_name = match['direTeam']['name'].lower()
                radiant_team_name = match['radiantTeam']['name'].lower()
                trnslt = {
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
                }
                if radiant_team_name in trnslt:
                    radiant_team_name = trnslt[radiant_team_name]
                if dire_team_name in trnslt:
                    dire_team_name = trnslt[dire_team_name]
                if pro:
                    result = proceed_map(match=match, map_id=map_id, players_imp_data=players_imp_data,
                                         used_maps=used_maps, lane_dict=lane_dict,
                                         synergy_and_counterpick_dict=synergy_and_counterpick_dict,
                                         total_time_kills_dict=total_time_kills_dict, over45_dict=over45_dict,
                                         radiant_team_name=radiant_team_name, dire_team_name=dire_team_name, over35_dict=over35_dict)
                    lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, over45_dict = result
                    for team_name in [radiant_team_name, dire_team_name]:
                        team_stat_dict.setdefault(team_name, {}).setdefault('kills', []).append(
                            sum(match['direKills']) + sum(match['radiantKills']))
                        team_stat_dict.setdefault(team_name, {}).setdefault('time', []).append(
                            match['durationSeconds'] / 60)
                        if match['radiantTeam']['name'].lower() == team_name:
                            team_stat_dict.setdefault(team_name, {}).setdefault('id', match['radiantTeam']['id'])
                        else:
                            team_stat_dict.setdefault(team_name, {}).setdefault('id', match['direTeam']['id'])

            else:
                if (match['durationSeconds'] / 60) >= 21:
                    result = proceed_map(match=match, map_id=map_id, players_imp_data=players_imp_data,
                                         used_maps=used_maps, lane_dict=lane_dict,
                                         synergy_and_counterpick_dict=synergy_and_counterpick_dict,
                                         total_time_kills_dict=total_time_kills_dict, over45_dict=over45_dict,
                                         over35_dict=over35_dict)
                    lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, over45_dict = result
            used_maps.append(map_id)
    if counter > 0:
        return players_imp_data, total_time_kills_dict, over45_dict, over35_dict, synergy_and_counterpick_dict, lane_dict, team_stat_dict, used_maps



def explore_database(mkdir, output, start_date_time, pro=False, show_prints=None, team_ids = None):
    database = load_json_file(f'./{mkdir}/{output}', {})
    players_imp_data = load_json_file(f'./egb/players_imp_data', {})
    total_time_kills_dict = load_json_file(f'./{mkdir}/total_time_kills_dict', {})
    over45_dict = load_json_file(f'./{mkdir}/over45_dict', {})
    synergy_and_counterpick_dict = load_json_file(f'./{mkdir}/synergy_and_counterpick_dict', {})
    lane_dict = load_json_file(f'./{mkdir}/lane_dict', {})
    over35_dict = load_json_file(f'./{mkdir}/over35_dict', {})
    used_maps = load_json_file(f'./{mkdir}/used_maps', [])
    result = analyze_database(database=database, start_date_time=start_date_time,
                              players_imp_data=players_imp_data, total_time_kills_dict=total_time_kills_dict,
                              over45_dict=over45_dict, synergy_and_counterpick_dict=synergy_and_counterpick_dict,
                              lane_dict=lane_dict, pro=pro, used_maps=used_maps, over35_dict=over35_dict, show_prints=show_prints, team_ids=team_ids)
    if result is not None:
        players_imp_data, total_time_kills_dict, over45_dict, over35_dict, synergy_and_counterpick_dict, lane_dict, team_stats_dict, used_maps = result
        save_json_file(f'./{mkdir}/synergy_and_counterpick_dict.txt', synergy_and_counterpick_dict)
        save_json_file(f'./{mkdir}/over45_dict.txt', over45_dict)
        save_json_file(f'./{mkdir}/total_time_kills_dict.txt', total_time_kills_dict)
        save_json_file(f'./egb/players_imp_data.txt', players_imp_data)
        save_json_file(f'./{mkdir}/lane_dict.txt', lane_dict)
        save_json_file(f'./{mkdir}/over35_dict.txt', over35_dict)
        save_json_file(f'./{mkdir}/used_maps.txt', used_maps)
        save_json_file(f'./{mkdir}/team_stats_dict.txt', team_stats_dict)




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
    new_values = [value for value in values if value < 0.44 or value > 0.56]
    return sum(new_values) / len(new_values) if new_values else None


def synergy_team(heroes_and_pos, enemy_heroes_and_pos, output, mkdir, data):
    unique_combinations = set()
    for pos in heroes_and_pos:
        try:
            hero_id = str(heroes_and_pos[pos]['hero_id'])
            hero_data = data[hero_id][pos]['synergy_duo']
            for second_pos in heroes_and_pos:
                if pos != second_pos:
                    second_hero_id = str(heroes_and_pos[second_pos]['hero_id'])
                    duo_data = hero_data[second_hero_id][second_pos]
                    if len(duo_data['value']) >= 15:
                        combo = tuple(sorted([hero_id, second_hero_id]))
                        if combo not in unique_combinations and len(duo_data['value']) > 6:
                            unique_combinations.add(combo)
                            value = duo_data['value'].count(1) / (
                                    duo_data['value'].count(1) + duo_data['value'].count(0))
                            output[f'{mkdir}_duo'].append(value)
                        for third_pos in heroes_and_pos:
                            if third_pos not in [pos, second_pos]:
                                third_hero_id = str(heroes_and_pos[third_pos]['hero_id'])
                                trio_data = duo_data['synergy_trio'][third_hero_id][third_pos]
                                if len(trio_data['value']) > 9:
                                    combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                    if combo not in unique_combinations:
                                        unique_combinations.add(combo)
                                        value = trio_data['value'].count(1) / (
                                                trio_data['value'].count(1) + trio_data['value'].count(0))
                                        output[f'{mkdir}_trio'].append(value)
                        for enemy_third_pos in enemy_heroes_and_pos:
                            third_hero_id = str(enemy_heroes_and_pos[enemy_third_pos]['hero_id'])
                            trio_data = duo_data['2vs1'][third_hero_id][enemy_third_pos]
                            if len(trio_data['value']) > 9:
                                combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                if combo not in unique_combinations:
                                    unique_combinations.add(combo)
                                    value = trio_data['value'].count(1) / (
                                            trio_data['value'].count(1) + trio_data['value'].count(0))
                                    output[f'{mkdir}_2vs1'].append(value)

        except KeyError:
            pass
    return output


def counterpick_team(heroes_and_pos, heroes_and_pos_opposite, output, mkdir, data):
    unique_combinations = set()
    for pos in heroes_and_pos:
        try:
            hero_id = str(heroes_and_pos[pos]['hero_id'])
            hero_data = data[hero_id][pos]['counterpick_duo']
            for second_pos in heroes_and_pos_opposite:
                second_hero_id = str(heroes_and_pos_opposite[second_pos]['hero_id'])
                duo_data = hero_data[second_hero_id][second_pos]
                if len(duo_data['value']) >= 15:
                    combo = tuple(sorted([hero_id, second_hero_id]))
                    if combo not in unique_combinations:
                        unique_combinations.add(combo)
                        value = duo_data['value'].count(1) / (
                                duo_data['value'].count(1) + duo_data['value'].count(0))
                        output[f'{mkdir}_duo'].append(value)
        except KeyError:
            pass
    return output


def synergy_and_counterpick_new(radiant_heroes_and_pos, dire_heroes_and_pos, output_message, over45=None):
    # print('my_protracker')
    output = {'radiant_synergy_duo': [], 'dire_synergy_duo': [], 'radiant_synergy_trio': [], 'dire_synergy_trio': [],
              'radiant_counterpick_duo': [], 'dire_counterpick_duo': [], 'radiant_synergy_2vs1':[], 'dire_synergy_2vs1':[]}
    unique_combinations = set()
    with open('./1722505765_top600_heroes_data/synergy_and_counterpick_dict.txt', 'r+') as f:
        data = json.load(f)
        data = data['value']

    # Process Radiant heroes
    output = synergy_team(radiant_heroes_and_pos, dire_heroes_and_pos, output, 'radiant_synergy', data)

    # Process Dire heroes
    output = synergy_team(dire_heroes_and_pos, radiant_heroes_and_pos, output, 'dire_synergy', data)
    output = counterpick_team(radiant_heroes_and_pos, dire_heroes_and_pos, output,
                              'radiant_counterpick', data)
    output = counterpick_team(dire_heroes_and_pos, radiant_heroes_and_pos, output,
                              'dire_counterpick', data)
    try:
        counterpick_dire = sum(output['dire_counterpick_duo'])/len(output['dire_counterpick_duo'])
        counterpick_radiant = sum(output['radiant_counterpick_duo'])/len(output['radiant_counterpick_duo'])
        if len(output['radiant_synergy_2vs1']):
            counterpick_radiant = (counterpick_radiant + sum(output['radiant_synergy_2vs1']) / len(
                output['radiant_synergy_2vs1'])) / 2
        if len(output['dire_synergy_2vs1']):
            counterpick_dire = (counterpick_dire + sum(output['dire_synergy_2vs1']) / len(
                output['dire_synergy_2vs1'])) / 2
        counterpick = (counterpick_radiant - counterpick_dire) * 100
    except ZeroDivisionError:
        counterpick = None
    try:
        synergy_dire = sum(output['dire_synergy_duo']) / len(output['dire_synergy_duo'])
        synergy_radiant = sum(output['radiant_synergy_duo']) / len(output['radiant_synergy_duo'])
        if len(output['dire_synergy_trio']):
            synergy_dire = (synergy_dire + sum(output['dire_synergy_trio']) / len(output['dire_synergy_trio'])) / 2
        if len(output['radiant_synergy_trio']):
            synergy_radiant = (synergy_radiant + sum(output['radiant_synergy_trio']) / len(
                output['radiant_synergy_trio'])) / 2
        synergy = (synergy_radiant - synergy_dire)*100
    except ZeroDivisionError:
        synergy = None
    return f'\nMyProtracker:\nSynergy: {synergy}\nCounterpick: {counterpick}\n'


def synergy_and_counterpick_orig(radiant_heroes_and_pos, dire_heroes_and_pos, output_message, over45=None):
    # print('my_protracker')
    sinergy, counterpick, pos1_vs_team, pos2_vs_team, pos3_vs_team, core_matchup = None, None, None, None, None, None

    # radiant_heroes_and_positions = {'pos 1': {'hero_id': 95, 'hero_name': 'Troll Warlord'}, 'pos 2': {'hero_id': 11, 'hero_name': 'Shadow Fiend'}, 'pos 3': {'hero_id': 33, 'hero_name': 'Enigma'}, 'pos 4': {'hero_id': 136, 'hero_name': 'Marci'}, 'pos 5': {'hero_id': 87, 'hero_name': 'Disruptor'}}
    # dire_heroes_and_positions = {'pos 1': {'hero_id': 99, 'hero_name': 'Bristleback'}, 'pos 2': {'hero_id': 52, 'hero_name': 'Leshrac'}, 'pos 3': {'hero_id': 20, 'hero_name': 'Vengeful Spirit'}, 'pos 4': {'hero_id': 51, 'hero_name': 'Clockwerk'}, 'pos 5': {'hero_id': 91, 'hero_name': 'Io'}}
    with open('./heroes_data/synergy_and_counterpick_dict.txt', 'r+') as f:
        data = json.load(f)['value']
        radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team, dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
        radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, dire_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [], [], [], [], [], [], [], None, None
        # radiant_synergy
        for pos in radiant_heroes_and_pos:
            hero_id = str(radiant_heroes_and_pos[pos]['hero_id'])
            id_pos = {str(item['hero_id']): position_name for position_name, item in radiant_heroes_and_pos.items() if
                      position_name != pos}
            try:
                hero_data = data[hero_id][pos]['synergy_duo']
                for another_hero_id in hero_data:
                    # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                radiant_pos1_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['3', '4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) > 5:
                                    wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                    radiant_pos2_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) > 5:
                                    wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                    radiant_pos3_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos4':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') == '5':
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) > 5:
                                    wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                    radiant_pos4_with_pos5 = wr
                        except:
                            pass
            except:
                pass
        if radiant_pos4_with_pos5 is not None:
            radiant_wr_with += [radiant_pos4_with_pos5]
        radiant_wr_with += radiant_pos3_with_team + radiant_pos2_with_team + radiant_pos1_with_team
        # dire_synergy
        for pos in dire_heroes_and_pos:
            try:
                hero_id = str(dire_heroes_and_pos[pos]['hero_id'])
                hero_data = data[hero_id][pos]['synergy_duo']
                id_pos = {str(item['hero_id']): position_name for position_name, item in
                          dire_heroes_and_pos.items() if position_name != pos}

                for another_hero_id in hero_data:
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                dire_pos1_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['3', '4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) > 5:
                                    wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                    dire_pos2_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) > 5:
                                    wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                    dire_pos3_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos4':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') == '5':
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) > 5:
                                    wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                    dire_pos4_with_pos5 = wr
                        except:
                            pass
            except:
                pass
        if dire_pos4_with_pos5 is not None:
            dire_wr_with += [dire_pos4_with_pos5]
        dire_wr_with += dire_pos3_with_team + dire_pos2_with_team + dire_pos1_with_team
        # against
        for pos in radiant_heroes_and_pos:
            try:
                hero_id = str(radiant_heroes_and_pos[pos]['hero_id'])
                id_pos = {str(item['hero_id']): position_name for position_name, item in
                          dire_heroes_and_pos.items()}
                hero_data = data[hero_id][pos]['counterpick_duo']
                for another_hero_id in hero_data:
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                if position_name == 'pos1':
                                    core_matchup = wr
                                radiant_pos1_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                radiant_pos2_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                radiant_pos3_vs_team.append(wr)
                        except:
                            pass
            except:
                pass
            # dire
            try:
                hero_id = str(dire_heroes_and_pos[pos]['hero_id'])
                hero_data = data[hero_id][pos]['counterpick_duo']
                id_pos = {str(item['hero_id']): position_name for position_name, item in
                          radiant_heroes_and_pos.items()}
                for another_hero_id in hero_data:
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                dire_pos1_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                dire_pos2_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) > 5:
                                wr = (values.count(1) / (values.count(1) + values.count(0))) * 100
                                dire_pos3_vs_team.append(wr)
                        except:
                            pass
            except:
                pass
        radiant_wr_against += radiant_pos3_vs_team + radiant_pos2_vs_team + radiant_pos1_vs_team
        dire_wr_against += dire_pos3_vs_team + dire_pos2_vs_team + dire_pos1_vs_team
        if radiant_pos4_with_pos5 is not None and dire_pos4_with_pos5 is not None:
            sups = radiant_pos4_with_pos5 - dire_pos4_with_pos5
        else:
            sups = None
        dire_wr_with = clean_up(dire_wr_with, 4)
        radiant_wr_with = clean_up(radiant_wr_with, 4)
        radiant_wr_against = clean_up(radiant_wr_against, 5)
        radiant_pos1_vs_team = clean_up(radiant_pos1_vs_team)
        dire_pos1_vs_team = clean_up(dire_pos1_vs_team)
        radiant_pos2_vs_team = clean_up(radiant_pos2_vs_team)
        dire_pos2_vs_team = clean_up(dire_pos2_vs_team)
        radiant_pos3_vs_team = clean_up(radiant_pos3_vs_team)
        dire_pos3_vs_team = clean_up(dire_pos3_vs_team)

        if len(radiant_wr_with) > 0 and len(dire_wr_with) > 0:
            sinergy = round(((sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))),
                            2)
        if len(radiant_wr_against) > 0 and len(dire_wr_against) > 0:
            counterpick = round((sum(radiant_wr_against) / len(radiant_wr_against)) - (
                    sum(dire_wr_against) / len(dire_wr_against)), 2)
        if len(radiant_pos1_vs_team) > 0 and len(dire_pos1_vs_team) > 0:
            pos1_vs_team = round(
                (sum(radiant_pos1_vs_team) / len(radiant_pos1_vs_team)) - (sum(dire_pos1_vs_team) / len(
                    dire_pos1_vs_team)), 2)
        if len(radiant_pos3_vs_team) > 0 and len(dire_pos3_vs_team) > 0:
            pos3_vs_team = round(
                (sum(radiant_pos3_vs_team) / len(radiant_pos3_vs_team)) - (sum(dire_pos3_vs_team) / len(
                    dire_pos3_vs_team)), 2)
        if len(radiant_pos2_vs_team) > 0 and len(dire_pos2_vs_team) > 0:
            pos2_vs_team = round(
                (sum(radiant_pos2_vs_team) / len(radiant_pos2_vs_team)) - (sum(dire_pos2_vs_team) / len(
                    dire_pos2_vs_team)), 2)
        if core_matchup is not None:
            core_matchup -= 50
            core_matchup = round(core_matchup, 2)
        verdict, radiant_predict, dire_predict = analyze_draft(sinergy, counterpick, pos1_vs_team, core_matchup,
                                                               pos2_vs_team, pos3_vs_team,
                                                               sups, over45)
        output_message += (
            f'\nMy protracker: {verdict}\nSinergy: {sinergy}\nCounterpick: {counterpick}\nPos1_vs_team: {pos1_vs_team}\nPos2_vs_team: {pos2_vs_team}\nPos3_vs_team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\n')

    return output_message


def avg_over35(heroes_and_positions):
    with open('./1722505765_top600_heroes_data/over35_dict.txt', 'r') as f:
        data = json.load(f)
        data = data['value']
    # print('avg_over45')
    over45_duo, over45_trio, time_duo, kills_duo, kills_trio, time_trio, radiant_lane_report_unique_combinations, dire_lane_report_unique_combinations = [], [], [], [], [], [], [], []
    over45_unique_combinations = set()
    positions = ['1', '2', '3', '4', '5']
    for pos in positions:
        try:
            hero_id = str(heroes_and_positions['pos' + pos]['hero_id'])
            hero_data = data[hero_id]['pos' + pos]['over35_duo']
            for pos, item in heroes_and_positions.items():
                second_hero_id = str(item['hero_id'])
                try:
                    if second_hero_id != hero_id:
                        duo_data = hero_data[second_hero_id][pos]
                        combo = tuple(sorted([hero_id, second_hero_id]))
                        if combo not in over45_unique_combinations:
                            over45_unique_combinations.add(combo)
                            if len(duo_data['value']) >= 10:
                                over45_duo.append(sum(duo_data['value']) / len(duo_data['value']))
                        # Третий герой
                        for pos3, item3 in heroes_and_positions.items():
                            third_hero_id = str(item3['hero_id'])
                            if third_hero_id not in [second_hero_id, hero_id]:
                                try:
                                    # Создаём отсортированный кортеж идентификаторов героев для уникальности
                                    combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                    if combo not in over45_unique_combinations:
                                        over45_unique_combinations.add(combo)
                                        value = duo_data['over35_trio'][third_hero_id][pos3]['value']
                                        if len(value) >= 10:
                                            over45_trio.append(
                                                sum(duo_data['over35_trio'][third_hero_id][pos3]['value']) / len(
                                                    duo_data['over35_trio'][third_hero_id][pos3]['value']))
                                except:
                                    pass
                except:
                    pass
        except:
            pass
    avg_over45_duo = calculate_average(over45_duo)
    avg_over45_trio = calculate_average(over45_trio)
    avg_over45 = (avg_over45_duo + avg_over45_trio) / 2 if avg_over45_trio is not None else avg_over45_duo
    return avg_over45


def lane_report_def(my_team, enemy_team):
    # print('lane_report')
    with open('./1722505765_top600_heroes_data/lane_dict.txt', 'r') as f:
        heroes_data = json.load(f)['value']
    avg_kills, avg_time, team_line_report, over35, over40, over45, over50, over55 = [], [], [], [], [], [], [], []
    copy_team_pos_and_heroes = {data['hero_id']: pos for pos, data in my_team.items()}
    for hero_id in copy_team_pos_and_heroes:
        pos = copy_team_pos_and_heroes[hero_id]
        data = heroes_data[str(hero_id)]
        if pos in data:
            if pos == 'pos1':
                try:
                    team_mate_hero_id = str(my_team['pos 5']['hero_id'])
                    team_mate_data = data[pos]['lane_report']['with_hero'][team_mate_hero_id]['pos5']['value']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                lane = team_mate_data.count(1) / (
                        team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                team_line_report.append(lane)
            elif pos == 'pos3':
                try:
                    team_mate_hero_id = str(my_team['pos 4']['hero_id'])
                    team_mate_data = \
                        data[pos]['lane_report']['with_hero'][team_mate_hero_id]['pos4']['value']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                lane = team_mate_data.count(1) / (
                        team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                team_line_report.append(lane)
            elif pos == 'pos2':
                try:
                    team_mate_hero_id = str(enemy_team['pos 2']['hero_id'])
                    team_mate_data = \
                        data[pos]['lane_report']['against_hero'][team_mate_hero_id]['pos2']['value']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                lane = team_mate_data.count(1) / (
                        team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                team_line_report.append(lane)
            pass
    team_line_report = [i for i in team_line_report if i > 0.54 or i < 0.46]
    team_avg_lanes = sum(team_line_report) / len(team_line_report)
    return round(team_avg_lanes, 2)


def calculate_average(values):
    return sum(values) / len(values) if values else None

def tm_kills(radiant_heroes_and_positions, dire_heroes_and_positions):
    output_data = {'dire_kills_duo': [], 'dire_kills_trio': [], 'dire_time_duo': [], 'dire_time_trio': [],
                   'radiant_kills_duo': [], 'radiant_kills_trio': [], 'radiant_time_duo': [], 'radiant_time_trio': []}
    # print('tm_kills')
    positions = ['1', '2', '3', '4', '5']
    radiant_time_unique_combinations, radiant_kills_unique_combinations, dire_kills_unique_combinations, dire_time_unique_combinations = set(), set(), set(), set()
    with open('./pro_heroes_data/total_time_kills_dict.txt', 'r') as f:
        data = json.load(f)
        data = data['value']
    for pos in positions:
        # radiant_synergy

        try:
            hero_id = str(radiant_heroes_and_positions['pos' + pos]['hero_id'])
            time_data = data[hero_id]['pos' + pos]['total_time_duo']
            kills_data = data[hero_id]['pos' + pos]['total_kills_duo']
            for hero_data in [time_data, kills_data]:
                for pos, item in radiant_heroes_and_positions.items():
                    second_hero_id = str(item['hero_id'])
                    try:
                        if second_hero_id != hero_id:
                            duo_data = hero_data[second_hero_id][pos]
                            if len(duo_data['value']) >= 2:
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
                                        try:
                                            # Создаём отсортированный кортеж идентификаторов героев для уникальности
                                            combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                            if hero_data == time_data:
                                                if combo not in radiant_time_unique_combinations:
                                                    radiant_time_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_time_trio'][third_hero_id][pos3]['value']
                                                    value = (sum(trio_data) / len(trio_data)) / 60
                                                    output_data['radiant_time_trio'].append(value)
                                            elif hero_data == kills_data:
                                                if combo not in radiant_kills_unique_combinations:
                                                    radiant_kills_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_kills_trio'][third_hero_id][pos3]['value']
                                                    value = sum(trio_data) / len(trio_data)
                                                    output_data['radiant_kills_trio'].append(value)

                                        except:
                                            pass
                    except:
                        pass
        except:
            pass
        # dire_synergy
        try:
            hero_id = str(dire_heroes_and_positions['pos' + pos]['hero_id'])
            time_data = data[hero_id]['pos' + pos][
                'total_time_duo']
            kills_data = data[hero_id]['pos' + pos][
                'total_kills_duo']
            for hero_data in [time_data, kills_data]:
                for pos, item in dire_heroes_and_positions.items():
                    second_hero_id = str(item['hero_id'])
                    try:
                        if second_hero_id != hero_id:
                            duo_data = hero_data[second_hero_id][pos]
                            if len(duo_data['value']) >= 2:
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
                                        try:
                                            combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                            if hero_data == time_data:
                                                if combo not in dire_time_unique_combinations:
                                                    dire_time_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_time_trio'][third_hero_id][pos3]['value']
                                                    value = (sum(trio_data) / len(trio_data)) / 60
                                                    output_data['dire_time_trio'].append(value)
                                            elif hero_data == kills_data:
                                                if combo not in dire_kills_unique_combinations:
                                                    dire_kills_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_kills_trio'][third_hero_id][pos3]['value']
                                                    value = sum(trio_data) / len(trio_data)
                                                    output_data['dire_kills_trio'].append(value)

                                        except:
                                            pass

                    except:
                        pass
        except:
            pass

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
    radiant_time_unique_combinations, radiant_kills_unique_combinations, dire_kills_unique_combinations, dire_time_unique_combinations = set(), set(), set(), set()
    with open('./all_teams/total_time_kills_dict.txt', 'r') as f:
        data = json.load(f)['teams']
    if radiant_team_name in data and dire_team_name in data:
        work_data = data[radiant_team_name]
        for pos in positions:
            # radiant_synergy
            try:
                hero_id = str(radiant_heroes_and_pos['pos' + pos]['hero_id'])
                time_data = work_data[hero_id]['pos' + pos]['total_time_duo']
                kills_data = work_data[hero_id]['pos' + pos]['total_kills_duo']
                for hero_data in [time_data, kills_data]:
                    for pos, item in radiant_heroes_and_pos.items():
                        second_hero_id = str(item['hero_id'])
                        try:
                            if second_hero_id != hero_id:
                                duo_data = hero_data[second_hero_id][pos]
                                if len(duo_data['value']) >= min_len:
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
                                            try:
                                                # Создаём отсортированный кортеж идентификаторов героев для уникальности
                                                combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                                if hero_data == time_data:
                                                    if combo not in radiant_time_unique_combinations:
                                                        radiant_time_unique_combinations.add(combo)
                                                        trio_data = duo_data['total_time_trio'][third_hero_id][pos3]['value']
                                                        value = (sum(trio_data) / len(trio_data)) / 60
                                                        output_data['radiant_time_trio'].append(value)
                                                elif hero_data == kills_data:
                                                    if combo not in radiant_kills_unique_combinations:
                                                        radiant_kills_unique_combinations.add(combo)
                                                        trio_data = duo_data['total_kills_trio'][third_hero_id][pos3]['value']
                                                        value = sum(trio_data) / len(trio_data)
                                                        output_data['radiant_kills_trio'].append(value)

                                            except:
                                                pass
                        except:
                            pass
            except:
                pass
        # dire_synergy
        dire_team_name.replace('g2.invictus gaming', 'g2 x ig')
        work_data = data[dire_team_name]
        for pos in positions:
            try:
                hero_id = str(dire_heroes_and_pos['pos' + pos]['hero_id'])
                time_data = work_data[hero_id]['pos' + pos][
                    'total_time_duo']
                kills_data = work_data[hero_id]['pos' + pos][
                    'total_kills_duo']
                for hero_data in [time_data, kills_data]:
                    for pos, item in dire_heroes_and_pos.items():
                        second_hero_id = str(item['hero_id'])
                        try:
                            if second_hero_id != hero_id:
                                duo_data = hero_data[second_hero_id][pos]
                                if len(duo_data['value']) >= min_len:
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
                                            try:
                                                combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                                if hero_data == time_data:
                                                    if combo not in dire_time_unique_combinations:
                                                        dire_time_unique_combinations.add(combo)
                                                        trio_data = duo_data['total_time_trio'][third_hero_id][pos3]['value']
                                                        value = (sum(trio_data) / len(trio_data)) / 60
                                                        output_data['dire_time_trio'].append(value)
                                                elif hero_data == kills_data:
                                                    if combo not in dire_kills_unique_combinations:
                                                        dire_kills_unique_combinations.add(combo)
                                                        trio_data = duo_data['total_kills_trio'][third_hero_id][pos3]['value']
                                                        value = sum(trio_data) / len(trio_data)
                                                        output_data['dire_kills_trio'].append(value)

                                            except:
                                                pass

                        except:
                            pass
            except:
                pass

        avg_time_trio = calculate_average(output_data['radiant_time_trio'] + output_data['dire_time_trio'])
        avg_kills_trio = calculate_average(output_data['radiant_kills_trio'] + output_data['dire_kills_trio'])
        avg_time_duo = calculate_average(output_data['radiant_time_duo'] + output_data['dire_time_duo'])
        avg_kills_duo = calculate_average(output_data['radiant_kills_duo'] + output_data['dire_kills_duo'])

        avg_kills = (avg_kills_trio + avg_kills_duo) / 2 if avg_kills_trio and avg_kills_duo else avg_kills_duo
        avg_time = (avg_time_duo + avg_time_trio) / 2 if avg_time_trio and avg_time_duo else avg_time_duo
        if len(output_data['dire_kills_duo']) > 0 and len(output_data['radiant_kills_duo']) > 0:
            return round(avg_kills, 2), round(avg_time, 2)
        else: raise TypeError
    else:
        if radiant_team_name not in data:
            print(f'{radiant_team_name} not in team list')
        if dire_team_name not in data:
            print(f'{dire_team_name} not in team list')
