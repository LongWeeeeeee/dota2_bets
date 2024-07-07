# from id_to_name import egb
import requests

import id_to_name
from keys import api_token
# import json
from collections import defaultdict
# import time
from dltv_cyberscore import analyze_draft, clean_up
from id_to_name import translate, egb, pro_teams, top_600_asia_europe, non_anon_top_1000_europe_top_1000_asia
# from database import maps, pro_maps
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
    heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('lane_report', {}).setdefault('personal', []).append(to_be_appended)
    return heroes_data


def get_maps(game_mods):
    with open('25_june_top600_maps.txt', 'r+') as f:
        file_data = json.load(f)
        ids_to_graph, total_map_ids = [], []
        count = 0
        for steam_id in non_anon_top_1000_europe_top_1000_asia:
            if steam_id not in top_600_asia_europe:
                print(f'{count}/{len(non_anon_top_1000_europe_top_1000_asia)}')
                check, skip = True, 0
                if len(ids_to_graph) != 5:
                    ids_to_graph.append(steam_id)
                else:
                    try:
                        while check:
                            query = '''
                            {players(steamAccountIds:%s){
                              steamAccountId
                              matches(request:{startDateTime:1719262800, take:100, skip:%s, gameModeIds:%s}){
                                id
                              }
                            }
                            }
                            ''' % (ids_to_graph, skip, game_mods)
                            headers = {"Authorization": f"Bearer {api_token}"}
                            response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
                            data = json.loads(response.text)
                            if any(player['matches'] != [] for player in data['data']['players']):
                                for player in data['data']['players']:
                                    for map_id in player['matches']:
                                        if map_id['id'] not in file_data:
                                            file_data.append(map_id['id'])
                                skip+=100
                            else:
                                ids_to_graph = []
                                check = False
                    except Exception as e:
                        print(f"Error {e}")
                        time.sleep(5)
            count +=1
        f.truncate()
        f.seek(0)
        json.dump(file_data, f)


def research_maps():
    with open('25_june_top600_maps.txt', 'r') as f2:
        maps_to_explore = json.load(f2)
    maps_to_explore = set(maps_to_explore)
    with open('25_june_top600_output.txt', 'r+') as f:
        file_data = json.load(f)
        counter = 0
        for map_id in maps_to_explore:
            print(f'{counter}/{len(maps_to_explore)}')
            counter += 1
            if str(map_id) not in file_data:
                if counter % 100 == 0:
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
                        name
                      }
                      radiantTeam{
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
                    headers = {"Authorization": f"Bearer {api_token}"}
                    response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
                    data = json.loads(response.text)['data']['match']
                    file_data[map_id] = data
                except Exception as e:
                    print(f"Error processing map ID {map_id}: {e}")
                    time.sleep(5)
        f.truncate()
        f.seek(0)
        json.dump(file_data, f)




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
        heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('lane_report', {}).setdefault('with_hero', {}).setdefault(another_player_hero_id, {}).setdefault(
            another_player_position, []).append(to_be_appended)
    if (position == 'POSITION_2') and (another_player_position == 'POSITION_2') and (hero_id != another_player_hero_id):
        heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('lane_report', {}).setdefault('against_hero', {}).setdefault(another_player_hero_id, {}).setdefault(
            another_player_position, []).append(to_be_appended)
    return heroes_data


def analyze_database(database, players_data, heroes_data):
    total = len(database)
    count = 0
    for map_id in database:
        print(f'{count}/{total}')
        count += 1
        match = database[map_id]
        if map_id not in heroes_data['used_maps'] and match['direKills'] != None and (match['durationSeconds']/60) > 20:
            if any(player['steamAccount']['id'] in top_600_asia_europe for player in match['players']):
                # radiant_team_name = match['direTeam']['name'].lower()
                # dire_team_name = match['radiantTeam']['name'].lower()
                for player in match['players']:
                    radiant_win = match['didRadiantWin']
                    position = player['position']
                    hero_id = str(player['hero']['id'])
                    isradiant = player['isRadiant']
                    steam_id = str(player['steamAccount']['id'])
                    if map_id not in players_data['used_maps']:
                        if (player['steamAccount']['isAnonymous']):
                            players_data.setdefault(steam_id, {}).setdefault(hero_id, {}).setdefault(position, []).append(player['imp'])
                            players_data.setdefault('used_maps', []).append(map_id)
                    if map_id not in heroes_data['used_maps']:
                        #time, kills, and other shit
                        heroes_data = fill_the_player(match, radiant_position_to_lane, dire_position_to_lane, hero_id, position,
                                        player, radiant_win,
                                        isradiant, heroes_data)
                        for another_player in match['players']:
                            another_player_hero_id = str(another_player['hero']['id'])
                            another_player_position = another_player['position']
                            another_isradiant = another_player['isRadiant']
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
                                heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('counterpick_duo', {}).setdefault(another_player_hero_id, {}).setdefault(
                                    another_player_position, {}).setdefault('value', []).append(to_be_appended)
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
                                total_kills = sum(match['direKills']) + sum(match['radiantKills'])
                                if match['durationSeconds'] / 60 > 45:
                                    heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault(
                                        'over45_duo', {}).setdefault(another_player_hero_id, {}).setdefault(another_player_position,{}).setdefault('value', []).append(to_be_appended)
                                heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('synergy_duo', {}).setdefault(another_player_hero_id, {}).setdefault(
                                    another_player_position, {}).setdefault('value', []).append(to_be_appended)
                                heroes_data[hero_id][position].setdefault('total_kills_duo', {}).setdefault(another_player_hero_id, {}).setdefault(another_player_position,{}).setdefault('value', []).append(total_kills)
                                heroes_data[hero_id][position].setdefault('total_time_duo', {}).setdefault(another_player_hero_id, {}).setdefault(another_player_position, {}).setdefault('value', []).append(match['durationSeconds'])
                                for third_player in match['players']:
                                    third_player_hero_id = str(third_player['hero']['id'])
                                    third_player_position = third_player['position']
                                    third_isradiant = third_player['isRadiant']

                                    # Ensure the third player is on the same team and different from the other two heroes
                                    if (isradiant == third_isradiant) and (third_player_hero_id not in [hero_id, another_player_hero_id]):
                                        # Update synergy and total stats for the triple combination
                                        if match['durationSeconds'] / 60 > 45:
                                            heroes_data[hero_id][position]['over45_duo'][another_player_hero_id][another_player_position].setdefault('over45_trio', {}).setdefault(third_player_hero_id, {}).setdefault(third_player_position, []).append(to_be_appended)
                                        heroes_data[hero_id][position]['synergy_duo'][another_player_hero_id][another_player_position].setdefault('syngergy_trio', {}).setdefault(third_player_hero_id, {}).setdefault(third_player_position, []).append(to_be_appended)
                                        heroes_data[hero_id][position]['total_kills_duo'][another_player_hero_id][another_player_position].setdefault('total_kills_trio',{}).setdefault(third_player_hero_id, {}).setdefault(third_player_position,[]).append(total_kills)
                                        heroes_data[hero_id][position]['total_time_duo'][another_player_hero_id][another_player_position].setdefault('total_time_trio', {}).setdefault(third_player_hero_id, {}).setdefault(third_player_position,[]).append(match['durationSeconds'])
                if map_id not in heroes_data['used_maps']:
                    heroes_data['used_maps'].append(map_id)
    with open('players_imp_data.txt', 'r+') as f2:
        f2.truncate()
        f2.seek(0)
        json.dump(players_data, f2)
    return heroes_data


def analyze_database_pros(database, players_data, heroes_data):
    total = len(database)
    count = 0
    for map_id in database:
        print(f'{count}/{total}')
        count += 1
        match = database[map_id]
        if map_id not in heroes_data['used_maps'] and match['direKills'] != None and (match['durationSeconds']/60) > 20:
            if any(player['steamAccount']['id'] in top_600_asia_europe for player in match['players']):
                try:
                    radiant_team_name = match['direTeam']['name'].lower()
                    dire_team_name = match['radiantTeam']['name'].lower()
                    if radiant_team_name in id_to_name.pro_teams and dire_team_name in id_to_name.pro_teams:
                        for player in match['players']:
                            radiant_win = match['didRadiantWin']
                            position = player['position']
                            hero_id = str(player['hero']['id'])
                            isradiant = player['isRadiant']
                            steam_id = str(player['steamAccount']['id'])
                            if map_id not in players_data['used_maps']:
                                if (player['steamAccount']['isAnonymous']):
                                    players_data.setdefault(steam_id, {}).setdefault(hero_id, {}).setdefault(position, []).append(player['imp'])
                                    players_data.setdefault('used_maps', []).append(map_id)
                            if map_id not in heroes_data['used_maps']:
                                #time, kills, and other shit
                                heroes_data = fill_the_player(match, radiant_position_to_lane, dire_position_to_lane, hero_id, position,
                                                player, radiant_win,
                                                isradiant, heroes_data)
                                for another_player in match['players']:
                                    another_player_hero_id = str(another_player['hero']['id'])
                                    another_player_position = another_player['position']
                                    another_isradiant = another_player['isRadiant']
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
                                        heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('counterpick_duo', {}).setdefault(another_player_hero_id, {}).setdefault(
                                            another_player_position, {}).setdefault('value', []).append(to_be_appended)
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
                                        total_kills = sum(match['direKills']) + sum(match['radiantKills'])
                                        if match['durationSeconds'] / 60 > 45:
                                            heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault(
                                                'over45_duo', {}).setdefault(another_player_hero_id, {}).setdefault(another_player_position,{}).setdefault('value', []).append(to_be_appended)
                                        heroes_data.setdefault(hero_id, {}).setdefault(position, {}).setdefault('synergy_duo', {}).setdefault(another_player_hero_id, {}).setdefault(
                                            another_player_position, {}).setdefault('value', []).append(to_be_appended)
                                        heroes_data[hero_id][position].setdefault('total_kills_duo', {}).setdefault(another_player_hero_id, {}).setdefault(another_player_position,{}).setdefault('value', []).append(total_kills)
                                        heroes_data[hero_id][position].setdefault('total_time_duo', {}).setdefault(another_player_hero_id, {}).setdefault(another_player_position, {}).setdefault('value', []).append(match['durationSeconds'])
                                        for third_player in match['players']:
                                            third_player_hero_id = str(third_player['hero']['id'])
                                            third_player_position = third_player['position']
                                            third_isradiant = third_player['isRadiant']

                                            # Ensure the third player is on the same team and different from the other two heroes
                                            if (isradiant == third_isradiant) and (third_player_hero_id not in [hero_id, another_player_hero_id]):
                                                # Update synergy and total stats for the triple combination
                                                if match['durationSeconds'] / 60 > 45:
                                                    heroes_data[hero_id][position]['over45_duo'][another_player_hero_id][another_player_position].setdefault('over45_trio', {}).setdefault(third_player_hero_id, {}).setdefault(third_player_position, []).append(to_be_appended)
                                                heroes_data[hero_id][position]['synergy_duo'][another_player_hero_id][another_player_position].setdefault('syngergy_trio', {}).setdefault(third_player_hero_id, {}).setdefault(third_player_position, []).append(to_be_appended)
                                                heroes_data[hero_id][position]['total_kills_duo'][another_player_hero_id][another_player_position].setdefault('total_kills_trio',{}).setdefault(third_player_hero_id, {}).setdefault(third_player_position,[]).append(total_kills)
                                                heroes_data[hero_id][position]['total_time_duo'][another_player_hero_id][another_player_position].setdefault('total_time_trio', {}).setdefault(third_player_hero_id, {}).setdefault(third_player_position,[]).append(match['durationSeconds'])
                        heroes_data['used_maps'].append(map_id)
                except: pass

    with open('players_imp_data.txt', 'r+') as f2:
        f2.truncate()
        f2.seek(0)
        json.dump(players_data, f2)
    return heroes_data


def calculate_average(values):
    return sum(values) / len(values) if values else 0



def syngery_and_counterpick(radiant_heroes_and_positions, dire_heroes_and_positions, output_message):
    print('my_protracker')
    sinergy, counterpick, pos1_vs_team, pos2_vs_team, pos3_vs_team, core_matchup = None, None, None, None, None, None

    # radiant_heroes_and_positions = {'pos 1': {'hero_id': 95, 'hero_name': 'Troll Warlord'}, 'pos 2': {'hero_id': 11, 'hero_name': 'Shadow Fiend'}, 'pos 3': {'hero_id': 33, 'hero_name': 'Enigma'}, 'pos 4': {'hero_id': 136, 'hero_name': 'Marci'}, 'pos 5': {'hero_id': 87, 'hero_name': 'Disruptor'}}
    # dire_heroes_and_positions = {'pos 1': {'hero_id': 99, 'hero_name': 'Bristleback'}, 'pos 2': {'hero_id': 52, 'hero_name': 'Leshrac'}, 'pos 3': {'hero_id': 20, 'hero_name': 'Vengeful Spirit'}, 'pos 4': {'hero_id': 51, 'hero_name': 'Clockwerk'}, 'pos 5': {'hero_id': 91, 'hero_name': 'Io'}}
    with open('25_june_top600_heroes_data.txt', 'r+') as f:
        data = json.load(f)
        data = dict(sorted(data.items()))

        radiant_pos1_with_team, radiant_pos2_with_team, radiant_pos3_with_team, dire_pos1_with_team, dire_pos2_with_team, dire_pos3_with_team = [], [], [], [], [], []
        radiant_wr_with, dire_wr_with, radiant_pos3_vs_team, dire_pos3_vs_team, radiant_wr_against, dire_wr_against, radiant_pos1_vs_team, dire_pos1_vs_team, radiant_pos2_vs_team, dire_pos2_vs_team, radiant_pos4_with_pos5, dire_pos4_with_pos5 = [], [], [], [], [], [], [], [], [], [], None, None
        positions = ['1', '2', '3', '4']
        #radiant_synergy
        for dig in positions:
            try:
                hero_data = data[str(radiant_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_'+ dig]['synergy_duo']
                copy_radiant_heroes_and_positions = radiant_heroes_and_positions.copy()
                copy_radiant_heroes_and_positions.pop('pos ' + dig)
                a = [[pos, item['hero_id']] for pos, item in copy_radiant_heroes_and_positions.items()]
                id_pos = {str(item[1]): item[0] for item in a}
                for another_hero_id in hero_data:
                        # Extract the values of 'data-hero', 'data-wr', and 'data-pos' attributes
                    if dig == '1':
                        if len(radiant_pos1_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos1_with_team.append(wr)
                        except: pass
                    elif dig == '2':
                        if len(radiant_pos2_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            if position_name.replace('POSITION_', '') in ['3', '4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    radiant_pos2_with_team.append(wr)
                        except: pass
                    elif dig == '3':
                        if len(radiant_pos3_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            if position_name.replace('POSITION_', '') in ['4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    radiant_pos3_with_team.append(wr)
                        except: pass
                    elif dig == '4':
                        if len(radiant_pos3_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            if position_name.replace('POSITION_', '') == '5':
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
        for dig in positions:
            try:
                hero_data = data[str(dire_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_' + dig]['synergy_duo']
                copy_dire_heroes_and_positions = dire_heroes_and_positions.copy()
                copy_dire_heroes_and_positions.pop('pos ' + dig)
                a = [[pos, item['hero_id']] for pos, item in copy_dire_heroes_and_positions.items()]
                id_pos = {str(item[1]): item[0] for item in a}
                for another_hero_id in hero_data:
                    if dig == '1':
                        if len(dire_pos1_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos1_with_team.append(wr)
                        except:
                            pass
                    elif dig == '2':
                        if len(dire_pos2_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            if position_name.replace('POSITION_', '') in ['3', '4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    dire_pos2_with_team.append(wr)
                        except:
                            pass
                    elif dig == '3':
                        if len(dire_pos3_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            if position_name.replace('POSITION_', '') in ['4', '5']:
                                values = hero_data[another_hero_id][position_name]['value']
                                if len(values) >= 4:
                                    wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                    dire_pos3_with_team.append(wr)
                        except:
                            pass
                    elif dig == '4':
                        if len(dire_pos3_with_team) == 4:
                            break
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            if position_name.replace('POSITION_', '') == '5':
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
        for dig in positions:
            try:
                hero_data = data[str(radiant_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_' + dig]['counterpick_duo']
                a = [[pos, item['hero_id']] for pos, item in dire_heroes_and_positions.items()]
                id_pos = {str(item[1]): item[0] for item in a}
                for another_hero_id in hero_data:
                    if dig == '1':
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                if position_name == 'POSITION_1':
                                    core_matchup = wr
                                radiant_pos1_vs_team.append(wr)
                        except: pass
                    elif dig == '2':
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos2_vs_team.append(wr)
                        except:
                            pass
                    elif dig == '3':
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                radiant_pos3_vs_team.append(wr)
                        except:
                            pass
            except: pass
            #dire
            try:
                hero_data = data[str(dire_heroes_and_positions['pos ' + dig]['hero_id'])]['POSITION_' + dig][
                    'counterpick_duo']

                a = [[pos, item['hero_id']] for pos, item in dire_heroes_and_positions.items()]
                id_pos = {str(item[1]): item[0] for item in a}
                for another_hero_id in hero_data:
                    if dig == '1':
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos1_vs_team.append(wr)
                        except:
                            pass
                    elif dig == '2':
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
                            values = hero_data[another_hero_id][position_name]['value']
                            if len(values) >= 4:
                                wr = (values.count(1) / (values.count(1) + values.count(0)))*100
                                dire_pos2_vs_team.append(wr)
                        except:
                            pass
                    elif dig == '3':
                        try:
                            position_name = id_pos[another_hero_id].replace('pos ', 'POSITION_')
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
            sinergy = (sum(radiant_wr_with) / len(radiant_wr_with)) - (sum(dire_wr_with) / len(dire_wr_with))
        if len(radiant_wr_against) > 0 and len(dire_wr_against) > 0:
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
        output_message += (f'\nMy protracker: {verdict}\nSinergy: {sinergy}\nCounterpick: {counterpick}\nPos1_vs_team: {pos1_vs_team}\nPos2_vs_team: {pos2_vs_team}\nPos3_vs_team: {pos3_vs_team}\nCore matchup: {core_matchup}\nSups: {sups}\n')

    return output_message



def avg_over45(heroes_and_positions, data):
    print('avg_over45')
    over45_duo, over45_trio, time_duo, kills_duo, kills_trio, time_trio, radiant_lane_report_unique_combinations, dire_lane_report_unique_combinations = [], [], [], [], [], [], [], []
    over45_unique_combinations = set()
    positions = ['1', '2', '3', '4']
    for dig in positions:
        try:
            hero_id = str(heroes_and_positions['pos ' + dig]['hero_id'])
            hero_data = data[hero_id]['POSITION_' + dig]['over45_duo']
            for pos, item in heroes_and_positions.items():
                second_hero_id = str(item['hero_id'])
                try:
                    if second_hero_id != hero_id:
                        duo_data = hero_data[second_hero_id][pos.replace('pos ', 'POSITION_')]
                        combo = tuple(sorted([hero_id, second_hero_id]))
                        if combo not in over45_unique_combinations:
                            over45_unique_combinations.add(combo)
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
                                        over45_trio.append(sum(duo_data['value']) / len(duo_data['value']))
                                except:
                                    pass
                except:
                    pass
        except:
            pass
    avg_over45_duo = calculate_average(over45_duo)
    avg_over45_trio = calculate_average(over45_trio)
    avg_over45 = (avg_over45_duo + avg_over45_trio) / 2 if avg_over45_trio and avg_over45_duo else avg_over45_duo
    return avg_over45

def analyze_players(my_team, enemy_team, heroes_data):
    print('analyze_players')
    avg_kills, avg_time, team_line_report, over35, over40, over45, over50, over55 = [], [], [], [], [], [], [], []
    copy_team_pos_and_heroes = {}
    for pos, data in my_team.items():
        copy_team_pos_and_heroes[data['hero_id']] = pos
    for hero_id in copy_team_pos_and_heroes:
        pos = copy_team_pos_and_heroes[hero_id].replace('pos ', 'POSITION_')
        data = heroes_data[str(hero_id)]
        hero_name = translate[hero_id]
        if pos in data:
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
    team_avg_lanes = sum(team_line_report) / len(team_line_report)
    return team_avg_lanes
def tm_kills(radiant_heroes_and_positions, dire_heroes_and_positions):
    print('tm_kills')
    positions = ['1', '2', '3', '4']
    over45_duo, over45_trio, time_duo, kills_duo, kills_trio, time_trio = [], [], [], [], [], []
    avg_time_trio, avg_time_duo, avg_kills_duo, avg_kills_trio, radiant_time_unique_combinations, radiant_kills_unique_combinations, dire_kills_unique_combinations, dire_time_unique_combinations, radiant_over45_unique_combinations, dire_over45_unique_combinations = [], [], [], [], set(), set(), set(), set(), set(), set()
    with open('heroes_data_pros.txt', 'r') as f:
        data = json.load(f)
        avg_kills, avg_time = [], []
        # radiant_synergy
        for dig in positions:
            try:
                hero_id = str(radiant_heroes_and_positions['pos ' + dig]['hero_id'])
                time_data = data[hero_id]['POSITION_' + dig]['total_time_duo']
                kills_data = data[hero_id]['POSITION_' + dig]['total_kills_duo']
                for hero_data in [time_data, kills_data]:
                    for pos, item in radiant_heroes_and_positions.items():
                        second_hero_id = str(item['hero_id'])
                        try:
                            if second_hero_id != hero_id:
                                duo_data = hero_data[second_hero_id][pos.replace('pos ', 'POSITION_')]
                                combo = tuple(sorted([hero_id, second_hero_id]))
                                if hero_data == time_data:
                                    if combo not in radiant_time_unique_combinations:
                                        radiant_time_unique_combinations.add(combo)
                                        time_duo.append((sum(duo_data['value']) / len(duo_data['value'])) / 60)
                                elif hero_data == kills_data:
                                    if combo not in radiant_kills_unique_combinations:
                                        radiant_kills_unique_combinations.add(combo)
                                        kills_duo.append(sum(duo_data['value']) / len(duo_data['value']))
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
                                                    trio_data = duo_data['total_time_trio'][third_hero_id][
                                                        pos3.replace('pos ', 'POSITION_')]
                                                    time_trio.append((sum(trio_data) / len(trio_data)) / 60)
                                            elif hero_data == kills_data:
                                                if combo not in radiant_kills_unique_combinations:
                                                    radiant_kills_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_kills_trio'][third_hero_id][
                                                        pos3.replace('pos ', 'POSITION_')]
                                                    kills_trio.append(sum(trio_data) / len(trio_data))

                                        except:
                                            pass
                        except:
                            pass
            except:
                pass
            try:
                hero_id = str(dire_heroes_and_positions['pos ' + dig]['hero_id'])
                time_data = data[hero_id]['POSITION_' + dig][
                    'total_time_duo']
                kills_data = data[hero_id]['POSITION_' + dig][
                    'total_kills_duo']
                over_45_data = data[hero_id]['POSITION_' + dig]['over45_duo']
                for hero_data in [time_data, kills_data]:
                    for pos, item in dire_heroes_and_positions.items():
                        second_hero_id = str(item['hero_id'])
                        try:
                            if second_hero_id != hero_id:
                                duo_data = hero_data[second_hero_id][pos.replace('pos ', 'POSITION_')]
                                combo = tuple(sorted([hero_id, second_hero_id]))
                                if hero_data == time_data:
                                    if combo not in dire_time_unique_combinations:
                                        dire_time_unique_combinations.add(combo)
                                        avg_time_duo.append((sum(duo_data['value']) / len(duo_data['value'])) / 60)
                                elif hero_data == kills_data:
                                    if combo not in dire_kills_unique_combinations:
                                        dire_kills_unique_combinations.add(combo)
                                        trio_data = duo_data['total_kills_trio'][third_hero_id][
                                            pos3.replace('pos ', 'POSITION_')]
                                        avg_kills_duo.append(sum(duo_data['value']) / len(duo_data['value']))

                                # third_hero
                                for pos3, item3 in dire_heroes_and_positions.items():
                                    third_hero_id = str(item3['hero_id'])
                                    if third_hero_id != hero_id:
                                        try:
                                            combo = tuple(sorted([hero_id, second_hero_id, third_hero_id]))
                                            if hero_data == time_data:
                                                if combo not in dire_time_unique_combinations:
                                                    dire_time_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_time_trio'][third_hero_id][
                                                        pos3.replace('pos ', 'POSITION_')]
                                                    avg_time_trio.append((sum(trio_data) / len(trio_data)) / 60)
                                            elif hero_data == kills_data:
                                                if combo not in dire_kills_unique_combinations:
                                                    dire_kills_unique_combinations.add(combo)
                                                    trio_data = duo_data['total_kills_trio'][third_hero_id][
                                                        pos3.replace('pos ', 'POSITION_')]
                                                    avg_kills_trio.append(sum(trio_data) / len(trio_data))

                                        except:
                                            pass

                        except:
                            pass
            except: pass

    def calculate_average(values):
        return sum(values) / len(values) if values else 0

    avg_time_trio = calculate_average(time_trio)
    avg_kills_trio = calculate_average(kills_trio)
    avg_time_duo = calculate_average(time_duo)
    avg_kills_duo = calculate_average(kills_duo)

    avg_kills = (avg_kills_trio + avg_kills_duo) / 2 if avg_kills_trio and avg_kills_duo else avg_kills_duo
    avg_time = (avg_time_duo + avg_time_trio) / 2 if avg_time_trio and avg_time_duo else avg_time_duo

    return avg_kills, avg_time
