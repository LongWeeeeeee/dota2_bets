# Структура приложения: Анализ пиков + анализ игроков + анализ команды
# можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
# сверха прошлых матчей и прошлых встреч
# Отладка винрейта на старых матчах
# Проверка того что все правильно работает
# ранги неправильно работают
import html
import json
import requests
from bs4 import BeautifulSoup
import re
import datetime

import id_to_name
import keys
from id_to_name import game_changer_list







def get_urls(url, target_datetime = 0):
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
                target_datetime = datetime.datetime.strptime(target_datetime_str, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=2, minutes=54)
        if not len(live_matches_urls):
            live_matches_urls = None
        return live_matches_urls, target_datetime
    else: print(f'{response.status_code}')


def get_team_names(soup):
    tags_block = soup.find('div', class_='plus__stats-details desktop-none')
    tags = tags_block.find_all('span', class_='title')
    scores = soup.find('div', class_='score__scores live').find_all('span')
    score = [i.text.strip() for i in scores]
    radiant_team_name, dire_team_name = None, None
    for tag in tags:
        team_info = tag.text.strip().split('\n')
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
                if id_to_name.translate[id] == heroes[i]:
                    hero_id = id
                    radiant_heroes_and_pos[f'pos {i+1}'] = {'hero_id':hero_id, 'hero_name' : heroes[i]}

        for i in range(5):
            for id in id_to_name.translate:
                if id_to_name.translate[id] == heroes[i]:
                    hero_id = id
                    dire_heroes_and_pos[f'pos {i+1}'] = {'hero_id':hero_id, 'hero_name' : heroes[i+5]}

        return radiant_heroes_and_pos, dire_heroes_and_pos
    else:
        print('нету live матчей')

def analyze_draft(output_message, sinergy, counterpick, pos1_vs_team, core_matchup, pos2_vs_team, pos3_vs_team,
                  sups):
    values = {'sinergy':sinergy, 'counterpick':counterpick, 'pos1_vs_team':pos1_vs_team, 'core_matchup':core_matchup, 'pos2_vs_team':pos2_vs_team, 'pos3_vs_team':pos3_vs_team, 'sups':sups}
    other_values = {'sinergy':sinergy, 'counterpick':counterpick, 'core_matchup':core_matchup, 'sups':sups}
    # values_nones = sum(1 for value in values.values() if value is None)
    # other_values_nones = sum(1 for value in other_values.values() if value is None)
    # nones = (values_nones <= 2) * (other_values_nones <= 1)
    # if nones:
    if True:
        # values, other_values = [value for value in values if value is not None], [value for value in other_values if value is not None]
        all_positive_or_negative = all(value >= 0 for value in values.values() if value is not None) + all(value <= 0 for value in values.values() if value is not None)
        other_values_check = all(value >= 0 for value in other_values.values() if value is not None) + all(value <= 0 for value in other_values.values() if value is not None)
        singery_or_counterpick = all(value >= 0 for value in [counterpick, sinergy] if value is not None) + all(
            value <= 0 for value in [counterpick, sinergy] if value is not None)
        both_over9 = all(value <= -9 for value in [counterpick, sinergy] if value is not None) + all(
            value >= 9 for value in [counterpick, sinergy] if value is not None)
        both_over5 = all(value <= -5 for value in [counterpick, sinergy] if value is not None) + all(
            value >= 5 for value in [counterpick, sinergy] if value is not None)
        any_over20 = (all(value > 0 for value in [counterpick, sinergy] if value is not None ) * any(
            value >= 20 for value in [counterpick, sinergy] if value is not None)) + (all(value < 0 for value in [counterpick, sinergy] if value is not None) * any(
            value <= -20 for value in [counterpick, sinergy] if value is not None))
        if counterpick is not None:
            counterpick_over10 = (all(value > 0 for value in [counterpick, sinergy] if value is not None) * counterpick >= 10) +(all(value < 0 for value in [counterpick, sinergy] if value is not None) * counterpick <= -10)
        else:
            counterpick_over10 = False
        if other_values_check and both_over9:
            output_message += f'ОТЛИЧНАЯ СТАВКА ALL IN\n'
        elif (other_values_check and both_over5) or (singery_or_counterpick and counterpick_over10) or any_over20 or both_over9:
            output_message += f'ХОРОШАЯ СТАВКА\n'
        elif (singery_or_counterpick and both_over5) or all_positive_or_negative or other_values_check :
            output_message += f'РИСКОВАЯ СТАВКА\n'
        else:
            output_message += f'ПЛОХАЯ СТАВКА!!!\n'
    else:
        output_message += f'ПЛОХАЯ СТАВКА!!!\n'
    return output_message





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
                            players[player_name]['position'] = player_position
                            lst.remove(player_position)
                            break
                        else:
                            players[player_name]['position'] = player_position
                            lst.remove(player_position)
    if len(lst) == 1:
        for player in players:
            if len(players[player]) == 1:
                players[player]['position'] = lst[0]

    for player in players:
        if 'position' in players[player]:
            heroes_and_position[translate[players[player]['position']]] = players[player]['hero']
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
    if match['team_dire'] is not None and match['team_radiant'] is not None and 'Kobold' not in match['tournament']['name']:
        radiant_team_name = match['team_radiant']['name'].lower()
        dire_team_name = match['team_dire']['name'].lower()
        score = match['best_of_score']
        keywords = ['FISSURE', 'Riyadh', 'International']
        if any(keyword in match['tournament']['name'] for keyword in keywords):
            tier = 1
        else:
            tier = match['tournament']['tier']
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
            if i >=48 and i <=52:
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


def dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name, dire_team_name, score, R_pos_strng=None, D_pos_strng=None, player_check = None, impact_diff=None, tier=None, antiplagiat_url=None, core_matchup=None, output_message='', egb=None):
    print('dota2protracker')
    radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team, dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
    radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [] ,[], [], [], [], [], None, None
    for position in radiant_heroes_and_positions:
        if position != 'pos 5':
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
                tracker_position = synergy['position']
                data_pos = synergy['other_pos']
                data_hero = synergy['other_hero']
                data_wr = synergy['win_rate']
                if synergy['num_matches'] >= 10:
                    # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                    if position == 'pos 1':
                        if len(radiant_pos1_with_team) == 4:
                            break
                        if 'pos 2' in data_pos and data_hero == radiant_heroes_and_positions['pos 2']['hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)
                        elif 'pos 3' in data_pos and data_hero == radiant_heroes_and_positions['pos 3']['hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)
                        elif 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']['hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)
                        elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            radiant_pos1_with_team.append(data_wr)

                    if position == 'pos 2':
                        if len(radiant_pos2_with_team) == 3:
                            break
                        if 'pos 3' in data_pos and data_hero == radiant_heroes_and_positions['pos 3']['hero_name'] and tracker_position == position:
                            radiant_pos2_with_team.append(data_wr)
                        elif 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']['hero_name'] and tracker_position == position:
                            radiant_pos2_with_team.append(data_wr)
                        elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            radiant_pos2_with_team.append(data_wr)

                    if position == 'pos 3':
                        if len(radiant_pos3_with_team) == 2:
                            break
                        if 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']['hero_name'] and tracker_position == position:
                            radiant_pos3_with_team.append(data_wr)
                        elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            radiant_pos3_with_team.append(data_wr)
                    if position == 'pos 4':
                        if radiant_pos4_with_pos5 is not None:
                            break
                        if 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            radiant_pos4_with_pos5 = data_wr
    if radiant_pos4_with_pos5 is not None:
        radiant_wr_with += [radiant_pos4_with_pos5]
    radiant_wr_with = radiant_pos3_with_team + radiant_pos2_with_team + radiant_pos1_with_team
    for position in dire_heroes_and_positions:
        if position != 'pos 5':
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
                tracker_position = synergy['position']
                data_pos = synergy['other_pos']
                data_hero = synergy['other_hero']
                data_wr = synergy['win_rate']
                if synergy['num_matches'] >= 8:
                    if position == 'pos 1':
                        if len(dire_pos1_with_team) == 4:
                            break
                        if 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']['hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)
                        elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']['hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)
                        elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']['hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)
                        elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            dire_pos1_with_team.append(data_wr)

                    if position == 'pos 2':
                        if len(dire_pos2_with_team) == 3:
                            break
                        if 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']['hero_name'] and tracker_position == position:
                            dire_pos2_with_team.append(data_wr)
                        elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']['hero_name'] and tracker_position == position:
                            dire_pos2_with_team.append(data_wr)
                        elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            dire_pos2_with_team.append(data_wr)

                    if position == 'pos 3':
                        if len(dire_pos3_with_team) == 2:
                            break
                        if 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']['hero_name'] and tracker_position == position:
                            dire_pos3_with_team.append(data_wr)
                        elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            dire_pos3_with_team.append(data_wr)
                    if position == 'pos 4':
                        if dire_pos4_with_pos5 is not None:
                            break
                        if 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']['hero_name'] and tracker_position == position:
                            dire_pos4_with_pos5 = data_wr
    if dire_pos4_with_pos5 is not None:
        dire_wr_with += [dire_pos4_with_pos5]
    dire_wr_with = dire_pos3_with_team + dire_pos2_with_team + dire_pos1_with_team
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
            tracker_position = matchup['position']
            data_pos = matchup['other_pos']
            data_hero = matchup['other_hero']
            data_wr = matchup['win_rate']
            if matchup['num_matches'] >= 8 and data_pos in radiant_heroes_and_positions:
                if position == 'pos 1' and tracker_position == 'pos 1' and data_hero == dire_heroes_and_positions[data_pos]['hero_name']:
                    if data_pos == 'pos 1':
                        core_matchup = data_wr
                    radiant_pos1_vs_team.append(data_wr)
                elif position == 'pos 2' and tracker_position == 'pos 2' and data_hero == dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_pos2_vs_team.append(data_wr)
                elif position == 'pos 3' and tracker_position == 'pos 3' and data_hero == dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_pos3_vs_team.append(data_wr)
                elif position == 'pos 4' and tracker_position == 'pos 4' and data_hero == dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_wr_against.append(data_wr)
                elif position == 'pos 5' and tracker_position == 'pos 5' and data_hero == dire_heroes_and_positions[data_pos]['hero_name']:
                    radiant_wr_against.append(data_wr)

                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']['hero_name'] and tracker_position == position:
                    dire_pos1_vs_team.append(100-data_wr)
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']['hero_name'] and tracker_position == position:
                    dire_pos2_vs_team.append(100-data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']['hero_name'] and tracker_position == position:
                    dire_pos3_vs_team.append(100-data_wr)
    radiant_wr_against += radiant_pos3_vs_team + radiant_pos2_vs_team + radiant_pos1_vs_team
    if type(antiplagiat_url) == int:
        output_message += f'https://stratz.com/matches/{antiplagiat_url}/live\n'
    elif antiplagiat_url is not None:
        output_message += antiplagiat_url + '\n'
    output_message += f'Счет: {score}\n'
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
    sinergy, counterpick ,pos1_vs_team, pos2_vs_team, pos3_vs_team  = None, None, None, None, None
    output_message += f'{radiant_team_name} vs {dire_team_name}\n'
    if len(radiant_wr_with) > 0 and len(dire_wr_with) > 0:
        sinergy = (sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))
    if len(radiant_wr_against) > 0:
        counterpick = sum(radiant_wr_against) / len(radiant_wr_against) - 50
    if len(radiant_pos1_vs_team) > 0 and len(dire_pos1_vs_team) > 0:
        pos1_vs_team = sum(radiant_pos1_vs_team) / len(radiant_pos1_vs_team) - sum(dire_pos1_vs_team) / len(
            dire_pos1_vs_team)
    if len(radiant_pos3_vs_team) > 0 and len(dire_pos3_vs_team) > 0:
        pos3_vs_team = sum(radiant_pos3_vs_team) / len(radiant_pos3_vs_team) - sum(dire_pos3_vs_team) / len(
            dire_pos3_vs_team)
    if len(radiant_pos2_vs_team) > 0 and len(dire_pos2_vs_team) > 0:
        pos2_vs_team = sum(radiant_pos2_vs_team) / len(radiant_pos2_vs_team) - sum(dire_pos2_vs_team) / len(
            dire_pos2_vs_team)
    if core_matchup is not None:
        core_matchup -= 50
    output_message = analyze_draft(output_message, sinergy, counterpick, pos1_vs_team, core_matchup, pos2_vs_team, pos3_vs_team,
                  sups)
    for hero in list(radiant_heroes_and_positions.values()):
        if hero in game_changer_list:
            output_message += f'Аккуратно! У {radiant_team_name} есть {hero}, который может изменить исход боя\n'
            check = True
    for hero in list(dire_heroes_and_positions.values()):
        if hero in game_changer_list:
            output_message += f'Аккуратно! У {dire_team_name} есть {hero}, который может изменить исход боя\n'
            check = True
    output_message += f'Sinergy: {sinergy}\nCounterpick: {counterpick}\nPos1_vs_team: {pos1_vs_team}\nPos2vs_team: {pos2_vs_team}\nPos3vs_team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\n'
    radiant_output = ", ".join([f"'{pos}' : '{data['hero_name']}'" for pos, data in radiant_heroes_and_positions.items()])
    dire_output = ", ".join([f"'{pos}' : '{data['hero_name']}'" for pos, data in dire_heroes_and_positions.items()])
    if radiant_pos4_with_pos5 is None:
        output_message += f'pos 4 {radiant_heroes_and_positions["pos 4"]["hero_name"]} with pos 5 {radiant_heroes_and_positions["pos 5"]["hero_name"]} нету на proracker\n'
    if dire_pos4_with_pos5 is None:
        output_message += f'pos 4 {dire_heroes_and_positions["pos 4"]["hero_name"]} with pos 5 {dire_heroes_and_positions["pos 5"]["hero_name"]} нету на proracker\n'
    if len(radiant_pos3_vs_team) < 1:
        output_message += f'Недостаточно данных pos 3 {radiant_heroes_and_positions["pos 3"]["hero_name"]} vs {dire_output}\n'
    if len(dire_pos3_vs_team) < 1:
        output_message += f'Недостаточно данных pos 3 {dire_heroes_and_positions["pos 3"]["hero_name"]} vs {radiant_output}\n'
    if len(dire_pos2_vs_team) < 1:
        output_message += f'Недостаточно данных pos 2 {dire_heroes_and_positions["pos 2"]["hero_name"]} vs {radiant_output}\n'
    if len(radiant_pos2_vs_team) < 1:
        output_message += f'Недостаточно данных pos 2 {radiant_heroes_and_positions["pos 2"]["hero_name"]} vs {dire_output}\n'
    if len(radiant_pos1_vs_team) < 1:
        output_message += f'Недостаточно данных pos 1 {radiant_heroes_and_positions["pos 1"]["hero_name"]} vs {dire_output}\n'
    if len(dire_pos1_vs_team) < 1:
        output_message += f'Недостаточно данных pos 1 {dire_heroes_and_positions["pos 1"]["hero_name"]} vs {dire_output}\n'
    if core_matchup is None:
        output_message += f'{radiant_heroes_and_positions["pos 1"]} vs {dire_heroes_and_positions["pos 1"]["hero_name"]} нету на dota2protracker\n'
    if len(dire_wr_with) < 1:
        output_message += f'Недостаточная выборка винрейтов у {dire_team_name} между командой:\n{dire_output}\n'
    if len(radiant_wr_with) < 1:
        output_message += f'Недостаточная выборка винрейтов у {radiant_team_name} между командой:\n{radiant_output}\n'
    if len(radiant_wr_against) < 1:
        output_message += f'Недостаточная выборка винрейтов у команды между друг другом:\n{radiant_output}\n{dire_output}\n'
    if sups is None:
        if radiant_pos4_with_pos5 is None:
            output_message += f'{radiant_heroes_and_positions["pos 4"]["hero_name"]} pos 4 with {radiant_heroes_and_positions["pos 5"]["hero_name"]} pos 5 Нету на dota2protracker\n'
        if dire_pos4_with_pos5 is None:
            output_message += f'{dire_heroes_and_positions["pos 4"]["hero_name"]} pos 4 with {dire_heroes_and_positions["pos 5"]["hero_name"]} pos 5 Нету на dota2protracker\n'
    if tier in [1, 2, 3]:
        if 'ОТЛИЧНАЯ СТАВКА' in output_message or 'ХОРОШАЯ СТАВКА' in output_message:
            send_message(output_message)
        else:
            print(output_message)
    elif egb:
        if not 'ПЛОХАЯ СТАВКА!!!' in output_message:
            send_message(output_message)
            print(output_message)
        else:
            if egb:
                if player_check or impact_diff >= 15 or impact_diff <= -15:
                    send_message(output_message)
            print(output_message)


    if antiplagiat_url is not None:
        add_url(antiplagiat_url)

# radiant_heroes_and_positions={'pos 1':{'hero_name':'Weaver'}, 'pos 5':{'hero_name':'Io'}, 'pos 2':{'hero_name':'Leshrac'}, 'pos 3':{'hero_name':'Axe'}, 'pos 4':{'hero_name':'Dark Willow'}}
#
# dire_heroes_and_positions={'pos 1':{'hero_name':'Alchemist'}, 'pos 5':{'hero_name':'Warlock'}, 'pos 3':{'hero_name':'Doom'}, 'pos 4':{'hero_name':'Techies'}, 'pos 2':{'hero_name':'Queen of Pain'}}
#
# dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_positions, dire_heroes_and_positions=dire_heroes_and_positions, radiant_team_name='Tundra', dire_team_name='Heroic', score=['0','0'], tier=2)