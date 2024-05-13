import time
import requests
import json
import traceback
from dltv_cyberscore import get_team_positions, dota2protracker,get_map_id
while True:
    try:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            for match in data['rows']:
                result = get_map_id(match)
                if result is not None:
                    url, radiant_team_name, dire_team_name, score = result
                    result = get_team_positions(url)
                    if result is not None:
                        radiant_heroes_and_pos, dire_heroes_and_pos = result
                        print(f'{radiant_team_name} VS {dire_team_name}')
                        dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                                        dire_heroes_and_positions=dire_heroes_and_pos, radiant_team_name=radiant_team_name,
                                        dire_team_name=dire_team_name, score=score, antiplagiat_url=url)
    except: pass
    print('Сплю 2 минуты')
    time.sleep(120)