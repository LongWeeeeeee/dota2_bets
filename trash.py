# from id_to_name import egb
import requests
from keys import api_token, api_token_2
# import time
from dltv_cyberscore import analyze_draft, clean_up
from id_to_name import top_500_asia_europe, non_anon_top_1000_europe_top_1000_asia, pro_teams, translate, output_data
import json
import os
import time
import shutil

radiant_position_to_lane ={
        'pos1': 'bottomLaneOutcome',
        'pos2': 'midLaneOutcome',
        'pos3': 'topLaneOutcome',
        'pos4': 'topLaneOutcome',
        'pos5': 'bottomLaneOutcome'
    }
dire_position_to_lane ={
    'pos1': 'topLaneOutcome',
    'pos2': 'midLaneOutcome',
    'pos3': 'bottomLaneOutcome',
    'pos4': 'bottomLaneOutcome',
    'pos5': 'topLaneOutcome'
}


def distribute_heroes_data(hero_id, position, to_be_appended, path, heroes_data):
    # Определяем индекс массива на основе hero_id
    current_dict = heroes_data.setdefault('value', {}).setdefault(hero_id, {}).setdefault(position, {})
    for key in path[:-1]:
        current_dict = current_dict.setdefault(key, {})
        # Обрабатываем последний ключ, добавляя к списку нужное значение
    current_dict.setdefault(path[-1], []).append(to_be_appended)
    return heroes_data


def proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count, pro_query=None, check=True, skip= 0):
    try:
        while check:
            if pro_query is None:
                query = '''
                                    {players(steamAccountIds:%s){
                                      steamAccountId
                                      matches(request:{startDateTime:%s, take:100, skip:%s, gameModeIds:%s}){
                                        id
                                      }
                                    }
                                    }
                                    ''' % (ids_to_graph, start_date_time, skip, game_mods)
            else:
                query = pro_query
            headers = {"Authorization": f"Bearer {api_token}"}
            response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
            data = json.loads(response.text)
            if pro_query is None:
                if any(player['matches'] != [] for player in data['data']['players']):
                    for player in data['data']['players']:
                        for map_id in player['matches']:
                            if map_id['id'] not in file_data:
                                file_data.append(map_id['id'])
                    skip += 100
                else:
                    ids_to_graph = []
                    check = False
            else:
                check = False
                for team in data['data']['teams']:
                    for match in team['matches']:
                        if match['id'] not in file_data:
                            radiant_team_name = match['radiantTeam']['name'].lower()
                            dire_team_name = match['direTeam']['name'].lower()
                            if radiant_team_name in pro_teams and dire_team_name in pro_teams:
                                file_data.append(match['id'])
    except Exception as e:
        print(f"Error {e}")
        time.sleep(5)
    count += 1
    return file_data



def get_maps(game_mods, start_date_time, players_dict, maps_to_save):
    file_data = []
    ids_to_graph, total_map_ids = [], []
    count = 0
    if game_mods == [2]:
        unique = set()
        for team_name in pro_teams:
            count+=1
            print(f'{count}/{len(pro_teams)}')
            steam_id = pro_teams[team_name]['id']
            if len(ids_to_graph) != 5:
                if steam_id not in unique:
                    ids_to_graph.append(steam_id)
                unique.add(steam_id)
            else:
                pro_query = '''
                            {teams(teamIds: %s){
                              matches(request:{startDateTime:%s, take:100, skip: 0}){
                                id
                                radiantTeam{
                                          name
                                          id
                                        }
                                        direTeam{
                                          name
                                          id
                                        }
                              }
                            }}''' % (ids_to_graph, start_date_time)
                file_data = proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count, pro_query)
                ids_to_graph = [steam_id]
    else:
        for steam_id in players_dict:
            count += 1
            print(f'{count}/{len(players_dict)}')
            if len(ids_to_graph) != 5:
                ids_to_graph.append(steam_id)
                if count == len(players_dict):
                    proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count)
            else:
                proceed_get_maps(ids_to_graph, start_date_time, game_mods, file_data, count)
                ids_to_graph = [steam_id]
    with open(f'{maps_to_save}.txt', 'w') as f:
        f.truncate()
        f.seek(0)
        json.dump(file_data, f)


def eat_temp_files(prefix, file_data, output):
    folder_path = f"./{prefix}/temp_files"
    if os.path.exists(folder_path):
        try:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'r+') as f:
                    data = json.load(f)
                    for map in data:
                        if map not in file_data:
                            file_data[map] = data[map]
        except:pass
        with open(f'./{prefix}/{output}.txt', 'w') as f:
            f.truncate()
            f.seek(0)
            json.dump(file_data, f)
        shutil.rmtree(f'./{prefix}/temp_files')



def research_map_proceed(maps_to_explore, file_data, output, prefix, counter =0, another_counter = 0, error_counter=0):
    token = api_token_2
    eat_temp_files(prefix, file_data, output)
    for map_id in maps_to_explore:
        counter += 1
        print(f'{counter}/{len(maps_to_explore)}')
        if error_counter >= 1:
            if token != api_token_2:
                token = api_token_2
            else:
                token = api_token
            error_counter = 0
        if str(map_id) not in file_data:
            another_counter +=1
            if another_counter % 300 == 0:
                if not os.path.isdir(f"./{prefix}/temp_files"):
                    os.mkdir(f"./{prefix}/temp_files")
                another_counter += 1
                path = f'./{prefix}/temp_files/{another_counter}.txt'
                if os.path.isfile(path):
                    while os.path.isfile(path):
                        another_counter += 1
                with open(path, 'w') as f:
                    f.truncate()
                    f.seek(0)
                    json.dump(file_data, f)
            try:
                query = '''
                {match(id:%s){
                  startDateTime
                  league{
                    id
                    tier
                    region
                    basePrizePool
                    prizePool
                    tournamentUrl
                    displayName
                  }
                  direTeam{
                    id
                    name
                  }
                  radiantTeam{
                    id
                    name
                  }
                  id
                  direKills
                  radiantKills
                  bottomLaneOutcome
                  topLaneOutcome
                  midLaneOutcome
                  radiantNetworthLeads
                  didRadiantWin
                  durationSeconds
                  players{
                    steamAccount{
                      id
                      isAnonymous
                    }
                    imp
                    position
                    isRadiant
                    hero{
                      id
                    }
                  }
                }
                }''' % map_id
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
                data = json.loads(response.text)['data']['match']
                file_data[map_id] = data
            except Exception as e:
                error_counter += 1
                print(f"Error processing map ID {map_id}: {e}")
    eat_temp_files(prefix, file_data, output)
    with open(f'./{prefix}/{output}.txt', 'r+') as f:
        f.truncate()
        f.seek(0)
        json.dump(file_data, f)



def research_maps(maps_to_explore, output, prefix):
    path = f'./{prefix}/{maps_to_explore}.txt'
    with open(path, 'r+') as f:
        maps_to_explore = set(json.load(f))
    try:
        with open(f'./{prefix}/{output}.txt', 'r+') as f:
            file_data = json.load(f)
    except (FileNotFoundError, FileExistsError):
        with open(f'./{prefix}/{output}.txt', 'w') as f:
            file_data = {}

    research_map_proceed(maps_to_explore, file_data, output, prefix)
    # except (FileExistsError, FileNotFoundError):
        # with open(f'./{prefix}/{output}.txt', 'w') as f:
        #     file_data = {}
    research_map_proceed(maps_to_explore, file_data, output, prefix)







def lane_with_hero(player, position, match, hero_id, another_player_position, another_player_hero_id, isradiant, another_isradiant, lane_dict):

    return lane_dict


def proceed_map(match, map_id, players_imp_data, used_maps, lane_dict, synergy_and_counterpick_dict, total_time_kills_dict, over45_dict):
    for player in match['players']:
        radiant_win = match['didRadiantWin']
        position = player['position'].replace('POSITION_', 'pos')
        hero_id = str(player['hero']['id'])
        isradiant = player['isRadiant']
        steam_id = str(player['steamAccount']['id'])
        if map_id not in players_imp_data['used_maps']:
            if (player['steamAccount']['isAnonymous']):
                players_imp_data.setdefault('value', {}).setdefault(steam_id, {}).setdefault(hero_id, {}).setdefault(position, []).append(
                    player['imp'])
                players_imp_data.setdefault('used_maps', []).append(map_id)
        if map_id not in used_maps:
            if isradiant:
                if radiant_win:
                    to_be_appended = 1
                else:
                    to_be_appended = 0
            else:
                if radiant_win:
                    to_be_appended = 0
                else:
                    to_be_appended = 1
            synergy_and_counterpick_dict.setdefault('value', {}).setdefault(hero_id, {}).setdefault(position, {}).setdefault('winrate', []).append(to_be_appended)
            # time, kills, and other shit

            if player['isRadiant'] is True:
                outcome = match[radiant_position_to_lane[position]]
                if 'RADIANT' in outcome:
                    to_be_appended = 1
                elif 'DIRE' in outcome:
                    to_be_appended = 0
                else:
                    #ничья
                    to_be_appended = 2
            else:
                outcome = match[dire_position_to_lane[position]]
                if 'RADIANT' in outcome:
                    to_be_appended = 0
                elif 'DIRE' in outcome:
                    to_be_appended = 1
                else:
                    #ничья
                    to_be_appended = 2
            lane_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                               ['lane_report', 'solo', 'value'],
                                               lane_dict)

            for another_player in match['players']:
                another_player_hero_id = str(another_player['hero']['id'])
                if another_player_hero_id != hero_id:
                    another_player_position = another_player['position'].replace('POSITION_', 'pos')
                    another_isradiant = another_player['isRadiant']
                    #lane
                    if player['isRadiant'] is True:
                        if 'RADIANT' in outcome:
                            to_be_appended = 1
                        elif 'DIRE' in outcome:
                            to_be_appended = 0
                        else:
                            to_be_appended = 2
                    else:
                        if 'RADIANT' in outcome:
                            to_be_appended = 0
                        elif 'DIRE' in outcome:
                            to_be_appended = 1
                        else:
                            to_be_appended = 2
                    if ((position in ['pos5', 'pos1']) and (another_player_position in ['pos1', 'pos5']) or (
                            position in ['pos3', 'pos4']) and (
                                another_player_position in ['pos3', 'pos4'])) and (isradiant == another_isradiant) and (
                            position != another_player_position):
                        lane_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                           ['lane_report', 'with_hero', another_player_hero_id,
                                                            another_player_position], lane_dict)

                    elif (position == 'pos2') and (another_player_position == 'pos2') and (
                            hero_id != another_player_hero_id):
                        lane_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                           ['lane_report', 'against_hero', another_player_hero_id],
                                                           lane_dict)
                    # counterpick
                    if isradiant:
                        if radiant_win:
                            to_be_appended = 1
                        else:
                            to_be_appended = 0
                    else:
                        if radiant_win:
                            to_be_appended = 0
                        else:
                            to_be_appended = 1
                    if isradiant != another_player['isRadiant']:
                        synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                               ['counterpick_duo',
                                                                                another_player_hero_id,
                                                                                another_player_position, 'value'],
                                                                               synergy_and_counterpick_dict)
                    # synergy
                    if (isradiant == another_player['isRadiant']) and (hero_id != another_player_hero_id):
                        synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position,
                                                                               to_be_appended,
                                                                               ['synergy_duo',
                                                                                another_player_hero_id,
                                                                                another_player_position,
                                                                                'value'],
                                                                               synergy_and_counterpick_dict)

                        total_kills = sum(match['direKills']) + sum(match['radiantKills'])
                        if match['durationSeconds'] / 60 > 45:
                            over45_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                 ['over45_duo', another_player_hero_id,
                                                                  another_player_position, 'value'], over45_dict)
                        total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                       ['total_kills_duo', another_player_hero_id,
                                                                        another_player_position, 'value'],
                                                                       total_time_kills_dict)

                        total_time_kills_dict = distribute_heroes_data(hero_id, position, match['durationSeconds'],
                                                                       ['total_time_duo', another_player_hero_id,
                                                                        another_player_position, 'value'],
                                                                       total_time_kills_dict)

                        for third_player in match['players']:
                            third_player_hero_id = str(third_player['hero']['id'])
                            third_player_position = third_player['position'].replace('POSITION_', 'pos')
                            third_isradiant = third_player['isRadiant']
                            if (isradiant == third_isradiant) and (
                                    third_player_hero_id not in [hero_id, another_player_hero_id]):
                                if match['durationSeconds'] / 60 > 45:
                                    over45_dict = distribute_heroes_data(hero_id, position, to_be_appended,
                                                                         ['over45_duo', another_player_hero_id,
                                                                          another_player_position, 'over45_trio',
                                                                          third_player_hero_id, third_player_position,
                                                                          'value'], over45_dict)
                                synergy_and_counterpick_dict = distribute_heroes_data(hero_id, position,
                                                                                       to_be_appended,
                                                                                       ['synergy_duo',
                                                                                        another_player_hero_id,
                                                                                        another_player_position,
                                                                                        'synergy_trio',
                                                                                        third_player_hero_id,
                                                                                        third_player_position, 'value'],
                                                                                       synergy_and_counterpick_dict)
                                total_time_kills_dict = distribute_heroes_data(hero_id, position, total_kills,
                                                                               ['total_kills_duo', another_player_hero_id,
                                                                                another_player_position, 'total_kills_trio',
                                                                                third_player_hero_id, third_player_position,
                                                                                'value'], total_time_kills_dict)

                                total_time_kills_dict = distribute_heroes_data(hero_id, position, match['durationSeconds'],
                                                                               ['total_time_duo', another_player_hero_id,
                                                                                another_player_position, 'total_time_trio',
                                                                                third_player_hero_id, third_player_position,
                                                                                'value'], total_time_kills_dict)
    return lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, over45_dict


def analyze_database(database, start_date_time, players_imp_data, to_be_saved, total_time_kills_dict=None, pro=False, over45_dict=None, synergy_and_counterpick_dict=None, lane_dict=None, count = 0):
    total = len(database)
    team_stat_dict = dict()
    used_maps = to_be_saved[0]['used_maps']
    for map_id in database:
        print(f'{count}/{total}')
        count += 1
        match = database[map_id]
        if map_id not in used_maps and match['direKills'] != None and (match['durationSeconds']/60) > 20:
            if any(player['steamAccount']['id'] in top_500_asia_europe for player in match['players']) and ('startDateTime' in match) and (match['startDateTime'] >= start_date_time):
                if pro:
                    if all(name in match and match[name] is not None for name in ['direTeam', 'radiantTeam']):
                        radiant_team_name = match['direTeam']['name'].lower()
                        dire_team_name = match['radiantTeam']['name'].lower()
                        if radiant_team_name in pro_teams and dire_team_name in pro_teams:
                            lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, over45_dict = proceed_map(match, map_id, players_imp_data, used_maps, lane_dict, synergy_and_counterpick_dict, total_time_kills_dict, over45_dict)
                        for team_name in [radiant_team_name, dire_team_name]:
                            team_stat_dict.setdefault(team_name, {}).setdefault('kills', []).append(sum(match['direKills']) + sum(match['radiantKills']))
                            team_stat_dict.setdefault(team_name, {}).setdefault('time', []).append(match['durationSeconds']/60)
                            if match['radiantTeam']['name'].lower() == team_name:
                                team_stat_dict.setdefault(team_name, {}).setdefault('id', match['radiantTeam']['id'])
                            else:
                                team_stat_dict.setdefault(team_name, {}).setdefault('id', match['direTeam']['id'])
                else:
                    lane_dict, players_imp_data, total_time_kills_dict, synergy_and_counterpick_dict, over45_dict = proceed_map(match, map_id, players_imp_data, used_maps, lane_dict, synergy_and_counterpick_dict, total_time_kills_dict, over45_dict)

                if map_id not in used_maps:
                    used_maps.append(map_id)
    for team in team_stat_dict:
        team_stat_dict[team]['time'] = sum(team_stat_dict[team]['time'])/len(team_stat_dict[team]['time'])
        team_stat_dict[team]['kills'] = sum(team_stat_dict[team]['kills']) / len(team_stat_dict[team]['kills'])
    with open('teams_stat_dict.txt', 'w') as f:
        json.dump(team_stat_dict, f)
    total_time_kills_dict['used_maps'], over45_dict['used_maps'], synergy_and_counterpick_dict['used_maps'], lane_dict['used_maps'] = used_maps, used_maps, used_maps, used_maps
    # for hero in synergy_and_counterpick_dict['value']:
    #     for pos in synergy_and_counterpick_dict['value'][hero]:
    #         winrate = synergy_and_counterpick_dict['value'][hero][pos]['winrate']
    #         synergy_and_counterpick_dict['value'][hero][pos]['winrate'] = {'value': (sum(winrate, 1) / (sum(winrate, 1) + sum(winrate, 0))) * 100, 'total_matches': len(winrate)}

    return players_imp_data, total_time_kills_dict, over45_dict, synergy_and_counterpick_dict, lane_dict
    # return ''.join(to_be_saved)


def calculate_average(values):
    new_values = [value for value in values if value < 0.44 or value > 0.56]
    return sum(new_values) / len(new_values) if new_values else None





def synergy_and_counterpick_copy(radiant_heroes_and_positions, dire_heroes_and_positions, output_message, over45):
    # print('my_protracker')
    sinergy, counterpick, pos1_vs_team, pos2_vs_team, pos3_vs_team, core_matchup = None, None, None, None, None, None

    # radiant_heroes_and_positions = {'pos 1': {'hero_id': 95, 'hero_name': 'Troll Warlord'}, 'pos 2': {'hero_id': 11, 'hero_name': 'Shadow Fiend'}, 'pos 3': {'hero_id': 33, 'hero_name': 'Enigma'}, 'pos 4': {'hero_id': 136, 'hero_name': 'Marci'}, 'pos 5': {'hero_id': 87, 'hero_name': 'Disruptor'}}
    # dire_heroes_and_positions = {'pos 1': {'hero_id': 99, 'hero_name': 'Bristleback'}, 'pos 2': {'hero_id': 52, 'hero_name': 'Leshrac'}, 'pos 3': {'hero_id': 20, 'hero_name': 'Vengeful Spirit'}, 'pos 4': {'hero_id': 51, 'hero_name': 'Clockwerk'}, 'pos 5': {'hero_id': 91, 'hero_name': 'Io'}}
    with open('./25_june_top600_heroes_data/synergy_and_counterpick_dict.txt', 'r+') as f:
        data = json.load(f)['value']
        radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team, dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
        radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, dire_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [], [], [], [], [], [], [], None, None
        #radiant_synergy
        for pos in radiant_heroes_and_positions:
            hero_id = str(radiant_heroes_and_positions[pos]['hero_id'])
            id_pos = {str(item['hero_id']): position_name for position_name, item in radiant_heroes_and_positions.items() if position_name != pos}
            try:
                hero_data = data[hero_id][pos]['synergy_duo']
                for another_hero_id in hero_data:
                    # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos1_with_team.append(wr)
                        except: pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['3', '4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    radiant_pos2_with_team.append(wr)
                        except: pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    radiant_pos3_with_team.append(wr)
                        except: pass
                    elif pos == 'pos4':
                            try:
                                position_name = id_pos[another_hero_id]
                                if position_name.replace('pos', '') == '5':
                                    values = hero_data[another_hero_id][position_name]['value']
                                    if len(values) >= 4:
                                        wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                        radiant_pos4_with_pos5 = wr
                            except: pass
            except: pass
        if radiant_pos4_with_pos5 is not None:
            radiant_wr_with += [radiant_pos4_with_pos5]
        radiant_wr_with += radiant_pos3_with_team + radiant_pos2_with_team + radiant_pos1_with_team
        #dire_synergy
        for pos in dire_heroes_and_positions:
            try:
                hero_id = str(dire_heroes_and_positions[pos]['hero_id'])
                hero_data = data[hero_id][pos]['synergy_duo']
                id_pos = {str(item['hero_id']): position_name for position_name, item in
                          dire_heroes_and_positions.items() if position_name != pos}

                for another_hero_id in hero_data:
                    if pos == 'pos1':
                        if len(dire_pos1_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos1_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos2':
                        if len(dire_pos2_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['3', '4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    dire_pos2_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        if len(dire_pos3_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') in ['4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    dire_pos3_with_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos4':
                        if len(dire_pos3_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id]
                            if position_name.replace('pos', '') == '5':
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    dire_pos4_with_pos5 = wr
                        except:
                            pass
            except: pass
        if dire_pos4_with_pos5 is not None:
            dire_wr_with += [dire_pos4_with_pos5]
        dire_wr_with += dire_pos3_with_team + dire_pos2_with_team + dire_pos1_with_team
        #against
        for pos in radiant_heroes_and_positions:
            try:
                hero_id = str(radiant_heroes_and_positions[pos]['hero_id'])
                id_pos = {str(item['hero_id']): position_name for position_name, item in
                          dire_heroes_and_positions.items()}
                hero_data = data[hero_id][pos]['counterpick_duo']
                for another_hero_id in hero_data:
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                if position_name == 'pos1':
                                    core_matchup = wr
                                radiant_pos1_vs_team.append(wr)
                        except: pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos2_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos3_vs_team.append(wr)
                        except:
                            pass
            except: pass
            #dire
            try:
                hero_id = str(dire_heroes_and_positions[pos]['hero_id'])
                hero_data = data[hero_id][pos]['counterpick_duo']
                id_pos = {str(item['hero_id']): position_name for position_name, item in
                          radiant_heroes_and_positions.items()}
                for another_hero_id in hero_data:
                    if pos == 'pos1':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos1_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos2':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos2_vs_team.append(wr)
                        except:
                            pass
                    elif pos == 'pos3':
                        try:
                            position_name = id_pos[another_hero_id]
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos3_vs_team.append(wr)
                        except:
                            pass
            except: pass
        radiant_wr_against += radiant_pos3_vs_team + radiant_pos2_vs_team + radiant_pos1_vs_team
        dire_wr_against += dire_pos3_vs_team + dire_pos2_vs_team + dire_pos1_vs_team
        if radiant_pos4_with_pos5 is not None and dire_pos4_with_pos5 is not None:
            sups = radiant_pos4_with_pos5 - dire_pos4_with_pos5
        else:
            sups = None
        dire_wr_with = clean_up(dire_wr_with, 4)
        radiant_wr_with = clean_up(radiant_wr_with, 4)
        radiant_wr_against = clean_up(radiant_wr_against, 5)
        radiant_pos1_vs_team = clean_up(radiant_pos1_vs_team)
        dire_pos1_vs_team = clean_up(dire_pos1_vs_team)
        radiant_pos2_vs_team = clean_up(radiant_pos2_vs_team)
        dire_pos2_vs_team = clean_up(dire_pos2_vs_team)
        radiant_pos3_vs_team = clean_up(radiant_pos3_vs_team)
        dire_pos3_vs_team = clean_up(dire_pos3_vs_team)

        if len(radiant_wr_with) > 0 and len(dire_wr_with) > 0:
            sinergy = round(((sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))), 2)
        if len(radiant_wr_against) > 0 and len(dire_wr_against) > 0:
            counterpick = round((sum(radiant_wr_against) / len(radiant_wr_against)) - (
                        sum(dire_wr_against) / len(dire_wr_against)), 2)
        if len(radiant_pos1_vs_team) > 0 and len(dire_pos1_vs_team) > 0:
            pos1_vs_team = round((sum(radiant_pos1_vs_team) / len(radiant_pos1_vs_team)) - (sum(dire_pos1_vs_team) / len(
                dire_pos1_vs_team)), 2)
        if len(radiant_pos3_vs_team) > 0 and len(dire_pos3_vs_team) > 0:
            pos3_vs_team = round((sum(radiant_pos3_vs_team) / len(radiant_pos3_vs_team)) - (sum(dire_pos3_vs_team) / len(
                dire_pos3_vs_team)), 2)
        if len(radiant_pos2_vs_team) > 0 and len(dire_pos2_vs_team) > 0:
            pos2_vs_team = round((sum(radiant_pos2_vs_team) / len(radiant_pos2_vs_team)) - (sum(dire_pos2_vs_team) / len(
                dire_pos2_vs_team)), 2)
        if core_matchup is not None:
            core_matchup -= 50
            core_matchup = round(core_matchup, 2)
        verdict, radiant_predict, dire_predict = analyze_draft(sinergy, counterpick, pos1_vs_team, core_matchup,
                                                               pos2_vs_team, pos3_vs_team,
                                                               sups, over45)
        output_message += (f'\nMy protracker: {verdict}\nSinergy: {sinergy}\nCounterpick: {counterpick}\nPos1_vs_team: {pos1_vs_team}\nPos2_vs_team: {pos2_vs_team}\nPos3_vs_team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\n')

    return output_message


def avg_over45(heroes_and_positions):
    with open('./heroes_data/over45_dict.txt', 'r') as f:
        data = json.load(f)
        data = data['value']
    # print('avg_over45')
    over45_duo, over45_trio, time_duo, kills_duo, kills_trio, time_trio, radiant_lane_report_unique_combinations, dire_lane_report_unique_combinations = [], [], [], [], [], [], [], []
    over45_unique_combinations = set()
    positions = ['1', '2', '3', '4', '5']
    for pos in positions:
        try:
            hero_id = str(heroes_and_positions['pos' + pos]['hero_id'])
            hero_data = data[hero_id]['pos' + pos]['over45_duo']
            for pos, item in heroes_and_positions.items():
                second_hero_id = str(item['hero_id'])
                try:
                    if second_hero_id != hero_id:
                        duo_data = hero_data[second_hero_id][pos]
                        combo = tuple(sorted([hero_id, second_hero_id]))
                        if combo not in over45_unique_combinations:
                            over45_unique_combinations.add(combo)
                            if len(duo_data['value']) >=4:
                                over45_duo.append(sum(duo_data['value']) / len(duo_data['value']))
                        # Третий герой
                        for pos3, item3 in heroes_and_positions.items():
                            third_hero_id = str(item3['hero_id'])
                            if third_hero_id not in [second_hero_id, hero_id]:
                                try:
                                    # Создаём отсортированный кортеж идентификаторов героев для уникальности
                                    combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                    if combo not in over45_unique_combinations:
                                        over45_unique_combinations.add(combo)
                                        value = duo_data['over45_trio'][third_hero_id][pos3]['value']
                                        if len(value) >=3:
                                            over45_trio.append(sum(duo_data['over45_trio'][third_hero_id][pos3]['value']) / len(duo_data['over45_trio'][third_hero_id][pos3]['value']))
                                except:
                                    pass
                except:
                    pass
        except:
            pass
    avg_over45_duo = calculate_average(over45_duo)
    avg_over45_trio = calculate_average(over45_trio)
    avg_over45 = (avg_over45_duo + avg_over45_trio) / 2 if avg_over45_trio is not None else avg_over45_duo
    return avg_over45

def lane_report_def(my_team, enemy_team):
    # print('lane_report')
    with open('./heroes_data/lane_dict.txt', 'r') as f:
        heroes_data = json.load(f)['value']
    avg_kills, avg_time, team_line_report, over35, over40, over45, over50, over55 = [], [], [], [], [], [], [], []
    copy_team_pos_and_heroes = {data['hero_id']: pos for pos, data in my_team.items()}
    for hero_id in copy_team_pos_and_heroes:
        pos = copy_team_pos_and_heroes[hero_id]
        data = heroes_data[str(hero_id)]
        if pos in data:
            if pos == 'pos1':
                try:
                    team_mate_hero_id = str(my_team['pos 5']['hero_id'])
                    team_mate_data = data[pos]['lane_report']['with_hero'][team_mate_hero_id]['pos5']['value']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                lane = team_mate_data.count(1) / (team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                team_line_report.append(lane)
            elif pos == 'pos3':
                try:
                    team_mate_hero_id = str(my_team['pos 4']['hero_id'])
                    team_mate_data = \
                    data[pos]['lane_report']['with_hero'][team_mate_hero_id]['pos4']['value']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                lane = team_mate_data.count(1) / (team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                team_line_report.append(lane)
            elif pos == 'pos2':
                try:
                    team_mate_hero_id = str(enemy_team['pos 2']['hero_id'])
                    team_mate_data = \
                    data[pos]['lane_report']['against_hero'][team_mate_hero_id]['pos2']['value']
                except KeyError:
                    team_mate_data = data[pos]['lane_report']['solo']['value']
                lane = team_mate_data.count(1) / (team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                team_line_report.append(lane)
            pass
    team_avg_lanes = sum(team_line_report) / len(team_line_report)
    return round(team_avg_lanes, 2)
def tm_kills(radiant_heroes_and_positions, dire_heroes_and_positions):
    # print('tm_kills')
    positions = ['1', '2', '3', '4', '5']
    radiant_time_unique_combinations, radiant_kills_unique_combinations, dire_kills_unique_combinations, dire_time_unique_combinations = set(), set(), set(), set()
    with open('./pro_heroes_data/total_time_kills_dict.txt', 'r') as f:
        data = json.load(f)
        data = data['value']
    # radiant_synergy
    for pos in positions:
        try:
            hero_id = str(radiant_heroes_and_positions['pos' + pos]['hero_id'])
            time_data = data[hero_id]['pos' + pos]['total_time_duo']
            kills_data = data[hero_id]['pos' + pos]['total_kills_duo']
            for hero_data in [time_data, kills_data]:
                for pos, item in radiant_heroes_and_positions.items():
                    second_hero_id = str(item['hero_id'])
                    try:
                        if second_hero_id != hero_id:
                            duo_data = hero_data[second_hero_id][pos]
                            combo = tuple(sorted([hero_id, second_hero_id]))
                            if hero_data == time_data:
                                if combo not in radiant_time_unique_combinations:
                                    radiant_time_unique_combinations.add(combo)
                                    value = (sum(duo_data['value']) / len(duo_data['value'])) / 60
                                    output_data['radiant_time_duo'].append(value)
                            elif hero_data == kills_data:
                                if combo not in radiant_kills_unique_combinations:
                                    radiant_kills_unique_combinations.add(combo)
                                    value = sum(duo_data['value']) / len(duo_data['value'])
                                    output_data['radiant_kills_duo'].append(value)
                            # Третий герой
                            for pos3, item3 in radiant_heroes_and_positions.items():
                                third_hero_id = str(item3['hero_id'])
                                if third_hero_id not in [second_hero_id, hero_id]:
                                    try:
                                        # Создаём отсортированный кортеж идентификаторов героев для уникальности
                                        combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                        if hero_data == time_data:
                                            if combo not in radiant_time_unique_combinations:
                                                radiant_time_unique_combinations.add(combo)
                                                trio_data = duo_data['total_time_trio'][third_hero_id][pos3]['value']
                                                value = (sum(trio_data) / len(trio_data)) / 60
                                                output_data['radiant_time_trio'].append(value)
                                        elif hero_data == kills_data:
                                            if combo not in radiant_kills_unique_combinations:
                                                radiant_kills_unique_combinations.add(combo)
                                                trio_data = duo_data['total_kills_trio'][third_hero_id][pos3]['value']
                                                value = sum(trio_data) / len(trio_data)
                                                output_data['radiant_kills_trio'].append(value)

                                    except:
                                        pass
                    except:
                        pass
        except:
            pass
        try:
            hero_id = str(dire_heroes_and_positions['pos' + pos]['hero_id'])
            time_data = data[hero_id]['pos' + pos][
                'total_time_duo']
            kills_data = data[hero_id]['pos' + pos][
                'total_kills_duo']
            for hero_data in [time_data, kills_data]:
                for pos, item in dire_heroes_and_positions.items():
                    second_hero_id = str(item['hero_id'])
                    try:
                        if second_hero_id != hero_id:
                            duo_data = hero_data[second_hero_id][pos]
                            combo = tuple(sorted([hero_id, second_hero_id]))
                            if hero_data == time_data:
                                if combo not in dire_time_unique_combinations:
                                    dire_time_unique_combinations.add(combo)
                                    value = (sum(duo_data['value']) / len(duo_data['value'])) / 60
                                    output_data['dire_time_duo'].append(value)
                            elif hero_data == kills_data:
                                if combo not in dire_kills_unique_combinations:
                                    dire_kills_unique_combinations.add(combo)
                                    value = sum(duo_data['value']) / len(duo_data['value'])
                                    output_data['dire_kills_duo'].append(value)
                            # third_hero
                            for pos3, item3 in dire_heroes_and_positions.items():
                                third_hero_id = str(item3['hero_id'])
                                if third_hero_id not in [second_hero_id, hero_id]:
                                    try:
                                        combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                        if hero_data == time_data:
                                            if combo not in dire_time_unique_combinations:
                                                dire_time_unique_combinations.add(combo)
                                                trio_data = duo_data['total_time_trio'][third_hero_id][pos3]['value']
                                                value = (sum(trio_data) / len(trio_data)) / 60
                                                output_data['dire_time_trio'].append(value)
                                        elif hero_data == kills_data:
                                            if combo not in dire_kills_unique_combinations:
                                                dire_kills_unique_combinations.add(combo)
                                                trio_data = duo_data['total_kills_trio'][third_hero_id][pos3]['value']
                                                value = sum(trio_data) / len(trio_data)
                                                output_data['dire_kills_trio'].append(value)

                                    except:
                                        pass

                    except:
                        pass
        except: pass

    def calculate_average(values):
        return sum(values) / len(values) if values else 0


    avg_time_trio = calculate_average(output_data['radiant_time_trio'] + output_data['dire_time_trio'])
    avg_kills_trio = calculate_average(output_data['radiant_kills_trio'] + output_data['dire_kills_trio'])
    avg_time_duo = calculate_average(output_data['radiant_time_duo'] + output_data['dire_time_duo'])
    avg_kills_duo = calculate_average(output_data['radiant_kills_duo'] + output_data['dire_kills_duo'])

    avg_kills = (avg_kills_trio + avg_kills_duo) / 2 if avg_kills_trio and avg_kills_duo else avg_kills_duo
    avg_time = (avg_time_duo + avg_time_trio) / 2 if avg_time_trio and avg_time_duo else avg_time_duo

    return round(avg_kills, 2), round(avg_time, 2)
