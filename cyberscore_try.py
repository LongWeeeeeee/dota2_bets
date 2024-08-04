import json
import time

import requests

# from test import get_maps, research_maps, explore_database
# from id_to_name import pro_teams
from dltv_cyberscore import get_team_positions, get_map_id, send_message, add_url
from trash import tm_kills, tm_kills_teams, synergy_and_counterpick_new, avg_over45, lane_report_def
from test import update_pro


def proceed_map(url, radiant_team_name, dire_team_name, score, tier, output_message=''):
    result = get_team_positions(url)
    if result is not None:
        radiant_heroes_and_pos, dire_heroes_and_pos = result
        print(f'{radiant_team_name} VS {dire_team_name}')
        radiant_lane_report = lane_report_def(my_team=radiant_heroes_and_pos, enemy_team=dire_heroes_and_pos)
        dire_lane_report = lane_report_def(my_team=dire_heroes_and_pos, enemy_team=radiant_heroes_and_pos)
        lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
        # radiant_over45 = avg_over45(radiant_heroes_and_pos)
        # dire_over45 = avg_over45(dire_heroes_and_pos)
        # over45 = (radiant_over45 - dire_over45) * 100
        avg_kills, avg_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
        avg_kills_teams, avg_time_teams = tm_kills_teams(radiant_heroes_and_pos=radiant_heroes_and_pos,
                                                         dire_heroes_and_pos=dire_heroes_and_pos,
                                                         radiant_team_name=radiant_team_name,
                                                         dire_team_name=dire_team_name)
        output_message += f'{radiant_team_name} vs {dire_team_name}\nСчет: {score}\n'
        # output_message += f'Radiant после 45 минуты сильнее на: {over45}\n'
        # output_message += f'Radiant lanes до 10 минуты: {lane_report}\n'
        output_message = synergy_and_counterpick_new(radiant_heroes_and_pos=radiant_heroes_and_pos,
                                                       dire_heroes_and_pos=dire_heroes_and_pos,
                                                 output_message=output_message)
        output_message += (
            f'\nСреднее кол-во убийств {avg_kills}\nСреднее время {avg_time}\n'
            f'Среднее кол-во убийств командное: {avg_kills_teams}\nСреднее время: {avg_time_teams}\n')
        # dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
        #                 dire_heroes_and_positions=dire_heroes_and_pos,
        #                 radiant_team_name=radiant_team_name,
        #                 dire_team_name=dire_team_name, score=score, antiplagiat_url=url, tier=tier,
        #                 output_message=output_message, lane_report=lane_report, over45=over45)
        send_message(output_message)
        add_url(url)


def general(match_list=None, radiant_team_name='radiant', dire_team_name='dire'):
    team_list = list()
    if match_list is None:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            for match in data['rows']:
                result = get_map_id(match)
                if result is not None:
                    update_pro()
                    url, radiant_team_name, dire_team_name, score, tier = result
                    proceed_map(url=url, radiant_team_name=radiant_team_name,
                                            dire_team_name=dire_team_name, score=score, tier=tier)
        else:
            print(response.status_code)
    else:
        for url in match_list:
            radiant_team_name, dire_team_name = radiant_team_name.lower(), dire_team_name.lower()
            proceed_map(url, radiant_team_name, dire_team_name, [0, 0], 1)


# def main(team_list):
#     if len(team_list) > 0:
#         team_list = [pro_teams[team]["id"] for team in team_list]
#         get_maps(maps_to_save='./pro_heroes_data/pro_maps', game_mods=[2], start_date_time=1716508800,
#                  update=team_list)
#         research_maps(maps_to_explore='pro_maps', output='pro_output', prefix='pro_heroes_data')
#         explore_database(prefix='pro_heroes_data', output='pro_output', start_date_time=1716508800,
#                          pro=True)
#     return general()

if __name__ == "__main__":
    # general(['https://cyberscore.live/en/matches/105415/'], radiant_team_name='WBG.XG', dire_team_name='Team Spirit')
    while True:
        try:
            general()
            print('Сплю 2 минуты')
            time.sleep(120)
        except Exception as e:
            send_message(e)
            print('Сплю 2 минуты')
            time.sleep(120)
