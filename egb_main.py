import id_to_name
import importlib
import json
import time
from dltv_cyberscore import dota2protracker
import requests
from egb import get_players, get_picks_and_pos, get_exac_match, get_strats_graph_match


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
                                        radiant, dire, match_id, output_message = answer
                                        print(f'Radint pick: {radiant}\nDire pick: {dire}')
                                        dota2protracker(radiant_heroes_and_positions=radiant, dire_heroes_and_positions=dire, radiant_team_name=dire_and_radiant['radiant'], dire_team_name=dire_and_radiant['dire'], antiplagiat_url=match_id, score = [0,0], egb=True, output_message=output_message)
                                    else:
                                        map = True
                            else:
                                print('карта не найдена, вероятно, матч только начался')
                                map = True
    except: pass
    if map:
        print('сплю 30 секунд')
        time.sleep(30)
    else:
        print('сплю 3 минуты')
        time.sleep(160)