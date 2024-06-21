import importlib
import json
import time
import traceback
import requests

import id_to_name
from dltv_cyberscore import dota2protracker
from egb import get_players, get_picks_and_pos, get_exac_match, get_strats_graph_match, check_players_skill

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
                                        radiant, dire, match_id, output_message, R_pos_strng, D_pos_strng = answer
                                        output_message, impact_diff, R_pos_strng, D_pos_strng, radiant_players_check, dire_players_check, radiant_impactandplayers, dire_impactandplayers = check_players_skill(
                                            radiant, dire, output_message, R_pos_strng, D_pos_strng)
                                        output = ", ".join(
                                            [f"'{pos}' : '{data['hero_name']}'" for pos, data in radiant.items()])
                                        dire_output = ", ".join(
                                            [f"'{pos}' : '{data['hero_name']}'" for pos, data in dire.items()])
                                        print(f'Radint pick: {output}\nDire pick: {dire_output}')
                                        dota2protracker(radiant_heroes_and_positions=radiant,
                                                        dire_heroes_and_positions=dire,
                                                        radiant_team_name=dire_and_radiant['radiant'],
                                                        dire_team_name=dire_and_radiant['dire'], antiplagiat_url=match_id,
                                                        score=[0, 0], egb=True, output_message=output_message,
                                                        radiant_players_check=radiant_players_check, dire_players_check=dire_players_check, radiant_impactandplayers=radiant_impactandplayers, dire_impactandplayers=dire_impactandplayers)
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