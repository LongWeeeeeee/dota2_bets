# Структура приложения: Анализ пиков + анализ игроков + анализ команды
# можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
# сверха прошлых матчей и прошлых встреч
# Отладка винрейта на старых матчах
# Проверка того что все правильно работает
# ранги неправильно работают
import html
import json
import time

import requests
from bs4 import BeautifulSoup

import keys


def get_live_matches(url='https://dltv.org/matches'):
    print("Функция выполняется...")
    live_matches_urls = get_urls(url)
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
                                            dire_team_name)


def get_urls(url):
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'lxml')
    live_matches_block = soup.find('div', class_='live__matches')
    live_matches = live_matches_block.find_all('div', class_='live__matches-item__body')
    live_matches_urls = set()
    # with open('map_id_check.txt', 'r+') as f:
    #     file = json.load(f)
    #     for match in live_matches:
    #         url = match.find('a')['href']
    #         if url not in file:
    #             file.append(url)
    #             live_matches_urls.add(url)
    #     f.truncate()
    #     f.seek(0)
    #     json.dump(file, f)
    #     return live_matches_urls
    for match in live_matches:
        url = match.find('a')['href']
        live_matches_urls.add(url)
    return live_matches_urls


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
        radiant_players[player_name] = {'hero': hero_name}
    for hero in dire_heroes_block:
        hero_name = hero.get('data-tippy-content').replace('Outworld Devourer', 'Outworld Destroyer')
        player_name = hero.find('span', class_='pick__player-title').text.lower()
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
    nick_fixes = {'griefy': 'asdekor_r', 'emptiness': 'aind', 'rincyq': 'ninamin', 'sagiri': 'kcl',
                  'somnia': 'oushaktian casedrop.com'}
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
        response = requests.get(url).text
        response_html = html.unescape(response)
        soup = BeautifulSoup(response_html, 'lxml')
        players = soup.find_all('div', class_='team-item')
        for player in players:
            nick_name = player.find('div', class_='player-name').text.lower().replace('.', '')
            position = player.find('span', class_='truncate').text.lower()
            if nick_name in nick_fixes:
                nick_name = nick_fixes[nick_name]
            if position in lst:
                for radiant_player_name in radiant_players:
                    if are_similar(radiant_player_name, nick_name, threshold=55):
                        radiant_pick[translate[position]] = radiant_players[radiant_player_name]['hero']
                        if position in radiant_lst:
                            radiant_lst.remove(position)
                            break
                        else:
                            print(f'ошибка позиции {position} не существует')
                # or radiant_player_name in nick_name or nick_name in radiant_player_name
                for dire_player_name in dire_players:
                    if are_similar(dire_player_name, nick_name, threshold=55):
                        dire_pick[translate[position]] = dire_players[dire_player_name]['hero']
                        if position in dire_lst:
                            dire_lst.remove(position)
                            break
                        else:
                            print(f'ошибка позиции {position} не существует')

        if len(radiant_pick) == 4:
            for player in radiant_players.values():
                hero = player['hero']
                if hero not in radiant_pick.values():
                    radiant_pick[translate[radiant_lst[0]]] = hero
        if len(dire_pick) == 4:
            for player in dire_players.values():
                hero = player['hero']
                if hero not in dire_players.values():
                    dire_pick[translate[dire_lst[0]]] = hero
        if len(radiant_pick) != 5:
            print(f'не удалось выяснить позиции игроков {radiant_pick}')
            return None
        if len(dire_pick) != 5:
            print(f'не удалось выяснить позиции игроков {dire_pick}')
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
            # Находим ячейку с позицией игрока
            player_position = row.find('td').find_next_sibling('td').text.strip()
            if player_position != '':
                for player_name in players:
                    if are_similar(player_name, player_nick) or player_nick in player_name:
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


def dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name, dire_team_name, core_matchup=0):
    radiant_wr_with, dire_wr_with, radiant_wr_against = [], [], []
    for position in radiant_heroes_and_positions:
        hero_url = radiant_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url)
        if response.status_code != 200:
            print(f'Ошибка dota2protracekr\n{url}')
        soup = BeautifulSoup(response.text, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        # #wr agai
        index = {'pos 1': 1, 'pos 2': 3, 'pos 3': 5, 'pos 4': 7, 'pos 5': 9}
        i = index[position]
        if len(stats) == 8:
            i -= 2
        elif len(stats) == 6:
            i -= 4
        elif len(stats) == 4:
            i -= 6
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
        index = {'pos 1': 1, 'pos 2': 3, 'pos 3': 5, 'pos 4': 7, 'pos 5': 9}
        i = index[position]
        if len(stats) == 8:
            i -= 2
        elif len(stats) == 6:
            i -= 4
        elif len(stats) == 4:
            i -= 6
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
        index = {'pos 1': 0, 'pos 2': 2, 'pos 3': 4, 'pos 4': 6, 'pos 5': 8}
        i = index[position]
        if len(stats) == 8:
            i -= 2
        elif len(stats) == 6:
            i -= 4
        elif len(stats) == 4:
            i -= 6
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')
            # positions = ['pos 1', 'pos 2', 'pos 3', 'pos 4', 'pos 5']
            # проверить
            # if position in positions:
            #     for pos in positions:
            #         if pos in data_pos and data_hero == dire_heroes_and_positions[pos]:
            #             radiant_wr_against.append(data_wr)
            #             break
            if position == 'pos 1':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    core_matchup = data_wr
                    radiant_wr_against.append(data_wr)
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)

            elif position == 'pos 2':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)

            elif position == 'pos 3':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)

            elif position == 'pos 4':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
            elif position == 'pos 5':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
    #
    core_matchup -= 50
    sinergy = (sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))
    counterpick = sum(radiant_wr_against) / len(radiant_wr_against) - 50
    if sinergy > 0 and counterpick > 0 and core_matchup >= 0:
        send_message(f'В среднем {radiant_team_name} сильнее на {(sinergy + counterpick) / 2}%')
        send_message(f'Core matchup сильнее на {core_matchup}%')
    elif sinergy < 0 and counterpick < 0 and core_matchup <= 0:
        send_message(f'В среднем {dire_team_name} сильнее на {((sinergy + counterpick) / 2) * -1}%')
        send_message(f'Core matchup сильнее на {core_matchup*-1}%')
    else:
        send_message(f'C cинергией как у {radiant_team_name} выигрывают на {sinergy} % больше ')
        send_message(f'С контрпиками как у {radiant_team_name} выигрывают на {counterpick} % больше')
        if core_matchup > 0:
            send_message(f'Radiant Core matchup сильнее на {core_matchup}%')
        elif core_matchup < 0:
            send_message(f'Dire Core matchup сильнее на {core_matchup}%')


def get_map_id(data, radiant_team_name, dire_team_name):
    for match in data['rows']:
        if match['team_dire'] is not None and match['team_dire'] is not None:
            if match ['team_radiant']['name'].lower() in radiant_team_name or \
            match['team_dire']['name'].lower() in dire_team_name:
                for karta in match['related_matches']:
                    if karta['status'] != 'ended':
                        map_id = karta['id']
                        url = f'https://cyberscore.live/en/matches/{map_id}/'
                        return url


def if_unique(url):
    with open('map_id_check.txt', 'r+') as f:
        data = json.load(f)
        if url not in data:
            data.append(url)
            f.truncate()
            f.seek(0)
            json.dump(data, f)
            return True


def send_message(message):
    bot_token = f'{keys.Token}'
    chat_id = f'{keys.Chat_id}'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    requests.post(url, json=payload)

while True:
    get_live_matches()
    time.sleep(90)