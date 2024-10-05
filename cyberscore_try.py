import json
import time
import requests
import traceback

from fuckkk import dota2protracker_gpt
from functions import get_team_positions, tm_kills_teams, tm_kills, send_message, add_url, get_map_id, \
    calculate_over45, calculate_lanes, synergy_and_counterpick_new
from maps_research import update_all_teams, update_pro, update_my_protracker


def general(match_list=None, radiant_team_name='radiant', dire_team_name='dire', tier=None):
    if match_list is None:
        url = 'https://api.cyberscore.live/api/v1/matches/?limit=20&type=liveOrUpcoming&locale=en'
        response = requests.get(url)
        data = json.loads(response.text)
        for match in data['rows']:
            result = get_map_id(match)
            if result is not None:
                url, radiant_team_name, dire_team_name, score, tier = result
                proceed_map(url=url, radiant_team_name=radiant_team_name,
                            dire_team_name=dire_team_name, score=score, tier=tier)
    else:
        for url in match_list:
            radiant_team_name, dire_team_name = radiant_team_name.lower(), dire_team_name.lower()
            proceed_map(url, radiant_team_name, dire_team_name, [0, 0], tier)



def proceed_map(url, radiant_team_name, dire_team_name, score, tier, output_message=''):
    result = get_team_positions(url)
    if result is not None:
        radiant_heroes_and_pos, dire_heroes_and_pos = result
        output_message += f'{radiant_team_name} VS {dire_team_name}\nСчет: {score}\n{url}\n'
        print(f'{radiant_team_name} VS {dire_team_name}\nСчет: {score}\n')
        # output_message += calculate_over45(radiant_heroes_and_pos, dire_heroes_and_pos)
        # output_message += calculate_lanes(radiant_heroes_and_pos, dire_heroes_and_pos)
        # output_message += synergy_and_counterpick_new(
        #     radiant_heroes_and_pos=radiant_heroes_and_pos,
        #     dire_heroes_and_pos=dire_heroes_and_pos)
        
        output_message += dota2protracker_gpt(
            radiant_heroes_and_positions=radiant_heroes_and_pos,
            dire_heroes_and_positions=dire_heroes_and_pos)
        # result = None
        # try:
            # if score in [[0, 0], [1, 1]]:
            #     update_pro(show_prints=True)
            #     update_all_teams(show_prints=True)
        #     result = tm_kills_teams(radiant_heroes_and_pos=radiant_heroes_and_pos,
        #                             dire_heroes_and_pos=dire_heroes_and_pos,
        #                             radiant_team_name=radiant_team_name,
        #                             dire_team_name=dire_team_name, min_len=2)
        # except TypeError:
        #     try:
        #         result = tm_kills_teams(radiant_heroes_and_pos=radiant_heroes_and_pos,
        #                                 dire_heroes_and_pos=dire_heroes_and_pos,
        #                                 radiant_team_name=radiant_team_name,
        #                                 dire_team_name=dire_team_name, min_len=1)
        #
        #     except TypeError:
        #         if tier == 3:
        #             avg_kills, avg_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
        #             output_message += (
        #                 f'\nСреднее кол-во убийств: {avg_kills}\nСреднее время: {avg_time}'
        #                 f'\nОпасная ставка на время!')
        #         else:
        #             print('не удалось выяснить кол-во килов у команд')
        # if result is not None:
        #     avg_kills_teams, avg_time_teams = result
        #     if tier == 1:
        #         avg_kills, avg_time = tm_kills(radiant_heroes_and_pos, dire_heroes_and_pos)
        #         output_message += (
        #             f'\nСреднее кол-во убийств: {(avg_kills + avg_kills_teams) / 2}\n'
        #             f'Командное: {avg_kills_teams}\nОбщее: {avg_kills}')
        #     else:
        #         output_message += (
        #             f'\nСреднее кол-во убийств: {avg_kills_teams}\n'
        #             f'Среднее время: {avg_time_teams}\n')
        send_message(output_message)
        # add_url(url)


if __name__ == "__main__":
    # update_pro(show_prints=True)
    # update_all_teams(show_prints=True)
    update_my_protracker(show_prints=True)
    # update_all_teams(show_prints=True, only_in_ids=['BetBoom Team', 'Team Liquid'])
    # general(['https://cyberscore.live/en/matches/109941/'], radiant_team_name='Aurora Gaming', dire_team_name='Beastcoast', tier=1)
    # while True:
    #     try:
    #         general()
    #     except:
    #         error_traceback = traceback.format_exc()
    #         print(error_traceback)
    #         time.sleep(180)
    #     print('Сплю 3 минуты')
    #     time.sleep(180)
