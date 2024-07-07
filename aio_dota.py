import importlib
import json
import time
import traceback
import requests

import id_to_name
from dltv_cyberscore import dota2protracker
from egb import get_players, get_picks_and_pos, get_exac_match, get_strats_graph_match, check_players_skill
from trash import analyze_players, syngery_and_counterpick, avg_over45
import time
import requests
import json
from dltv_cyberscore import get_team_positions, dota2protracker,get_map_id
from trash import analyze_players, syngery_and_counterpick, tm_kills, avg_over45

with open('heroes_data.txt', 'r') as f:
    heroes_data = json.load(f)
while True:
    try:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            for match in data['rows']:
                result = get_map_id(match)
                if result is not None:
                    url, radiant_team_name, dire_team_name, score, tier = result
                    result = get_team_positions(url)
                    if result is not None:
                        radiant_heroes_and_pos, dire_heroes_and_pos = result
                        print(f'{radiant_team_name} VS {dire_team_name}')
                        radiant_lane_report = analyze_players(my_team = radiant_heroes_and_pos, enemy_team = dire_heroes_and_pos, heroes_data =heroes_data)
                        dire_lane_report = analyze_players(my_team = dire_heroes_and_pos, enemy_team = radiant_heroes_and_pos, heroes_data = heroes_data)
                        lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
                        map_kills, map_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
                        radiant_over45 = avg_over45(radiant_heroes_and_pos, heroes_data)
                        dire_over45 = avg_over45(dire_heroes_and_pos, heroes_data)
                        over45 = (radiant_over45 - dire_over45)*100
                        output_message = (f'Radiant после 45 минуты сильнее на: {over45}\nRadiant lanes до 10 минуты: {lane_report}\n')
                        output_message = syngery_and_counterpick(radiant_heroes_and_pos, dire_heroes_and_pos,
                                                                 output_message)
                        output_message+=(f'\nСреднее кол-во убийств {map_kills}, Среднее время {map_time}\n')
                        dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                                        dire_heroes_and_positions=dire_heroes_and_pos,
                                        radiant_team_name=radiant_team_name,
                                            dire_team_name=dire_team_name, score=score, antiplagiat_url=url, tier=tier, output_message=output_message, lane_report=lane_report)
        else:
            print(response.status_code)

    except Exception as e:
        print(e)
    print('Сплю 2 минуты')
    time.sleep(120)
url = "https://egb.com/bets"
params = {
    "active": "true",
    "st": "1714418601",
    "ut": "1714418584"
}

headers = {
    "Host": "egb.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-CSRF-Token": "UUu1IL8sY0iZFFc2_FYI4ICk-WT34IRRGjz19DND8CbKEJZ9zTvbeAdcw72OYEecZiDlBaZimaYP-VuJwtmkAQ",
    "DNT": "1",
    "Sec-GPC": "1",
}
while True:
    map = False
    try:
        importlib.reload(id_to_name)
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            for bet in data['bets']:
                if bet['esports'] and bet['streams_enabled'] and bet['game'] == 'Dota 2' and bet['tourn'] in ['Incubator','Ladder Games']:
                    answer = get_players(bet)
                    if answer is not None:
                        if answer != True:
                            players_ids, dire_and_radiant = answer
                            response = get_strats_graph_match()
                            exac_match = get_exac_match(response, players_ids)
                            if exac_match is not None:
                                answer = get_picks_and_pos(match_id=exac_match['matchId'])
                                if answer is not None:
                                    if answer != True:
                                        radiant_heroes_and_pos, dire_heroes_and_pos, match_id, output_message = answer
                                        output_message, impact_diff, radiant_players_check, dire_players_check, radiant_impactandplayers, dire_impactandplayers, radiant_message_add, dire_message_add, impact_message = check_players_skill(
                                            radiant_heroes_and_pos, dire_heroes_and_pos, output_message)
                                        radiant_lane_report = analyze_players(my_team=radiant_heroes_and_pos,
                                                                              enemy_team=dire_heroes_and_pos,
                                                                              heroes_data=heroes_data)
                                        dire_lane_report = analyze_players(my_team=dire_heroes_and_pos,
                                                                           enemy_team=radiant_heroes_and_pos,
                                                                           heroes_data=heroes_data)
                                        lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
                                        radiant_over45 = avg_over45(radiant_heroes_and_pos, heroes_data)
                                        dire_over45 = avg_over45(dire_heroes_and_pos, heroes_data)
                                        over45 = (radiant_over45 - dire_over45) * 100
                                        output_message += (
                                            f'Radiant после 45 минуты сильнее на: {over45}\nRadiant lanes до 10 минуты: {lane_report}\n')
                                        output_message = syngery_and_counterpick(radiant_heroes_and_pos,
                                                                                 dire_heroes_and_pos,
                                                                                 output_message)
                                        output = ", ".join(
                                            [f"'{pos}' : '{data['hero_name']}'" for pos, data in radiant_heroes_and_pos.items()])
                                        dire_output = ", ".join(
                                            [f"'{pos}' : '{data['hero_name']}'" for pos, data in dire_heroes_and_pos.items()])
                                        print(f'Radint pick: {output}\nDire pick: {dire_output}')
                                        dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                                                        dire_heroes_and_positions=dire_heroes_and_pos,
                                                        radiant_team_name=dire_and_radiant['radiant'],
                                                        dire_team_name=dire_and_radiant['dire'], antiplagiat_url=match_id,
                                                        score=[0, 0], egb=True, output_message=output_message,
                                                        radiant_players_check=radiant_players_check, dire_players_check=dire_players_check, radiant_impactandplayers=radiant_impactandplayers, dire_impactandplayers=dire_impactandplayers, radiant_message_add=radiant_message_add, dire_message_add=dire_message_add, impact_message=impact_message)
                                    else:
                                        map = True
                            else:
                                print('карта не найдена, вероятно, матч только начался')
                                map = True
    except:
        full_traceback = traceback.format_exc()
        print(full_traceback)
        with open('error_log.txt', 'a') as f:
            f.write(full_traceback)
            f.write('\n')
    if map:
        print('сплю 30 секунд')
        time.sleep(30)
    else:
        print('сплю 3 минуты')
        time.sleep(160)