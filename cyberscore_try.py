import time
import requests
import json
from dltv_cyberscore import get_team_positions, dota2protracker,get_map_id
from trash import lane_report_def, synergy_and_counterpick, tm_kills, avg_over45
def main_try():
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
                            radiant_lane_report = lane_report_def(my_team = radiant_heroes_and_pos, enemy_team = dire_heroes_and_pos)
                            dire_lane_report = lane_report_def(my_team = dire_heroes_and_pos, enemy_team = radiant_heroes_and_pos)
                            lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
                            map_kills, map_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
                            radiant_over45 = avg_over45(radiant_heroes_and_pos)
                            dire_over45 = avg_over45(dire_heroes_and_pos)
                            over45 = (radiant_over45 - dire_over45)*100
                            output_message = (f'Radiant после 45 минуты сильнее на: {over45}\nRadiant lanes до 10 минуты: {lane_report}\n')
                            output_message = synergy_and_counterpick(radiant_heroes_and_pos, dire_heroes_and_pos,
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


def main_no_try():
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
                            radiant_lane_report = lane_report_def(my_team=radiant_heroes_and_pos,
                                                                  enemy_team=dire_heroes_and_pos)
                            dire_lane_report = lane_report_def(my_team=dire_heroes_and_pos,
                                                               enemy_team=radiant_heroes_and_pos)
                            lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
                            map_kills, map_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
                            radiant_over45 = avg_over45(radiant_heroes_and_pos)
                            dire_over45 = avg_over45(dire_heroes_and_pos)
                            over45 = (radiant_over45 - dire_over45) * 100
                            output_message = (
                                f'Radiant после 45 минуты сильнее на: {over45}\nRadiant lanes до 10 минуты: {lane_report}\n')
                            output_message = synergy_and_counterpick(radiant_heroes_and_pos, dire_heroes_and_pos,
                                                                     output_message)
                            output_message += (f'\nСреднее кол-во убийств {map_kills}, Среднее время {map_time}\n')
                            dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                                            dire_heroes_and_positions=dire_heroes_and_pos,
                                            radiant_team_name=radiant_team_name,
                                            dire_team_name=dire_team_name, score=score, antiplagiat_url=url, tier=tier,
                                            output_message=output_message, lane_report=lane_report)
            else:
                print(response.status_code)

        except Exception as e:
            print(e)
        print('Сплю 2 минуты')
        time.sleep(120)
def past_matches(match_list):
    for url in match_list:
        result = get_team_positions(url)
        if result is not None:
            radiant_heroes_and_pos, dire_heroes_and_pos = result
            radiant_lane_report = lane_report_def(my_team=radiant_heroes_and_pos, enemy_team=dire_heroes_and_pos)
            dire_lane_report = lane_report_def(my_team=dire_heroes_and_pos, enemy_team=radiant_heroes_and_pos)
            lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
            map_kills, map_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
            radiant_over45 = avg_over45(radiant_heroes_and_pos)
            dire_over45 = avg_over45(dire_heroes_and_pos)
            over45 = (radiant_over45 - dire_over45) * 100
            output_message = (f'Radiant после 45 минуты сильнее на: {over45}\nRadiant lanes до 10 минуты: {lane_report}\n')
            output_message = synergy_and_counterpick(radiant_heroes_and_pos, dire_heroes_and_pos,
                                                     output_message)
            output_message += (f'\nСреднее кол-во убийств {map_kills}, Среднее время {map_time}\n')
            dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                            dire_heroes_and_positions=dire_heroes_and_pos,
                            radiant_team_name='radiant_team_name',
                            dire_team_name='dire_team_name', score=[0,0], antiplagiat_url=url, tier=1,
                            output_message=output_message, lane_report=lane_report)
if __name__ == "__main__":
    # main_try()
    past_matches(['https://cyberscore.live/en/matches/103298/', 'https://cyberscore.live/en/matches/102760/', 'https://cyberscore.live/en/matches/103297/', 'https://cyberscore.live/en/matches/102761/', 'https://cyberscore.live/en/matches/103291/', 'https://cyberscore.live/en/matches/102755/', 'https://cyberscore.live/en/matches/103290/', 'https://cyberscore.live/en/matches/102756/', 'https://cyberscore.live/en/matches/103289/', 'https://cyberscore.live/en/matches/102753/', 'https://cyberscore.live/en/matches/103288/', 'https://cyberscore.live/en/matches/102757/', 'https://cyberscore.live/en/matches/103283/', 'https://cyberscore.live/en/matches/102750/', 'https://cyberscore.live/en/matches/103282/', 'https://cyberscore.live/en/matches/102752/', 'https://cyberscore.live/en/matches/103281/', 'https://cyberscore.live/en/matches/102749/', 'https://cyberscore.live/en/matches/103280/', 'https://cyberscore.live/en/matches/102751/', 'https://cyberscore.live/en/matches/103219/', 'https://cyberscore.live/en/matches/102746/'])