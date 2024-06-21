import time
import requests
import json
import traceback
from dltv_cyberscore import get_team_positions, dota2protracker,get_map_id
from trash import analyze_players
from database import heroes_data
while True:
    # try:
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
                    radaint_team_avg_kills, radiant_team_avg_time, radiant_over35, radiant_lane_report, radiant_over40, radiant_over45,radiant_over50 ,radiant_over55 = analyze_players(radiant_heroes_and_pos, heroes_data)
                    dire_team_avg_kills, dire_team_avg_time, dire_over35, dire_lane_report, dire_over40, dire_over45,dire_over50 ,dire_over55 = analyze_players(dire_heroes_and_pos, heroes_data)
                    avg_kills = (radaint_team_avg_kills + dire_team_avg_kills) / 2
                    avg_time = (dire_team_avg_time + radiant_team_avg_time) / 2
                    diff = (radiant_over35 - dire_over35) * 100
                    diff40 = (radiant_over40 - dire_over40) * 100
                    diff45 = (radiant_over45 - dire_over45) * 100
                    diff50= (radiant_over50 - dire_over50) * 100
                    diff55 = (radiant_over55 - dire_over55) * 100
                    lane_report = (radiant_lane_report - dire_lane_report) * 100

                    print(f'Среднее количество килов: {avg_kills}\nСреднее время: {avg_time}\nРадиант выигрывает чаще после 40 минуты на: {diff}%\nRadiant выиграют линии с шансом: {lane_report}\n')
                    output_message = (
                        f'Среднее количество килов: {avg_kills}, Среднее время: {avg_time}, Радиант выигрывает чаще после 40 минуты на: {diff}%\nRadiant выиграют линии с шансом: {lane_report}\n')

                    dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                                    dire_heroes_and_positions=dire_heroes_and_pos,
                                    radiant_team_name=radiant_team_name,
                                        dire_team_name=dire_team_name, score=score, antiplagiat_url=url, tier=tier, output_message=output_message)
    # except: pass
    print('Сплю 2 минуты')
    time.sleep(120)
# url = 'https://cyberscore.live/en/matches/100534/'
# result = get_team_positions(url)
# if result is not None:
#     radiant_heroes_and_pos, dire_heroes_and_pos = result
#     radaint_team_avg_kills, radiant_team_avg_time, radiant_over35, radiant_lane_report, radiant_over40, radiant_over45, radiant_over50, radiant_over55 = analyze_players(
#         radiant_heroes_and_pos, heroes_data)
#     dire_team_avg_kills, dire_team_avg_time, dire_over35, dire_lane_report, dire_over40, dire_over45, dire_over50, dire_over55 = analyze_players(
#         dire_heroes_and_pos, heroes_data)
#     avg_kills = (radaint_team_avg_kills + dire_team_avg_kills) / 2
#     avg_time = (dire_team_avg_time + radiant_team_avg_time) / 2
#     diff35 = (radiant_over35 - dire_over35) * 100
#     diff40 = (radiant_over40 - dire_over40) * 100
#     diff45 = (radiant_over45 - dire_over45) * 100
#     diff50 = (radiant_over50 - dire_over50) * 100
#     diff55 = (radiant_over55 - dire_over55) * 100
#     lane_report = (radiant_lane_report - dire_lane_report) * 100
#
#     print(
#         f'Среднее количество килов: {avg_kills}\nСреднее время: {avg_time}\nРадиант выигрывает чаще после 40 минуты на: {diff}%\nRadiant выиграют линии с шансом: {lane_report}\n')
#     output_message = (
#         f'Среднее количество килов: {avg_kills}, Среднее время: {avg_time}, Радиант выигрывает чаще после 40 минуты на: {diff}%\nRadiant выиграют линии с шансом: {lane_report}\n')
#
#     dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
#                     dire_heroes_and_positions=dire_heroes_and_pos,
#                     radiant_team_name='radiant',
#                     dire_team_name='radiant', score=[0, 0], antiplagiat_url=url, tier=1,
#                     output_message=output_message)

