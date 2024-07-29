import time
import requests
import json
from dltv_cyberscore import get_team_positions, dota2protracker,get_map_id
from trash import lane_report_def, synergy_and_counterpick_copy, tm_kills, avg_over45
def proceed_map(url, radiant_team_name, dire_team_name, score, tier, output_message = ''):
    result = get_team_positions(url)
    if result is not None:
        radiant_heroes_and_pos, dire_heroes_and_pos = result
        print(f'{radiant_team_name} VS {dire_team_name}')
        radiant_lane_report = lane_report_def(my_team=radiant_heroes_and_pos, enemy_team=dire_heroes_and_pos)
        dire_lane_report = lane_report_def(my_team=dire_heroes_and_pos, enemy_team=radiant_heroes_and_pos)
        lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
        radiant_over45 = avg_over45(radiant_heroes_and_pos)
        dire_over45 = avg_over45(dire_heroes_and_pos)
        over45 = (radiant_over45 - dire_over45) * 100
        avg_kills, avg_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
        output_message += (f'Radiant после 45 минуты сильнее на: {over45}\nRadiant lanes до 10 минуты: {lane_report}\n')
        output_message  = synergy_and_counterpick_copy(radiant_heroes_and_pos, dire_heroes_and_pos,
                                                 output_message, over45)
        output_message += (
            f'\nСреднее кол-во убийств {avg_kills}\nСреднее время {avg_time}\n')
        dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                        dire_heroes_and_positions=dire_heroes_and_pos,
                        radiant_team_name=radiant_team_name,
                        dire_team_name=dire_team_name, score=score, antiplagiat_url=url, tier=tier,
                        output_message=output_message, lane_report=lane_report, over45=over45)
def main(match_list=None):
    if match_list is None:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            for match in data['rows']:
                result = get_map_id(match)
                if result is not None:
                    url, radiant_team_name, dire_team_name, score, tier = result
                    proceed_map(url, radiant_team_name, dire_team_name, score, tier)
        else:
            print(response.status_code)
    else:
        for url in match_list:
            proceed_map(url, 'radiant', 'dire', [0, 0], 1)




if __name__ == "__main__":
    # main(['https://cyberscore.live/en/matches/104486/'])
    # main()
    while True:
        try:
            main()
            print('Сплю 2 минуты')
            time.sleep(120)
        except:
            print('Сплю 2 минуты')
            time.sleep(120)
