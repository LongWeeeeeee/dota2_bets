# Структура приложения: Анализ пиков + анализ игроков + анализ команды
#можно также попробовать собирать другую статистику такую как продолжительность матча и все такое
#сверха прошлых матчей и прошлых встреч
#Отладка винрейта на старых матчах
#Проверка того что все правильно работает
#ранги неправильно работают
import requests
from bs4 import BeautifulSoup
import json

import keys


def get_live_matches():
    print("Функция выполняется...")
    url = 'https://dltv.org/matches'
    live_matches_urls = get_urls(url)
    for url in live_matches_urls:
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        radiant_block = soup.find('div', class_='picks__new-picks__picks radiant')
        if radiant_block is not None:
            items = radiant_block.find('div', class_='items')
            # Проверяем, не скрыт ли элемент и содержит ли он другие элементы
            if items and items.get('style') != 'display: none;' and len(items.find_all('div', class_='pick')) > 0:
                radiant_players, dire_players = get_player_names_and_heroes(radiant_block, soup)
                radiant_team_name, dire_team_name = get_team_names(soup)
                print(f'{radiant_team_name} VS {dire_team_name}')
                result = get_team_positions(radiant_team_name, dire_team_name, radiant_players, dire_players)
                if result is not None:
                    radiant_heroes_and_positions, dire_heroes_and_positions = result
                    dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name, dire_team_name)

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
        if team_info[1].replace(' ', '') == 'Radiant':
            radiant_team_name = team_info[0]
        else:
            dire_team_name = team_info[0]
    return radiant_team_name.lower(), dire_team_name.lower()
def get_player_names_and_heroes(radiant_block, soup):
    radiant_players, dire_players = {}, {}
    radiant_heroes_block = radiant_block.find_all('div', class_='pick player')
    dire_block = soup.find('div', class_='picks__new-picks__picks dire')
    dire_heroes_block = dire_block.find_all('div', class_='pick player')
    for hero in radiant_heroes_block[0:5]:
        hero_name = hero.get('data-tippy-content')
        player_name = hero.find('span', class_='pick__player-title').text.lower()
        radiant_players[player_name] = {'hero': hero_name}
    for hero in dire_heroes_block:
        hero_name = hero.get('data-tippy-content')
        player_name = hero.find('span', class_='pick__player-title').text.lower()
        dire_players[player_name] = {'hero': hero_name}
    return radiant_players, dire_players


def get_team_ids(radiant_team_name, dire_team_name):
    url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
    response = requests.get(url).text
    matches = json.loads(response)
    for match in matches['rows']:
        if match['team_radiant']['name'].lower() in radiant_team_name.lower() or match['team_dire']['name'].lower() in dire_team_name.lower():
            radiant_team_id = match['team_radiant']['id']
            dire_team_id = match['team_dire']['id']
            return radiant_team_id, dire_team_id


def get_team_positions(radiant_team_name, dire_team_name, radiant_players, dire_players):
    fix_names = {'entity gaming': 'enity', '9 pandas': 'pandas'}
    main_url = 'https://dota2.ru/esport/team/get_list_by_filter/'
    for current_team in [radiant_team_name.lower(), dire_team_name.lower()]:
        if current_team in fix_names:
            current_team = fix_names[current_team]
        # The data you want to send in the POST request
        data = {
            f'team': f"{current_team}",
            'region': '0',
            'sort': ''  # It looks like you want to include a 'sort' parameter, but haven't specified a value.
        }

        # The headers you want to include with your request
        headers = {
            'Host': 'dota2.ru',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://dota2.ru',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://dota2.ru/esport/teams/',
        }

        # Sending the POST request
        response = requests.post(main_url, data=data, headers=headers)
        json_response = json.loads(response.text)
        soup = BeautifulSoup(json_response['data']['list'], 'lxml')
        team_url = soup.find('a')
        if team_url is not None:
            url_name = 'https://dota2.ru' + team_url['href']
            response = requests.get(url_name)
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')[1:]  # Пропускаем заголовок
            if current_team == radiant_team_name:
                players = radiant_players
                radiant_players = fill_players_position(rows, players)
                if radiant_players is None:
                    return None
            else:
                players = dire_players
                dire_players = fill_players_position(rows, players)
                if dire_players is None:
                    return None
        else:
            print(f'{current_team} нету на https://dota2.ru/esport/teams/')
            return None
    return radiant_players, dire_players
def fill_players_position(rows, players):
    heroes_and_position = {}
    lst = ['Мидер', 'Сапорт 4', 'Керри', 'Сапорт 5', 'Оффлейнер']
    translate = {'Мидер':'pos 2', 'Сапорт 4': 'pos 4', 'Керри': 'pos 1', 'Сапорт 5': 'pos 5', 'Оффлейнер': 'pos 3'}
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


def dota2protracker(radiant_heroes_and_positions, dire_heroes_and_positions, radiant_team_name, dire_team_name):
    radiant_wr_with, dire_wr_with, radiant_wr_against = [], [], []
    
    for position in radiant_heroes_and_positions:
        hero_url = radiant_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        # #wr against
        # index = {'Керри': 0, 'Мидер': 2, 'Оффлейнер': 4, 'Сапорт 4': 6, 'Сапорт 5': 8}
        # hero_divs = stats[index[position]].find_all('div', attrs={'data-hero': True})
        # for div in hero_divs:
        #     # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
        #     data_hero = div.get('data-hero')
        #     data_wr = div.get('data-wr')
        #     data_pos = div.get('data-pos')
        # wr with
        index = {'pos 1': 1, 'pos 2': 3, 'pos 3': 5, 'pos 4': 7, 'pos 5': 9}
        i = index[position]
        if len(stats) == 8:
            i -= 2
        elif len(stats) == 6:
            i -= 4
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')
            if position == 'pos 1':
                if 'pos 2' in data_pos and data_hero == radiant_heroes_and_positions['pos 2']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos1_with_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == radiant_heroes_and_positions['pos 3']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos1_with_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos1_with_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos1_with_pos5 = data_wr

            if position == 'pos 2':
                if 'pos 3' in data_pos and data_hero == radiant_heroes_and_positions['pos 3']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos2_with_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos2_with_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos2_with_pos5 = data_wr

            if position == 'pos 3':
                if 'pos 4' in data_pos and data_hero == radiant_heroes_and_positions['pos 4']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos3_with_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos3_with_pos5 = data_wr

            if position == 'pos 4':
                if 'pos 5' in data_pos and data_hero == radiant_heroes_and_positions['pos 5']:
                    radiant_wr_with.append(data_wr)
                    Radiant_Pos4_with_pos5 = data_wr
    for position in dire_heroes_and_positions:
        hero_url = dire_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        index = {'pos 1': 1, 'pos 2': 3, 'pos 3': 5, 'pos 4': 7, 'pos 5': 9}
        i = index[position]
        if len(stats) == 8:
            i -= 2
        elif len(stats) == 6:
            i -= 4
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')

            if position == 'pos 1':
                if 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    dire_Pos1_with_pos2 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    dire_Pos1_with_pos3 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    dire_Pos1_with_pos4 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_Pos1_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)

            if position == 'pos 2':
                if 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    dire_Pos2_with_pos3 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    dire_Pos2_with_pos4 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_Pos2_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)

            if position == 'pos 3':
                if 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    dire_Pos3_with_pos4 = data_wr
                    dire_wr_with.append(data_wr)
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_Pos3_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)

            if position == 'pos 4':
                if 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    dire_Pos4_with_pos5 = data_wr
                    dire_wr_with.append(data_wr)
    for position in radiant_heroes_and_positions:
        hero_url = radiant_heroes_and_positions[position].replace(' ', '%20')
        url = f'https://dota2protracker.com/hero/{hero_url}/new'
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        stats = soup.find_all('div', class_='overflow-y-scroll tbody h-96')
        # #wr against
        index = {'pos 1': 0, 'pos 2': 2, 'pos 3': 4, 'pos 4': 6, 'pos 5': 8}
        i = index[position]
        if len(stats) == 8:
            i -= 2
        elif len(stats) == 6:
            i -= 4
        hero_divs = stats[i].find_all('div', attrs={'data-hero': True})
        for div in hero_divs:
            # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
            data_hero = div.get('data-hero')
            data_wr = int(float(div.get('data-wr')))
            data_pos = div.get('data-pos')
            if position == 'pos 1':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos1_vs_Dire_pos1 = data_wr
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos1_vs_Dire_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos1_vs_Dire_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos1_vs_Dire_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos1_vs_Dire_pos5 = data_wr

            elif position == 'pos 2':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos2_vs_Dire_pos1 = data_wr
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos2_vs_Dire_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos2_vs_Dire_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos2_vs_Dire_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos2_vs_Dire_pos5 = data_wr

            elif position == 'pos 3':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos3_vs_Dire_pos1 = data_wr
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos3_vs_Dire_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos3_vs_Dire_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos3_vs_Dire_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos3_vs_Dire_pos5 = data_wr

            elif position == 'pos 4':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos4_vs_Dire_pos1 = data_wr
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos4_vs_Dire_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos4_vs_Dire_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos4_vs_Dire_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos4_vs_Dire_pos5 = data_wr
            elif position == 'pos 5':
                if 'pos 1' in data_pos and data_hero == dire_heroes_and_positions['pos 1']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos5_vs_Dire_pos1 = data_wr
                elif 'pos 2' in data_pos and data_hero == dire_heroes_and_positions['pos 2']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos5_vs_Dire_pos2 = data_wr
                elif 'pos 3' in data_pos and data_hero == dire_heroes_and_positions['pos 3']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos5_vs_Dire_pos3 = data_wr
                elif 'pos 4' in data_pos and data_hero == dire_heroes_and_positions['pos 4']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos5_vs_Dire_pos4 = data_wr
                elif 'pos 5' in data_pos and data_hero == dire_heroes_and_positions['pos 5']:
                    radiant_wr_against.append(data_wr)
                    Radiant_Pos5_vs_Dire_pos5 = data_wr

    if len(radiant_wr_with) == len(dire_wr_with):
        print(f'C cинергией как у {radiant_team_name} выигрывают на {sum(radiant_wr_with)/len(dire_wr_with) - sum(dire_wr_with)/len(dire_wr_with)} % больше ')
    else:
        print('Ошибка синергий, вероятно пикнуто что-то экстроординарное')
        print(f'{radiant_team_name}\n{radiant_heroes_and_positions}\n{dire_team_name}\n{dire_heroes_and_positions}')
    print(f'С контрпиками как у {radiant_team_name} выигрывают на {sum(radiant_wr_against)/len(radiant_wr_against) - 50} % больше')





def send_message(message):
    BOT_TOKEN = f'{keys.Token}'
    CHAT_ID = f'{keys.Chat_id}'
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    requests.post(url, json=payload)


get_live_matches()