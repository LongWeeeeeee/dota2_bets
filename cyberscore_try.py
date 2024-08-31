import requests
import traceback
from functions import get_team_positions,tm_kills_teams, tm_kills, send_message, add_url, get_map_id,\
    lane_report_def, avg_over35, dota2protracker, synergy_and_counterpick_new
from maps_research import update_pro, update_my_protracker, update_all_teams
import time
import json

def proceed_map(url, radiant_team_name, dire_team_name, score, tier, output_message=''):
    result = get_team_positions(url)
    if result is not None:
        radiant_heroes_and_pos, dire_heroes_and_pos = result
        output_message += (f'{radiant_team_name} VS {dire_team_name}\nСчет: {score}\n{url}\n')
        print(f'{radiant_team_name} VS {dire_team_name}\nСчет: {score}\n')
        try:
            radiant_lane_report = lane_report_def(my_team=radiant_heroes_and_pos, enemy_team=dire_heroes_and_pos)
            dire_lane_report = lane_report_def(my_team=dire_heroes_and_pos, enemy_team=radiant_heroes_and_pos)
            lane_report = round(((radiant_lane_report - dire_lane_report) * 100), 2)
            radiant_over35 = avg_over35(radiant_heroes_and_pos)
            dire_over35 = avg_over35(dire_heroes_and_pos)
            if radiant_over35 is not None and dire_over35 is not None:
                over35 = (radiant_over35 - dire_over35) * 100
                output_message += f'Radiant после 35 минуты сильнее на: {over35}\n'
            output_message += f'Radiant lanes до 10 минуты: {lane_report}\n'

            output_message += synergy_and_counterpick_new(radiant_heroes_and_pos=radiant_heroes_and_pos,
                                                 dire_heroes_and_pos=dire_heroes_and_pos,
                                                 output_message=output_message)
        except:
            error_traceback = traceback.format_exc()
            print(error_traceback)
        output_message += dota2protracker(radiant_heroes_and_positions=radiant_heroes_and_pos,
                                          dire_heroes_and_positions=dire_heroes_and_pos,
                                          output_message=output_message)
        result = None
        try:
            update_all_teams(show_prints=True, team_names=[radiant_team_name, dire_team_name])
            result = tm_kills_teams(radiant_heroes_and_pos=radiant_heroes_and_pos,
                                    dire_heroes_and_pos=dire_heroes_and_pos,
                                    radiant_team_name=radiant_team_name,
                                    dire_team_name=dire_team_name, min_len=2)
        except TypeError:
            try:
                result = tm_kills_teams(radiant_heroes_and_pos=radiant_heroes_and_pos,
                                    dire_heroes_and_pos=dire_heroes_and_pos,
                                    radiant_team_name=radiant_team_name,
                                    dire_team_name=dire_team_name, min_len=1)

            except TypeError:
                if tier == 1:
                    avg_kills, avg_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
                    output_message += (
                        f'\nСреднее кол-во убийств: {(avg_kills)}\nСреднее время: {(avg_time)}'
                        f'\nОпасная ставка на время!')
                else:
                    print('не удалось выяснить кол-во килов у команд')
            except:
                error_traceback = traceback.format_exc()
                print(error_traceback)
        except:
            error_traceback = traceback.format_exc()
            print(error_traceback)
        if result is not None:
            avg_kills_teams, avg_time_teams = result
            if tier == 1:
                avg_kills, avg_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
                output_message += (
                    f'\nСреднее кол-во убийств: {(avg_kills+avg_kills_teams)/2}\n'
                    f'Среднее время: {(avg_time+avg_time_teams)/2}\n')
            else:
                output_message += (
                    f'\nСреднее кол-во убийств: {(avg_kills_teams)}\n'
                    f'Среднее время: {(avg_time_teams)}\n')
        send_message(output_message)
        add_url(url)


def general(match_list=None, radiant_team_name='radiant', dire_team_name='dire', tier=None):
    if match_list is None:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
        try:
            response = requests.get(url)
            data = json.loads(response.text)
            for match in data['rows']:
                result = get_map_id(match)
                if result is not None:
                    url, radiant_team_name, dire_team_name, score, tier = result
                    proceed_map(url=url, radiant_team_name=radiant_team_name,
                                            dire_team_name=dire_team_name, score=score, tier=tier)
        except:
            error_traceback = traceback.format_exc()
            print(error_traceback)
    else:
        for url in match_list:
            radiant_team_name, dire_team_name = radiant_team_name.lower(), dire_team_name.lower()
            proceed_map(url, radiant_team_name, dire_team_name, [0, 0], tier)


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
    # update_pro(show_prints=True)
    # update_my_protracker(show_prints=True)
    # update_all_teams(show_prints=True)
    # update_all_teams(show_prints=True, team_names=['fusion esports', 'south team'])
    general(['https://cyberscore.live/en/matches/108656/'], radiant_team_name='avulus', dire_team_name='1win', tier=2)
    # while True:
    #     try:
    #         general()
    #     except:
    #         error_traceback = traceback.format_exc()
    #         print(error_traceback)
    #         time.sleep(180)
    #     print('Сплю 3 минуты')
    #     time.sleep(180)
