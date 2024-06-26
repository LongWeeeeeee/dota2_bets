from id_to_name import egb
import requests
from keys import api_token
import json
import time
from dltv_cyberscore import analyze_draft, clean_up
from id_to_name import translate, egb
from database import maps
import json
import time
# from aiolimiter import AsyncLimiter
# # Rate limiters for the API
# rate_limit_per_second = AsyncLimiter(20, 1)  # 20 requests per second
# rate_limit_per_minute = AsyncLimiter(250, 60)  # 250 requests per minute
# rate_limit_per_hour = AsyncLimiter(2000, 3600)  # 2000 requests per hour
# rate_limit_per_day = AsyncLimiter(10000, 86400)  # 10000 requests per day
# radiant_heroes_and_pos = {'pos 1': {'hero_id': 54, 'hero_name': 'Lifestealer'}, 'pos 2': {'hero_id': 11, 'hero_name': 'Shadow Fiend'}, 'pos 3': {'hero_id': 137, 'hero_name': 'Primal Beast'}, 'pos 4': {'hero_id': 114, 'hero_name': 'Monkey King'}, 'pos 5': {'hero_id': 65, 'hero_name': 'Batrider'}}
# dire_heroes_and_pos = {'pos 1': {'hero_id': 72, 'hero_name': 'Gyrocopter'}, 'pos 2': {'hero_id': 34, 'hero_name': 'Tinker'}, 'pos 3': {'hero_id': 96, 'hero_name': 'Centaur Warrunner'}, 'pos 4': {'hero_id': 63, 'hero_name': 'Weaver'}, 'pos 5': {'hero_id': 85, 'hero_name': 'Undying'}}
radiant_position_to_lane ={
        'POSITION_1': 'bottomLaneOutcome',
        'POSITION_2': 'midLaneOutcome',
        'POSITION_3': 'topLaneOutcome',
        'POSITION_4': 'topLaneOutcome',
        'POSITION_5': 'bottomLaneOutcome'
    }
dire_position_to_lane ={
    'POSITION_1': 'topLaneOutcome',
    'POSITION_2': 'midLaneOutcome',
    'POSITION_3': 'bottomLaneOutcome',
    'POSITION_4': 'bottomLaneOutcome',
    'POSITION_5': 'topLaneOutcome'
}

def fill_the_player(match, radiant_position_to_lane, dire_position_to_lane, hero_id, position, player, radiant_win,
                    isradiant, heroes_data):
    total_kills = sum(match['direKills']) + sum(match['radiantKills'])
    outcome = match[radiant_position_to_lane[position]]

    if 'total_kills' in heroes_data[hero_id][position]:
        heroes_data[hero_id][position]['total_kills'].append(total_kills)
    else:
        heroes_data[hero_id][position]['total_kills'] = [total_kills]
    if player['isRadiant'] is True:
        if 'RADIANT' in outcome:
            to_be_appended = 1
        elif 'DIRE' in outcome:
            to_be_appended = 0
        else:
            to_be_appended = 2
    else:
        outcome = match[dire_position_to_lane[position]]
        if 'RADIANT' in outcome:
            to_be_appended = 0
        elif 'DIRE' in outcome:
            to_be_appended = 1
        else:
            to_be_appended = 2
    if position != 'POSITION_2':
        if 'lane_report' not in heroes_data[hero_id][position]:
            heroes_data[hero_id][position]['lane_report'] = {'personal': [], 'with_hero': {}}
    else:
        if 'lane_report' not in heroes_data[hero_id][position]:
            heroes_data[hero_id][position]['lane_report'] = {'personal': [], 'against_hero': {}}
    heroes_data[hero_id][position]['lane_report']['personal'].append(to_be_appended)
    # if ((position in ['POSITION_5', 'POSITION_1']) and (another_player_position in ['POSITION_1', 'POSITION_5']) or (position in ['POSITION_3', 'POSITION_4']) and (another_player_position in ['POSITION_3', 'POSITION_4'])) and (isradiant == another_isradiant) and (position != another_player_position):
    #     if another_player_hero_id not in heroes_data[hero_id][position]['lane_report']['with_hero']:
    #         heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id] = {}
    #     if another_player_position not in heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id]:
    #         heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id][another_player_position] = []
    #         heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id][another_player_position].append(to_be_appended)
    if 'total_time' in heroes_data[hero_id][position]:
        heroes_data[hero_id][position]['total_time'].append(match['durationSeconds'])
    else:
        heroes_data[hero_id][position]['total_time'] = [match['durationSeconds']]
    if match['durationSeconds'] / 60 > 35:
        if radiant_win:
            if isradiant:
                to_be_appended = 1
            else:
                to_be_appended = 0
            if 'over35' in heroes_data[hero_id][position]:
                heroes_data[hero_id][position]['over35'].append(to_be_appended)
            else:
                heroes_data[hero_id][position]['over35'] = [to_be_appended]
    if match['durationSeconds'] / 60 > 40:
        if radiant_win:
            if isradiant:
                to_be_appended = 1
            else:
                to_be_appended = 0
            if 'over40' in heroes_data[hero_id][position]:
                heroes_data[hero_id][position]['over40'].append(to_be_appended)
            else:
                heroes_data[hero_id][position]['over40'] = [to_be_appended]
    if match['durationSeconds'] / 60 > 45:
        if radiant_win:
            if isradiant:
                to_be_appended = 1
            else:
                to_be_appended = 0
            if 'over45' in heroes_data[hero_id][position]:
                heroes_data[hero_id][position]['over45'].append(to_be_appended)
            else:
                heroes_data[hero_id][position]['over45'] = [to_be_appended]
    if match['durationSeconds'] / 60 > 50:
        if radiant_win:
            if isradiant:
                to_be_appended = 1
            else:
                to_be_appended = 0
            if 'over50' in heroes_data[hero_id][position]:
                heroes_data[hero_id][position]['over50'].append(to_be_appended)
            else:
                heroes_data[hero_id][position]['over50'] = [to_be_appended]
    if match['durationSeconds'] / 60 > 55:
        if radiant_win:
            if isradiant:
                to_be_appended = 1
            else:
                to_be_appended = 0
            if 'over55' in heroes_data[hero_id][position]:
                heroes_data[hero_id][position]['over55'].append(to_be_appended)
            else:
                heroes_data[hero_id][position]['over55'] = [to_be_appended]
    return heroes_data


def get_maps():
    ids_to_graph, total_map_ids = [], []
    for steam_id in egb:
        check, skip = True, 0
        if len(ids_to_graph) != 5:
            ids_to_graph.append(steam_id)
        else:
            try:
                while check:
                    query = '''
                    {players(steamAccountIds:%s){
                      steamAccountId
                      matches(request:{startDateTime:1716595200, take:100, skip:%s, gameModeIds:[22,2]}){
                        id
                      }
                    }
                    }
                    ''' % (ids_to_graph, skip)
                    headers = {"Authorization": f"Bearer {api_token}"}
                    response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
                    data = json.loads(response.text)
                    if any(player['matches'] != [] for player in data['data']['players']):
                        for player in data['data']['players']:
                            for map_id in player['matches']:
                                total_map_ids.append(map_id['id'])
                        skip+=100
                    else:
                        ids_to_graph = []
                        check = False
            except Exception as e:
                print(f"Error {e}")
                time.sleep(5)
    return set(total_map_ids)


def research_maps(maps_to_explore):
    maps_to_explore = set(maps_to_explore)
    with open('output_file.txt', 'r+') as f:
        file_data = json.load(f)
        counter = 0
        for map_id in maps_to_explore:
            if str(map_id) not in file_data:
                if counter == 100:
                    f.truncate()
                    f.seek(0)
                    json.dump(file_data, f)
                    counter = 0
                try:
                    query = '''
                    {match(id:%s){
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
                    headers = {"Authorization": f"Bearer {api_token}"}
                    response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
                    data = json.loads(response.text)['data']['match']
                    file_data[map_id] = data
                    print(f'Длина файла: {len(file_data)}')
                    counter += 1
                except Exception as e:
                    print(f"Error processing map ID {map_id}: {e}")
                    time.sleep(5)



def heroes_data_structure(heroes_data, hero_id, position):
    if hero_id not in heroes_data:
        heroes_data[hero_id] = {}
    if position not in heroes_data[hero_id]:
        heroes_data[hero_id][position] = {}
    if 'counterpick' not in heroes_data[hero_id][position]:
        heroes_data[hero_id][position]['counterpick'] = {}
    if 'synergy' not in heroes_data[hero_id][position]:
        heroes_data[hero_id][position]['counterpick'] = {}
    return heroes_data


def player_add_structure(players_data, steam_id, hero_id, position):
    #steamAnonymos

    if steam_id not in players_data:
        players_data[steam_id] = {}
    if hero_id not in players_data[steam_id]:
        players_data[steam_id][hero_id] = {}
    if position not in players_data[steam_id][hero_id]:
        players_data[steam_id][hero_id][position] = []
    return players_data

def lane_with_hero(player, heroes_data, position, match, hero_id, another_player_position, another_player_hero_id, isradiant, another_isradiant):
    outcome = match[radiant_position_to_lane[position]]
    if player['isRadiant'] is True:
        if 'RADIANT' in outcome:
            to_be_appended = 1
        elif 'DIRE' in outcome:
            to_be_appended = 0
        else:
            to_be_appended = 2
    else:
        outcome = match[dire_position_to_lane[position]]
        if 'RADIANT' in outcome:
            to_be_appended = 0
        elif 'DIRE' in outcome:
            to_be_appended = 1
        else:
            to_be_appended = 2
    if ((position in ['POSITION_5', 'POSITION_1']) and (another_player_position in ['POSITION_1', 'POSITION_5']) or (
            position in ['POSITION_3', 'POSITION_4']) and (
                another_player_position in ['POSITION_3', 'POSITION_4'])) and (isradiant == another_isradiant) and (
            position != another_player_position):
        if another_player_hero_id not in heroes_data[hero_id][position]['lane_report']['with_hero']:
            heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id] = {}
        if another_player_position not in heroes_data[hero_id][position]['lane_report']['with_hero'][
            another_player_hero_id]:
            heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id][
                another_player_position] = []
        heroes_data[hero_id][position]['lane_report']['with_hero'][another_player_hero_id][
            another_player_position].append(to_be_appended)
    if (position == 'POSITION_2') and (another_player_position == 'POSITION_2') and (hero_id != another_player_hero_id):
        if another_player_hero_id not in heroes_data[hero_id][position]['lane_report']['against_hero']:
            heroes_data[hero_id][position]['lane_report']['against_hero'][another_player_hero_id] = {}
        if another_player_position not in heroes_data[hero_id][position]['lane_report']['against_hero'][
            another_player_hero_id]:
            heroes_data[hero_id][position]['lane_report']['against_hero'][another_player_hero_id][
                another_player_position] = []
        heroes_data[hero_id][position]['lane_report']['against_hero'][another_player_hero_id][
            another_player_position].append(to_be_appended)
    return heroes_data


def fix_for_another_player(another_player_hero_id, position, hero_id, another_player_position, heroes_data):

    if another_player_hero_id not in heroes_data[hero_id][position]['counterpick']:
        heroes_data[hero_id][position]['counterpick'][another_player_hero_id] = {}
    if another_player_position not in heroes_data[hero_id][position]['counterpick'][another_player_hero_id]:
        heroes_data[hero_id][position]['counterpick'][another_player_hero_id][another_player_position] = []
    if 'synergy' not in heroes_data[hero_id][position]:
        heroes_data[hero_id][position]['synergy'] = {}
    if another_player_hero_id not in heroes_data[hero_id][position]['synergy']:
        heroes_data[hero_id][position]['synergy'][another_player_hero_id] = {}
    if another_player_position not in heroes_data[hero_id][position]['synergy'][another_player_hero_id]:
        heroes_data[hero_id][position]['synergy'][another_player_hero_id][another_player_position] = []
    return heroes_data



def analyze_database(database, done = 0):
    with open('heroes_data.txt', 'r+') as f:
        with open('players_imp_data.txt', 'r+') as f2:
            heroes_data = json.load(f)
            players_data = json.load(f2)
            total = len(database)
            for map_id in database:
                match = database[map_id]
                if match['direKills'] != None and (match['durationSeconds']/60) > 20:
                    for player in match['players']:
                        radiant_win = match['didRadiantWin']
                        position = player['position']
                        hero_id = player['hero']['id']
                        isradiant = player['isRadiant']
                        steam_id = player['steamAccount']['id']
                        if player['steamAccount']['isAnonymous']:
                            players_data = player_add_structure(players_data, steam_id, hero_id, position)
                            players_data[steam_id][hero_id][position].append(player['imp'])
                        heroes_data = heroes_data_structure(heroes_data, hero_id, position)
                        #time, kills, and other shit
                        heroes_data = fill_the_player(match, radiant_position_to_lane, dire_position_to_lane, hero_id, position,
                                        player, radiant_win,
                                        isradiant, heroes_data)
                        for another_player in match['players']:
                            another_player_hero_id = another_player['hero']['id']
                            another_player_position = another_player['position']
                            another_isradiant = another_player['isRadiant']
                            heroes_data = fix_for_another_player(another_player_hero_id, position, hero_id, another_player_position, heroes_data)
                            heroes_data = lane_with_hero(player, heroes_data, position, match, hero_id, another_player_position, another_player_hero_id, isradiant, another_isradiant)
                            #counterpick
                            if isradiant != another_player['isRadiant']:
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
                                heroes_data[hero_id][position]['counterpick'][another_player_hero_id][
                                    another_player_position].append(to_be_appended)
                            #synergy
                            if (isradiant == another_player['isRadiant']) and (hero_id != another_player_hero_id):
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
                                heroes_data[hero_id][position]['synergy'][another_player_hero_id][
                                    another_player_position].append(to_be_appended)
                done +=1
                print(f'{done}/{total}')
            f.truncate()
            f.seek(0)
            json.dump(heroes_data, f)
            f2.truncate()
            f2.seek(0)
            json.dump(players_data, f2)


def syngery_and_counterpick(radiant_heroes_and_positions, dire_heroes_and_positions, output_message):
    sinergy, counterpick, pos1_vs_team, pos2_vs_team, pos3_vs_team, core_matchup = None, None, None, None, None, None

    # radiant_heroes_and_positions = {'pos 1': {'hero_id': 95, 'hero_name': 'Troll Warlord'}, 'pos 2': {'hero_id': 11, 'hero_name': 'Shadow Fiend'}, 'pos 3': {'hero_id': 33, 'hero_name': 'Enigma'}, 'pos 4': {'hero_id': 136, 'hero_name': 'Marci'}, 'pos 5': {'hero_id': 87, 'hero_name': 'Disruptor'}}
    # dire_heroes_and_positions = {'pos 1': {'hero_id': 99, 'hero_name': 'Bristleback'}, 'pos 2': {'hero_id': 52, 'hero_name': 'Leshrac'}, 'pos 3': {'hero_id': 20, 'hero_name': 'Vengeful Spirit'}, 'pos 4': {'hero_id': 51, 'hero_name': 'Clockwerk'}, 'pos 5': {'hero_id': 91, 'hero_name': 'Io'}}
    with open('heroes_data.txt', 'r+') as f:
        data = json.load(f)
        data = dict(sorted(data.items()))

        radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team, dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
        radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, dire_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [], [], [], [], [], [], [], None, None
        positions = ['1', '2', '3', '4']
        #radiant_synergy
        for dig in positions:
            hero_data = data[str(radiant_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_'+ dig]['synergy']
            for another_hero_id in hero_data:
                copy_radiant_heroes_and_positions = radiant_heroes_and_positions.copy()
                copy_radiant_heroes_and_positions.pop('pos ' + dig)
                a = [[pos, item['hero_id']] for pos, item in copy_radiant_heroes_and_positions.items()]
                id_pos = {}
                for item in a:
                    id_pos[item[1]] = item[0]
                    # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                if dig == '1':
                    if len(radiant_pos1_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            radiant_pos1_with_team.append(wr)
                    except: pass
                elif dig == '2':
                    if len(radiant_pos2_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        if position_name.replace('POSITION_', '') in ['3', '4', '5']:
                            values = hero_data[another_hero_id][position_name]
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos2_with_team.append(wr)
                    except: pass
                elif dig == '3':
                    if len(radiant_pos3_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        if position_name.replace('POSITION_', '') in ['4', '5']:
                            values = hero_data[another_hero_id][position_name]
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos3_with_team.append(wr)
                    except: pass
                elif dig == '4':
                    if len(radiant_pos3_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        if position_name.replace('POSITION_', '') == '5':
                            values = hero_data[another_hero_id][position_name]
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos4_with_pos5 = wr
                    except: pass
        if radiant_pos4_with_pos5 is not None:
            radiant_wr_with += [radiant_pos4_with_pos5]
        radiant_wr_with += radiant_pos3_with_team + radiant_pos2_with_team + radiant_pos1_with_team
        #dire_synergy
        for dig in positions:
            hero_data = data[str(dire_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_' + dig]['synergy']
            for another_hero_id in hero_data:
                copy_dire_heroes_and_positions = dire_heroes_and_positions.copy()
                copy_dire_heroes_and_positions.pop('pos ' + dig)
                a = [[pos, item['hero_id']] for pos, item in copy_dire_heroes_and_positions.items()]
                id_pos = {}
                for item in a:
                    id_pos[item[1]] = item[0]
                    # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                if dig == '1':
                    if len(dire_pos1_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            dire_pos1_with_team.append(wr)
                    except:
                        pass
                elif dig == '2':
                    if len(dire_pos2_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        if position_name.replace('POSITION_', '') in ['3', '4', '5']:
                            values = hero_data[another_hero_id][position_name]
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos2_with_team.append(wr)
                    except:
                        pass
                elif dig == '3':
                    if len(dire_pos3_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        if position_name.replace('POSITION_', '') in ['4', '5']:
                            values = hero_data[another_hero_id][position_name]
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos3_with_team.append(wr)
                    except:
                        pass
                elif dig == '4':
                    if len(dire_pos3_with_team) == 4:
                        break
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        if position_name.replace('POSITION_', '') == '5':
                            values = hero_data[another_hero_id][position_name]
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos4_with_pos5 = wr
                    except:
                        pass
        if dire_pos4_with_pos5 is not None:
            dire_wr_with += [dire_pos4_with_pos5]
        dire_wr_with += dire_pos3_with_team + dire_pos2_with_team + dire_pos1_with_team
        #against
        for dig in positions:
            hero_data = data[str(radiant_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_' + dig]['counterpick']
            for another_hero_id in hero_data:
                a = [[pos, item['hero_id']] for pos, item in dire_heroes_and_positions.items()]
                id_pos = {}
                for item in a:
                    id_pos[item[1]] = item[0]
                if dig == '1':
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            if position_name == 'POSITION_1':
                                core_matchup = wr
                            radiant_pos1_vs_team.append(wr)
                    except:
                        pass
                elif dig == '2':
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            radiant_pos2_vs_team.append(wr)
                    except:
                        pass
                elif dig == '3':
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            radiant_pos3_vs_team.append(wr)
                    except:
                        pass
            radiant_wr_against += radiant_pos3_vs_team + radiant_pos2_vs_team + radiant_pos1_vs_team
            #dire
            hero_data = data[str(dire_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_' + dig][
                'counterpick']
            for another_hero_id in hero_data:
                a = [[pos, item['hero_id']] for pos, item in dire_heroes_and_positions.items()]
                id_pos = {}
                for item in a:
                    id_pos[item[1]] = item[0]
                if dig == '1':
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            dire_pos1_vs_team.append(wr)
                    except:
                        pass
                elif dig == '2':
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4: 
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            dire_pos2_vs_team.append(wr)
                    except:
                        pass
                elif dig == '3':
                    try:
                        position_name = id_pos[int(another_hero_id)].replace('pos ', 'POSITION_')
                        values = hero_data[another_hero_id][position_name]
                        if len(values) >= 4:
                            wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                            dire_pos3_vs_team.append(wr)
                    except:
                        pass
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
            sinergy = (sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))
        if len(radiant_wr_against) > 0:
            counterpick = (sum(radiant_wr_against) / len(radiant_wr_against)) - (
                        sum(dire_wr_against) / len(dire_wr_against))
        if len(radiant_pos1_vs_team) > 0 and len(dire_pos1_vs_team) > 0:
            pos1_vs_team = (sum(radiant_pos1_vs_team) / len(radiant_pos1_vs_team)) - (sum(dire_pos1_vs_team) / len(
                dire_pos1_vs_team))
        if len(radiant_pos3_vs_team) > 0 and len(dire_pos3_vs_team) > 0:
            pos3_vs_team = (sum(radiant_pos3_vs_team) / len(radiant_pos3_vs_team)) - (sum(dire_pos3_vs_team) / len(
                dire_pos3_vs_team))
        if len(radiant_pos2_vs_team) > 0 and len(dire_pos2_vs_team) > 0:
            pos2_vs_team = (sum(radiant_pos2_vs_team) / len(radiant_pos2_vs_team)) - (sum(dire_pos2_vs_team) / len(
                dire_pos2_vs_team))
        if core_matchup is not None:
            core_matchup -= 50
        verdict, radiant_predict, dire_predict = analyze_draft(sinergy, counterpick, pos1_vs_team, core_matchup,
                                                               pos2_vs_team, pos3_vs_team,
                                                               sups)
        output_message += (f'My protracker: {verdict}\nSinergy: {sinergy}\nCounterpick: {counterpick}\nPos1_vs_team: {pos1_vs_team}\nPos2_vs_team: {pos2_vs_team}\nPos3_vs_team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\n')

        pass


def analyze_players(my_team, enemy_team):
    with open('heroes_data.txt', 'r') as f:
        heroes_data = json.load(f)
        team_avg_kills, team_avg_time, team_line_report, over35, over40, over45, over50, over55 = [], [], [], [], [], [], [], []
        copy_team_pos_and_heroes = {}
        for pos, data in my_team.items():
            copy_team_pos_and_heroes[data['hero_id']] = pos
        for hero_id in copy_team_pos_and_heroes:
            pos = copy_team_pos_and_heroes[hero_id].replace('pos ', 'POSITION_')
            data = heroes_data[str(hero_id)]
            hero_name = translate[hero_id]
            if pos in data:
                if 'over45' in data[pos]:
                    maps = (data[pos]['over45'].count(1) + data[pos]['over45'].count(0))
                    value = data[pos]['over45'].count(1) / maps
                    over45.append(value)
                if pos == 'POSITION_1':
                    try:
                        team_mate_hero_id = str(my_team['pos 5']['hero_id'])
                        team_mate_data = data[pos]['lane_report']['with_hero'][team_mate_hero_id]['POSITION_5']
                    except KeyError:
                        team_mate_data = data[pos]['lane_report']['personal']
                    lane = team_mate_data.count(1) / (team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                    team_line_report.append(lane)
                elif pos == 'POSITION_3':
                    try:
                        team_mate_hero_id = str(my_team['pos 4']['hero_id'])
                        team_mate_data = \
                        data[pos]['lane_report']['with_hero'][team_mate_hero_id]['POSITION_4']
                    except KeyError:
                        team_mate_data = data[pos]['lane_report']['personal']
                    lane = team_mate_data.count(1) / (team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                    team_line_report.append(lane)
                elif pos == 'POSITION_2':
                    try:
                        team_mate_hero_id = str(enemy_team['pos 2']['hero_id'])
                        team_mate_data = \
                        data[pos]['lane_report']['against_hero'][team_mate_hero_id]['POSITION_2']
                    except KeyError:
                        team_mate_data = data[pos]['lane_report']['personal']
                    lane = team_mate_data.count(1) / (team_mate_data.count(1) + team_mate_data.count(0) + team_mate_data.count(2))
                    team_line_report.append(lane)
                pass
        team_over45_win = sum(over45) / len(over45)
        team_avg_lanes = sum(team_line_report) / len(team_line_report)
    return team_avg_lanes, team_over45_win
# maps = get_maps()
# pass
maps_data = research_maps(maps_to_explore=maps)
pass
# with open('output_file.txt', 'r+') as f:
#     database = json.load(f)
#     analyze_database(database)
#     pass
# syngery_and_counterpick()