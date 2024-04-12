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
import time
import re
import datetime
import keys


game_changer_list = ['Faceless Void', 'Enigma', 'Phoenix', 'Disruptor', 'Bane', 'Magnus', 'Bristleback', 'Doom', 'Lone Druid', 'Tusk', 'Arc Warden', 'Kunkka', 'Phantom Lancer', 'Axe', 'Storm Spirit', 'Tinker', 'Huskar']

def get_live_matches(url='https://dltv.org/matches'):
    live_matches_urls, sleep_time = get_urls(url)
    if live_matches_urls is not None:
        print(f'Сейчас идут {len(live_matches_urls)} матча')
        for url in live_matches_urls:
            response = requests.get(url).text
            soup = BeautifulSoup(response, 'lxml')
            radiant_block = soup.find('div', class_='picks__new-picks__picks radiant')
            if radiant_block is not None:
                items = radiant_block.find('div', class_='items')
                # Проверяем, не скрыт ли элемент и содержит ли он другие элементы
                if items and items.get('style') != 'display: none;' and len(items.find_all('div', class_='pick')) >= 4:
                    radiant_players, dire_players = get_player_names_and_heroes(radiant_block, soup)
                    result = get_team_names(soup)
                    if result is not None:
                        radiant_team_name, dire_team_name = result
                        result = get_team_positions(radiant_team_name, dire_team_name, radiant_players, dire_players)
                        if result is not None:
                            radiant_heroes_and_positions, dire_heroes_and_positions, url = result
                            if if_unique(url):
                                print(f'{radiant_team_name} VS {dire_team_name}')
                                dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name,
                                                dire_team_name, url)
                else:
                    print('Пики еще не закончились')
    else:
        now = datetime.datetime.now()
        if sleep_time > now:
            wait_seconds = (sleep_time - now).total_seconds()
            print(f'Live матчей нет, сплю {wait_seconds/60} минут')
            time.sleep(wait_seconds)


def get_urls(url, target_datetime = 0):
    response = requests.get(url)
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
                target_datetime = datetime.datetime.strptime(target_datetime_str, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=3)
        if not len(live_matches_urls):
            live_matches_urls = None
        return live_matches_urls, target_datetime


def get_team_names(soup):
    tags_block = soup.find('div', class_='plus__stats-details desktop-none')
    tags = tags_block.find_all('span', class_='title')
    radiant_team_name, dire_team_name = None, None
    for tag in tags:
        team_info = tag.text.strip().split('\n')
        if team_info[1].replace(' ', '').lower() == 'radiant':
            radiant_team_name = team_info[0].lower()
        else:
            dire_team_name = team_info[0].lower()
    return radiant_team_name, dire_team_name


def get_player_names_and_heroes(radiant_block, soup):
    radiant_players, dire_players = {}, {}
    radiant_heroes_block = radiant_block.find_all('div', class_='pick player')
    dire_block = soup.find('div', class_='picks__new-picks__picks dire')
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
    return radiant_players, dire_players


def get_team_ids(radiant_team_name, dire_team_name):
    url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
    response = requests.get(url).text
    matches = json.loads(response)
    for match in matches['rows']:
        if match['team_radiant']['name'].lower() in radiant_team_name.lower() or match['team_dire'][
        'name'].lower() in dire_team_name.lower():
            radiant_team_id = match['team_radiant']['id']
            dire_team_id = match['team_dire']['id']
            return radiant_team_id, dire_team_id


def get_team_positions(radiant_team_name, dire_team_name, radiant_players, dire_players):
    radiant_pick, dire_pick = {}, {}
    nick_fixes = {'griefy': 'asdekor_r', 'placebo':'egxrdemxn', 'faker':'kxy', 'satanic':'king', '999xu': 'imitator', 'emptiness': 'aind','red2' :'nico' ,'bnc' :'xxxblincc', 'xdddd':'fachero','sagiri': 'kcl',
                  'somnia': 'oushaktian casedrop.com', 'yuukichi': 'hiori','neko': 'sh1do', 'ra1ncloud': 'v1necy', 'qjy': 'newbie', 'young ame is back': 'a1one', 'ksh':'raz', 'xn丶e': 'xne-'}
    lst = ['mid', 'semi-support', 'carry', 'main-support', 'offlaner']
    radiant_lst = ['mid', 'semi-support', 'carry', 'main-support', 'offlaner']
    dire_lst = ['mid', 'semi-support', 'carry', 'main-support', 'offlaner']
    translate = {'mid': 'pos 2', 'semi-support': 'pos 4', 'carry': 'pos 1', 'main-support': 'pos 5',
                 'offlaner': 'pos 3'}
    url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
    response = requests.get(url)
    data = json.loads(response.text)
    url = get_map_id(data, radiant_team_name, dire_team_name)
    if url is not None:
        response = requests.get(url)
        if response.status_code == 200:
            response_html = html.unescape(response.text)
            soup = BeautifulSoup(response_html, 'lxml')
            players = soup.find_all('div', class_='team-item')
            for player in players:
                nick_name = player.find('div', class_='player-name')
                if nick_name is not None:
                    nick_name = nick_name.text.lower().replace('.', '')
                    nick_name = re.sub(r'[^\w\s\u4e00-\u9fff]+', '', nick_name)
                    position = player.find('span', class_='truncate').text.lower()
                    if nick_name in nick_fixes:
                        nick_name = nick_fixes[nick_name]
                    if position in lst:
                        result = find_in_radiant(radiant_players, nick_name, translate, position, radiant_pick, radiant_lst)
                        if result is not None:
                            radiant_lst, radiant_pick = result
                        else:
                            result = find_in_dire(dire_players, nick_name, translate, position, dire_pick, dire_lst)
                            if result is not None:
                                dire_lst, dire_pick = result


            if len(radiant_pick) == 4:
                for player in radiant_players.values():
                    hero = player['hero']
                    p_list = list(radiant_pick.values())
                    if hero not in p_list:
                        radiant_pick[translate[radiant_lst[0]]] = hero
            if len(dire_pick) == 4:
                for player in dire_players.values():
                    hero = player['hero']
                    p_list = list(dire_pick.values())
                    if hero not in p_list:
                        dire_pick[translate[dire_lst[0]]] = hero
            if len(radiant_pick) != 5:
                print(f'{radiant_team_name}\nНе удалось выяснить позиции игроков {radiant_pick}')
                send_message(f'{radiant_team_name}\nНе удалось выяснить позиции игроков {radiant_pick}')
                add_url(url)
                return None
            if len(dire_pick) != 5:
                print((f'{dire_team_name}\nНе удалось выяснить позиции игроков {dire_pick}'))
                send_message(f'{dire_team_name}\nНе удалось выяснить позиции игроков {dire_pick}')
                add_url(url)
                return None


            return radiant_pick, dire_pick, url
    else:
        return None


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


def dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name, dire_team_name, antiplagiat_url=None, core_matchup=None):
    print('dota2protracker')
    radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team = [], [], [], [] ,[], [], [], [], []
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
        index = {'pos 1': 0, 'pos 2': 2, 'pos 3': 4, 'pos 4': len(stats) - 4, 'pos 5': len(stats) - 2}
        i = index[position]
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')
            positions = ['pos 1', 'pos 2', 'pos 3', 'pos 4', 'pos 5']
            # проверить
            if data_pos.split(',')[0] in positions:
                for pos in positions:
                    if pos in data_pos and data_hero == dire_heroes_and_positions[pos]:
                        if position == 'pos 1' and pos == 'pos 1':
                            core_matchup = data_wr
                        radiant_wr_against.append(data_wr)
                try:
                    if position == 'pos 1' and data_hero == dire_heroes_and_positions[data_pos.split(',')[0]]:
                        radiant_pos1_vs_team.append(data_wr)
                    if position == 'pos 2' and data_hero == dire_heroes_and_positions[data_pos.split(',')[0]]:
                        radiant_pos2_vs_team.append(data_wr)
                    if position == 'pos 3' and data_hero == dire_heroes_and_positions[data_pos.split(',')[0]]:
                        radiant_pos3_vs_team.append(data_wr)
                except: pass

                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    dire_pos1_vs_team.append(100-data_wr)
                if 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    dire_pos2_vs_team.append(100-data_wr)
                if 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    dire_pos3_vs_team.append(100-data_wr)
    #
    if core_matchup is not None and len(dire_wr_with) >= 4 and len(radiant_wr_with) >= 4 and len(radiant_wr_against) >= 4 and len(radiant_pos1_vs_team) >= 3 and len(dire_pos1_vs_team) >= 3 and len(radiant_pos2_vs_team) >= 3 and len(dire_pos2_vs_team) >= 3 and len(radiant_pos3_vs_team) >= 3 and len(dire_pos3_vs_team) >= 3:
        core_matchup -= 50
        sinergy = (sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))
        counterpick = sum(radiant_wr_against) / len(radiant_wr_against) - 50
        pos1_vs_team = sum(radiant_pos1_vs_team) / len(radiant_pos1_vs_team) - sum(dire_pos1_vs_team) / len(
            dire_pos1_vs_team)
        pos2_vs_team = sum(radiant_pos2_vs_team) / len(radiant_pos2_vs_team) - sum(dire_pos2_vs_team) / len(dire_pos2_vs_team)
        pos3_vs_team = sum(radiant_pos3_vs_team) / len(radiant_pos3_vs_team) - sum(dire_pos3_vs_team) / len(dire_pos3_vs_team)
        try:
            sups = radiant_pos4_with_pos5 - dire_pos4_with_pos5
        except:
            sups = 0
        if sinergy > 0 and counterpick > 0 and pos1_vs_team > 0 and core_matchup > 0 and pos2_vs_team > 0 and pos3_vs_team > 0 and sups > 0:
            send_message(f'Синергия {radiant_team_name} сильнее на {sinergy}%\nCounterpick: {counterpick}\nPos1 vs team: {pos1_vs_team}\nPos2 vs team: {pos2_vs_team}\nPos3 vs team: {pos3_vs_team}\nSups: {sups}\nCore matchup: {core_matchup}')
        elif sinergy < 0 and counterpick < 0 and pos1_vs_team < 0 and core_matchup < 0 and pos2_vs_team < 0 and pos3_vs_team < 0 and sups < 0:
            send_message(f'Синергия {dire_team_name} сильнее на {sinergy*-1}%\nCounterpick: {counterpick*-1}\nPos1 vs team: {pos1_vs_team*-1}\nPos2 vs team: {pos2_vs_team*-1}\nPos3 vs team: {pos3_vs_team*-1}\nSups: {sups*-1}\nCore matchup: {core_matchup*-1}')
        else:
            send_message(f'{radiant_team_name} vs {dire_team_name}\nSinergy: {sinergy}\nCounterpick: {counterpick}\npos1_vs_team: {pos1_vs_team}\nPos2 vs team: {pos2_vs_team}\nPos3 vs team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\nПлохая ставка!!!')
    else:
        send_message(f'{radiant_team_name} vs {dire_team_name}')
        if len(radiant_pos3_vs_team) < 3:
            send_message(f'Недостаточно данных {radiant_heroes_and_positions["pos 3"]} vs {dire_heroes_and_positions}')
        if len(dire_pos3_vs_team) < 3:
            send_message(f'Недостаточно данных {dire_heroes_and_positions["pos 3"]} vs {radiant_heroes_and_positions}')
        if len(dire_pos2_vs_team) < 3:
            send_message(f'Недостаточно данных {dire_heroes_and_positions["pos 2"]} vs {radiant_heroes_and_positions}')
        if len(radiant_pos2_vs_team) < 3:
            send_message(f'Недостаточно данных {radiant_heroes_and_positions["pos 2"]} vs {dire_heroes_and_positions}')
        if len(radiant_pos1_vs_team) < 3:
            send_message(f'Недостаточно данных {radiant_heroes_and_positions["pos 1"]} vs {dire_heroes_and_positions}')
        if len(dire_pos1_vs_team) < 3:
            send_message(f'Недостаточно данных {dire_heroes_and_positions["pos 1"]} vs {radiant_heroes_and_positions}')
        if core_matchup is None:
            send_message(f'{radiant_heroes_and_positions["pos 1"]} vs {dire_heroes_and_positions["pos 1"]} нету на dota2protracker')
        if len(dire_wr_with) < 5:
            send_message(f'Недостаточная выборка винрейтов у {dire_team_name} между командой\n{dire_heroes_and_positions}')
        if len(radiant_wr_with) < 5:
            send_message(f'Недостаточная выборка винрейтов у {radiant_team_name} между командой\n{radiant_heroes_and_positions}')
        if len(radiant_wr_against) < 5:
            send_message(
                f'Недостаточная выборка винрейтов у команду между друг друга\n{radiant_heroes_and_positions}\n{dire_heroes_and_positions}')
    add_url(antiplagiat_url)



def get_map_id(data, radiant_team_name, dire_team_name):
    for match in data['rows']:
        if match['team_dire'] is not None and match['team_dire'] is not None:
            if match ['team_radiant']['name'].lower() in radiant_team_name or \
            match['team_dire']['name'].lower() in dire_team_name:
                for karta in match['related_matches']:
                    if karta['status'] != 'ended':
                        map_id = karta['id']
                        url = f'https://cyberscore.live/en/matches/{map_id}/'
                        if if_unique(url) is not None:
                            return url


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

def send_message(message):
    bot_token = f'{keys.Token}'
    chat_id = f'{keys.Chat_id}'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, json=payload)
# while True:
#     try:
#         get_live_matches()
#     except Exception as e:
#         print(e)
#         with open('errors.txt', 'r+' ) as f:
#             f.write(str(e))
#     # get_live_matches()
#     print('сплю 2 минуты')
#     time.sleep(120)
#testing
# radiant_heroes_and_positions={'pos 1': 'Troll Warlord', 'pos 2': 'Tiny', 'pos 3': 'Enigma', 'pos 4': 'Hoodwink', 'pos 5': 'Crystal Maiden'}
# dire_heroes_and_positions={'pos 1': 'Lifestealer', 'pos 2': 'Leshrac', 'pos 3': 'Brewmaster', 'pos 4': 'Batrider', 'pos 5': 'Shadow Demon'}
# dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_positions, dire_heroes_and_positions=dire_heroes_and_positions, radiant_team_name='Boom', dire_team_name='Talon')
