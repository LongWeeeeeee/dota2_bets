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




def get_live_matches():
    result = get_team_positions()
    if result is not None:
        radiant_heroes_and_pos, dire_heroes_and_pos, radiant_team_name, dire_team_name, url, score = result
        print(f'{radiant_team_name} VS {dire_team_name}')
        dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos, dire_heroes_and_positions=dire_heroes_and_pos, radiant_team_name=radiant_team_name,
                        dire_team_name=dire_team_name, score=score, antiplagiat_url=url)


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



def get_team_positions():
    url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        result = get_map_id(data)
        if result is not None:
            url, radiant_team_name, dire_team_name, score = result
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
                    radiant_heroes_and_pos[f'pos {i+1}'] = heroes[i]

                for i in range(5):
                    dire_heroes_and_pos[f'pos {i+1}'] = heroes[i+5]

                return radiant_heroes_and_pos, dire_heroes_and_pos, radiant_team_name, dire_team_name, url, score
        else:
            print('нету live матчей')



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


def dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name, dire_team_name, antiplagiat_url, score=[0,0], core_matchup=None, output_message=''):
    print('dota2protracker')
    radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [] ,[], [], [], [], [], None, None
    for position in radiant_heroes_and_positions:
        hero_url = radiant_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка dota2protracekr\n{url}')
        soup = BeautifulSoup(response.text, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        # #wr agai
        index = {'pos 1': 1, 'pos 2': 3, 'pos 3': 5, 'pos 4': len(stats) - 3, 'pos 5': len(stats) - 1}
        i = index[position]
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        if len(hero_divs) == 0:
            divs_dict = dict()
            for i, digit in enumerate(list(index.values())):
                hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
                divs_dict[digit] = hero_divs
            c = 0
            for i in divs_dict:
                if len(divs_dict[i]) > c:
                    c = len(divs_dict[i])
                    hero_divs = divs_dict[i]
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')
            if position == 'pos 1':
                if 'pos 2' in data_pos and data_hero == radiant_heroes_and_positions['pos 2']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos1_with_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == radiant_heroes_and_positions['pos 3']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos1_with_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos1_with_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos1_with_pos5 = data_wr

            if position == 'pos 2':
                if 'pos 3' in data_pos and data_hero == radiant_heroes_and_positions['pos 3']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos2_with_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos2_with_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos2_with_pos5 = data_wr

            if position == 'pos 3':
                if 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos3_with_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos3_with_pos5 = data_wr

            if position == 'pos 4':
                if 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    radiant_pos4_with_pos5 = data_wr
    for position in dire_heroes_and_positions:
        hero_url = dire_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка dota2protracekr\n{url}')
        soup = BeautifulSoup(response.text, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        index = {'pos 1': 1, 'pos 2': 3, 'pos 3': 5, 'pos 4': len(stats) - 3, 'pos 5': len(stats) - 1}
        i = index[position]
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        if len(hero_divs) == 0:
            divs_dict = dict()
            for i, digit in enumerate(list(index.values())):
                hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
                divs_dict[digit] = hero_divs
            c = 0
            for i in divs_dict:
                if len(divs_dict[i]) > c:
                    c = len(divs_dict[i])
                    hero_divs = divs_dict[i]
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')
            if position == 'pos 1':
                if 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    dire_pos1_with_pos2 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    dire_pos1_with_pos3 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    dire_pos1_with_pos4 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_pos1_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)

            if position == 'pos 2':
                if 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    dire_pos2_with_pos3 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    dire_pos2_with_pos4 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_pos2_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)

            if position == 'pos 3':
                if 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    dire_pos3_with_pos4 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_pos3_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)
            if position == 'pos 4':
                if 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_pos4_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)
    for position in radiant_heroes_and_positions:
        hero_url = radiant_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка dota2protracekr\n{url}')
        soup = BeautifulSoup(response.text, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        # #wr against
        cores = ['pos 1', 'pos 2', 'pos 3', 'pos 5', 'pos 4']
        index = {'pos 1': 0, 'pos 2': 2, 'pos 3': 4, 'pos 4': len(stats) - 4, 'pos 5': len(stats) - 2}
        i = index[position]
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        if len(hero_divs) == 0:
            divs_dict = dict()
            for i, digit in enumerate(list(index.values())):
                hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
                divs_dict[digit] = hero_divs
            c = 0
            for i in divs_dict:
                if len(divs_dict[i]) > c:
                    c = len(divs_dict[i])
                    hero_divs = divs_dict[i]
        for div in hero_divs:
                # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                data_hero = div.get('data-hero')
                data_wr = int(float(div.get('data-wr')))
                data_pos = div.get('data-pos')
                positions = ['pos 1', 'pos 2', 'pos 3', 'pos 4', 'pos 5']
                protracker_pos = data_pos.split(',')[0]
                # проверить
                if protracker_pos in positions:
                    for pos in positions:
                        if pos in data_pos and data_hero == dire_heroes_and_positions[pos]:
                            if position == 'pos 1' and pos == 'pos 1':
                                core_matchup = data_wr
                            radiant_wr_against.append(data_wr)
                    if position == 'pos 1' and data_hero == dire_heroes_and_positions[protracker_pos]:
                        radiant_pos1_vs_team.append(data_wr)
                    if position == 'pos 2' and data_hero == dire_heroes_and_positions[protracker_pos]:
                        radiant_pos2_vs_team.append(data_wr)
                    if position == 'pos 3' and data_hero == dire_heroes_and_positions[protracker_pos]:
                        radiant_pos3_vs_team.append(data_wr)

                    if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                        dire_pos1_vs_team.append(100-data_wr)
                    if 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                        dire_pos2_vs_team.append(100-data_wr)
                    if 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                        dire_pos3_vs_team.append(100-data_wr)
    #
    output_message += f'Счет: {score}\n'
    if radiant_pos4_with_pos5 is not None and dire_pos4_with_pos5 is not None:
        sups = radiant_pos4_with_pos5 - dire_pos4_with_pos5
    else:
        sups = None
    dire_wr_with = clean_up(dire_wr_with)
    radiant_wr_with = clean_up(radiant_wr_with)
    radiant_wr_against = clean_up(radiant_wr_against)
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
    if None not in [sinergy, counterpick, pos1_vs_team, core_matchup, pos2_vs_team, pos3_vs_team, sups]:
        if ((sinergy > 0 and counterpick > 0 and pos1_vs_team > 0 and core_matchup > 0 and pos2_vs_team > 0 and pos3_vs_team > 0 and sups > 0) or \
                (sinergy < 0 and counterpick < 0 and pos1_vs_team < 0 and core_matchup < 0 and pos2_vs_team < 0 and pos3_vs_team < 0 and sups < 0)):
            output_message += f'ХОРОШАЯ СТАВКА\n'
    else:
        output_message += f'ПЛОХАЯ СТАВКА!!!\n'


    output_message += f'Sinergy: {sinergy}\nCounterpick: {counterpick}\nPos1_vs_team: {pos1_vs_team}\nPos2vs_team: {pos2_vs_team}\nPos3vs_team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\n'
    if radiant_pos4_with_pos5 is None:
        output_message += f'pos 4 {radiant_heroes_and_positions["pos 4"]} with pos 5 {radiant_heroes_and_positions["pos 5"]} нету на proracker\n'
    if dire_pos4_with_pos5 is None:
        output_message += f'pos 4 {dire_heroes_and_positions["pos 4"]} with pos 5 {dire_heroes_and_positions["pos 5"]} нету на proracker\n'
    if len(radiant_pos3_vs_team) < 1:
        output_message+= f'Недостаточно данных pos 3 {radiant_heroes_and_positions["pos 3"]} vs {dire_heroes_and_positions}\n'
    if len(dire_pos3_vs_team) < 1:
        output_message+= f'Недостаточно данных pos 3 {dire_heroes_and_positions["pos 3"]} vs {radiant_heroes_and_positions}\n'
    if len(dire_pos2_vs_team) < 1:
        output_message+= f'Недостаточно данных pos 2 {dire_heroes_and_positions["pos 2"]} vs {radiant_heroes_and_positions}\n'
    if len(radiant_pos2_vs_team) <1:
        output_message+=f'Недостаточно данных pos 2 {radiant_heroes_and_positions["pos 2"]} vs {dire_heroes_and_positions}\n'
    if len(radiant_pos1_vs_team) < 1:
        output_message+=f'Недостаточно данных pos 1 {radiant_heroes_and_positions["pos 1"]} vs {dire_heroes_and_positions}\n'
    if len(dire_pos1_vs_team) < 1:
        output_message+=f'Недостаточно данных pos 1 {dire_heroes_and_positions["pos 1"]} vs {radiant_heroes_and_positions}\n'
    if core_matchup is None:
        output_message+=f'{radiant_heroes_and_positions["pos 1"]} vs {dire_heroes_and_positions["pos 1"]} нету на dota2protracker\n'
    if len(dire_wr_with) < 1:
        output_message+=f'Недостаточная выборка винрейтов у {dire_team_name} между командой\n{dire_heroes_and_positions}\n'
    if len(radiant_wr_with) < 1:
        output_message+=f'Недостаточная выборка винрейтов у {radiant_team_name} между командой\n{radiant_heroes_and_positions}\n'
    if len(radiant_wr_against) < 1:
        output_message+=f'Недостаточная выборка винрейтов у команду между друг друга\n{radiant_heroes_and_positions}\n{dire_heroes_and_positions}\n'
    if sups is None:
        if radiant_pos4_with_pos5 is None:
            output_message += f'{radiant_heroes_and_positions["pos 4"]} pos 4 with {radiant_heroes_and_positions["pos 5"]} pos 5 Нету на dota2protracker\n'
        if dire_pos4_with_pos5 is None:
            output_message += f'{dire_heroes_and_positions["pos 4"]} pos 4 with {dire_heroes_and_positions["pos 5"]} pos 5 Нету на dota2protracker\n'
    for hero in list(radiant_heroes_and_positions.values()):
        if hero in game_changer_list:
            output_message+=f'Аккуратно! У {radiant_team_name} есть {hero}, который может изменить исход боя\n'
    output_message += '\n'
    for hero in list(dire_heroes_and_positions.values()):
        if hero in game_changer_list:
            output_message+=f'Аккуратно! У {dire_team_name} есть {hero}, который может изменить исход боя\n'
    send_message(output_message)
    add_url(antiplagiat_url)



def get_map_id(data):
    for match in data['rows']:
        if match['tournament']['tier'] in [1    ] and match['team_dire'] is not None and match['team_radiant'] is not None and 'Kobold' not in match['tournament']['name']:
            radiant_team_name = match['team_radiant']['name'].lower()
            dire_team_name = match['team_dire']['name'].lower()
            score = match['best_of_score']
            for karta in match['related_matches']:
                if karta['status'] == 'online':
                    map_id = karta['id']
                    url = f'https://cyberscore.live/en/matches/{map_id}/'
                    result = if_unique(url)
                    if result is not None:
                        return url, radiant_team_name, dire_team_name, score
    # for match in data['rows']:
    #     if match['tournament']['tier'] in [1, 2] and 'name' in match['team_radiant'] and 'name' in match[
    #         'team_radiant']:
    #         radiant_team_name = match['team_radiant']['name']
    #         dire_team_name = match['team_dire']['name']
    #         time_until = datetime.datetime.fromisoformat(match['date_start']) + datetime.timedelta(hours=3)
    #         now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
    #         to_wait = time_until - now
    #         if to_wait.seconds > 0:
    #
    #             print(f'{radiant_team_name} vs {dire_team_name}\nсплю {to_wait.seconds/60} минут')
    #             time.sleep(to_wait.seconds)




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


def clean_up(inp):
    copy = inp.copy()
    for i in inp:
        if i >45 and i <55:
            copy.remove(i)
    if len(copy) == 0:
        return inp
    else:
        return copy


def send_message(message):
    bot_token = f'{keys.Token}'
    chat_id = f'{keys.Chat_id}'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, json=payload)

# testing
# radiant_heroes_and_positions={'pos 1': 'Troll Warlord', 'pos 2': 'Zeus', 'pos 3': 'Kunkka', 'pos 4': 'Techies', 'pos 5': "Elder Titan"}
# dire_heroes_and_positions={'pos 1': 'Faceless Void', 'pos 2': 'Leshrac', 'pos 3': 'Dark Seer', 'pos 4': 'Clockwerk', 'pos 5': 'Gyrocopter'}
# dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_positions, dire_heroes_and_positions=dire_heroes_and_positions, radiant_team_name='Tundra', dire_team_name='Heroic', score=['0','0'])