import json

import requests
import id_to_name
from dltv_cyberscore import if_unique, send_message
from keys import api_token

url = "https://egb.com/bets"
params = {
    "active": "true",
    "st": "1714418601",
    "ut": "1714418584"
}

headers = {
    "Host": "egb.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-CSRF-Token": "UUu1IL8sY0iZFFc2_FYI4ICk-WT34IRRGjz19DND8CbKEJZ9zTvbeAdcw72OYEecZiDlBaZimaYP-VuJwtmkAQ",
    "DNT": "1",
    "Sec-GPC": "1",}

players_to_add = set()
def get_players(bet):
    dire_and_radiant = {}
    players = [player for player in bet['game_label'].lower().replace(' team', '').split(' vs ')]
    player_names = [player.replace("'s", '') for player in players if 'enemy' not in player]
    dire_and_radiant['radiant'] = players[0]
    dire_and_radiant['dire'] = players[1]
    print(bet['game_label'])
    players_ids = []
    if len(player_names) == 2:
        if player_names[0] not in id_to_name.blacklist_players and player_names[1] not in id_to_name.blacklist_players:
            if player_names[0] in id_to_name.egb or player_names[1] in id_to_name.egb:
                if player_names[0] in id_to_name.egb:
                    for player in id_to_name.egb[player_names[0]]['steamId']:
                        players_ids.append(player)
                elif player_names[1] in id_to_name.egb:
                    for player in id_to_name.egb[player_names[1]]['steamId']:
                        players_ids.append(player)
            else:
                data = id_to_name.add_players
                if any(player not in data for player in player_names):
                    if player_names[0] not in players_to_add:
                        players_to_add.add(player_names[0])
                        send_message(f'{player_names[0]} не найден')
                    if player_names[1] not in players_to_add:
                        players_to_add.add(player_names[1])
                        send_message(f'{player_names[1]} не найден')
                    return True
        else:
            print('blacklisted')
            return True
    elif len(player_names) == 1:
        if player_names[0] not in id_to_name.blacklist_players:
            if player_names[0] in id_to_name.egb:
                for player in id_to_name.egb[player_names[0]]['steamId']:
                    players_ids.append(player)
            else:

                if player_names[0] not in players_to_add:
                    players_to_add.add(player_names[0])
                    send_message(f'{player_names[0]} не найден')
                    return True
        else:
            print('blacklisted')
            return True
    return players_ids, dire_and_radiant


def spread_heroes_left(heroes_left, radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid):
    for player in heroes_left:
        if player['isRadiant']:
            if len(radiant_hard) == 1:
                radiant_hard.append(player)
            elif len(radiant_safe) == 1:
                radiant_safe.append(player)
            elif len(radiant_mid) == 0:
                radiant_mid.append(player)
        elif not player['isRadiant']:
            if len(dire_hard) == 1:
                dire_hard.append(player)
            elif len(dire_safe) == 1:
                dire_safe.append(player)
            elif len(dire_mid) == 0:
                dire_mid.append(player)
    return radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid


def get_strats_graph_match(map_id=None):
    if map_id is None:
        query = '''{
          live{
            matches(request:{gameStates:GAME_IN_PROGRESS, isParsing:true, isCompleted: false, orderBy:SPECTATOR_COUNT, take: 100}){
              matchId
              players{
                numLastHits
                playbackData{
                  positionEvents{
                    time
                    x
                    y
                  }
                }
                heroId
                steamAccountId
                position
                isRadiant
                steamAccount{
                  name
                }
              }

            }


          }
        }

        '''
    else:
        query = '''{
          live{
            match(id:%s){
              players{
              steamAccountId
            heroId
            isRadiant
            networth
            playbackData{
            goldEvents{
            networth
            time
          }
          csEvents{
            time
          }
          positionEvents{
            time
            x
            y
          }
        }
      }
    }


  }
}
        '''%map_id
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.post('https://api.stratz.com/graphql', json={"query": query}, headers=headers)
    return response


def get_exac_match(response, players_ids, exac_match=None):
    if response.status_code == 200:
        data = json.loads(response.text)['data']['live']['matches']
        for match in data:
            for player in match['players']:
                if player['steamAccountId'] in players_ids:
                    exac_match = match
                    return exac_match

def know_the_position(radiant_safe, check_time, radiant_hard, radiant_mid, dire_safe, dire_hard, dire_mid, heroes_left, radiant, dire, output_message, R_pos_strng, D_pos_strng):
    if len(radiant_safe) == 2:
        zero_networth, first_networth, zero_cs, first_cs = 0, 0, 0, 0
        for event in radiant_safe[0]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                zero_networth = event['networth']
                break
        for event in radiant_safe[1]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                first_networth = event['networth']
                break

        for event in radiant_safe[0]['playbackData']['csEvents']:
            if event['time'] < check_time:
                zero_cs += 1
            else:
                break
        for event in radiant_safe[1]['playbackData']['csEvents']:
            if event['time'] < check_time:
                first_cs += 1
            else:
                break
        if zero_networth > first_networth and zero_cs > first_cs:
            for player in id_to_name.egb:
                if radiant_safe[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 5' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_safe[1]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_safe[1]["heroId"]]} pos 5'
                elif radiant_safe[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 1' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_safe[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_safe[0]["heroId"]]} pos 1'
            radiant['pos 1'] = {'hero_id': radiant_safe[0]['heroId'], 'hero_name': id_to_name.translate[radiant_safe[0]['heroId']], 'steamAccountId' : radiant_safe[0]['steamAccountId']}
            radiant['pos 5'] = {'hero_id': radiant_safe[1]['heroId'], 'hero_name': id_to_name.translate[radiant_safe[1]['heroId']], 'steamAccountId' : radiant_safe[1]['steamAccountId']}
        elif zero_networth < first_networth and zero_cs < first_cs:
            for player in id_to_name.egb:
                if radiant_safe[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 1' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_safe[1]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_safe[1]["heroId"]]} pos 1'
                elif radiant_safe[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 5' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_safe[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_safe[0]["heroId"]]} pos 5'
            radiant['pos 1'] = {'hero_id': radiant_safe[1]['heroId'] , 'hero_name': id_to_name.translate[radiant_safe[1]['heroId']], 'steamAccountId' : radiant_safe[1]['steamAccountId']}
            radiant['pos 5'] = {'hero_id': radiant_safe[0]['heroId'], 'hero_name': id_to_name.translate[radiant_safe[0]['heroId']], 'steamAccountId' : radiant_safe[0]['steamAccountId']}
    if len(radiant_hard) == 2:
        zero_networth, first_networth, zero_cs, first_cs = 0, 0, 0, 0
        for event in radiant_hard[0]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                zero_networth = event['networth']
                break
        for event in radiant_hard[1]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                first_networth = event['networth']
                break
        for event in radiant_hard[0]['playbackData']['csEvents']:
            if event['time'] < check_time:
                zero_cs += 1
            else:
                break
        for event in radiant_hard[1]['playbackData']['csEvents']:
            if event['time'] < check_time:
                first_cs += 1
            else:
                break
        if zero_networth > first_networth and zero_cs > first_cs:
            for player in id_to_name.egb:
                if radiant_hard[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 4' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_hard[1]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_hard[1]["heroId"]]} pos 4'
                elif radiant_hard[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 3' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_hard[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_hard[0]["heroId"]]} pos 3'


            radiant['pos 3'] = {'hero_id': radiant_hard[0]['heroId'], 'hero_name': id_to_name.translate[radiant_hard[0]['heroId']], 'steamAccountId' : radiant_hard[0]['steamAccountId']}
            radiant['pos 4'] = {'hero_id': radiant_hard[1]['heroId'], 'hero_name': id_to_name.translate[radiant_hard[1]['heroId']], 'steamAccountId' : radiant_hard[1]['steamAccountId']}
        elif zero_networth < first_networth and zero_cs < first_cs:
            for player in id_to_name.egb:
                if radiant_hard[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 3' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_hard[1]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_hard[1]["heroId"]]} pos 3'
                elif radiant_hard[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 4' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_hard[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_hard[0]["heroId"]]} pos 4'

            radiant['pos 3']= {'hero_id': radiant_hard[1]['heroId'], 'hero_name': id_to_name.translate[radiant_hard[1]['heroId']], 'steamAccountId' : radiant_hard[1]['steamAccountId']}
            radiant['pos 4']= {'hero_id': radiant_hard[0]['heroId'], 'hero_name': id_to_name.translate[radiant_hard[0]['heroId']], 'steamAccountId' : radiant_hard[0]['steamAccountId']}
    if len(dire_safe) == 2:
        zero_networth, first_networth, zero_cs, first_cs = 0, 0, 0, 0
        for event in dire_safe[0]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                zero_networth = event['networth']
                break
        for event in dire_safe[1]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                first_networth = event['networth']
                break
        for event in dire_safe[0]['playbackData']['csEvents']:
            if event['time'] < check_time:
                zero_cs += 1
            else:
                break
        for event in dire_safe[1]['playbackData']['csEvents']:
            if event['time'] < check_time:
                first_cs += 1
            else:
                break
        if zero_networth > first_networth and zero_cs > first_cs:
            for player in id_to_name.egb:
                if dire_safe[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 5' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_safe[0]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_safe[1]["heroId"]]} pos 5'
                elif dire_safe[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 1' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_safe[0]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_safe[0]["heroId"]]} pos 1'
            dire['pos 1']= {'hero_id': dire_safe[0]['heroId'], 'hero_name': id_to_name.translate[dire_safe[0]['heroId']], 'steamAccountId' : dire_safe[0]['steamAccountId']}
            dire['pos 5']= {'hero_id': dire_safe[1]['heroId'], 'hero_name': id_to_name.translate[dire_safe[1]['heroId']], 'steamAccountId' : dire_safe  [1]['steamAccountId']}
        if zero_networth < first_networth and zero_cs < first_cs:
            for player in id_to_name.egb:
                if dire_safe[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 1' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_safe[1]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_safe[1]["heroId"]]} pos 1'
                elif dire_safe[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 5' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_safe[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[dire_safe[0]["heroId"]]} pos 5'
            dire['pos 1']= {'hero_id': dire_safe[1]['heroId'], 'hero_name': id_to_name.translate[dire_safe[1]['heroId']], 'steamAccountId' : dire_safe[1]['steamAccountId']}
            dire['pos 5']= {'hero_id': dire_safe[0]['heroId'], 'hero_name': id_to_name.translate[dire_safe[0]['heroId']], 'steamAccountId' : dire_safe[0]['steamAccountId']}
    if len(dire_hard) == 2:
        zero_networth, first_networth, zero_cs, first_cs = 0, 0, 0, 0
        for event in dire_hard[0]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                zero_networth = event['networth']
                break
        for event in dire_hard[1]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                first_networth = event['networth']
                break
        for event in dire_hard[0]['playbackData']['csEvents']:
            if event['time'] < check_time:
                zero_cs += 1
            else:
                break
        for event in dire_hard[1]['playbackData']['csEvents']:
            if event['time'] < check_time:
                first_cs += 1
            else:
                break
        if zero_networth > first_networth and zero_cs > first_cs:
            for player in id_to_name.egb:
                if dire_hard[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 4' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_hard[1]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_hard[1]["heroId"]]} pos 4'
                elif dire_hard[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 3' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_hard[0]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_hard[0]["heroId"]]} pos 3'

            dire['pos 3']= {'hero_id': dire_hard[0]['heroId'], 'hero_name': id_to_name.translate[dire_hard[0]['heroId']], 'steamAccountId' : dire_hard[0]['steamAccountId']}
            dire['pos 4']= {'hero_id': dire_hard[1]['heroId'], 'hero_name': id_to_name.translate[dire_hard[1]['heroId']], 'steamAccountId' : dire_hard[1]['steamAccountId']}
        elif zero_networth < first_networth and zero_cs < first_cs:
            for player in id_to_name.egb:
                if dire_hard[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 3' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_hard[1]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_hard[1]["heroId"]]} pos 3'
                elif dire_hard[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 4' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_hard[0]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_hard[0]["heroId"]]} pos 4'

            dire['pos 3']= {'hero_id': dire_hard[1]['heroId'], 'hero_name': id_to_name.translate[dire_hard[1]['heroId']], 'steamAccountId' : dire_hard[1]['steamAccountId']}
            dire['pos 4']= {'hero_id': dire_hard[0]['heroId'], 'hero_name': id_to_name.translate[dire_hard[0]['heroId']], 'steamAccountId' : dire_hard[0]['steamAccountId']}
    if len(radiant_mid) == 1:
        for player in id_to_name.egb:
            if radiant_mid[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                if 'pos 2' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                    R_pos_strng[radiant_mid[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_mid[0]["heroId"]]} pos 2'
        radiant['pos 2']= {'hero_id': radiant_mid[0]['heroId'], 'hero_name': id_to_name.translate[radiant_mid[0]['heroId']], 'steamAccountId' : radiant_mid[0]['steamAccountId']}
    elif len(radiant_mid) == 2:
        zero_networth, first_networth, zero_cs, first_cs = 0, 0, 0, 0
        for event in radiant_mid[0]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                zero_networth = event['networth']
                break
        for event in radiant_mid[1]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                first_networth = event['networth']
                break
        for event in radiant_mid[0]['playbackData']['csEvents']:
            if event['time'] < check_time:
                zero_cs += 1
            else:
                break
        for event in radiant_mid[1]['playbackData']['csEvents']:
            if event['time'] < check_time:
                first_cs += 1
            else:
                break
        if zero_networth > first_networth and zero_cs > first_cs:
            for player in id_to_name.egb:
                if radiant_mid[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 2' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_mid[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_mid[0]["heroId"]]} pos 2'

            radiant['pos 2']= {'hero_id': radiant_mid[0]['heroId'], 'hero_name': id_to_name.translate[radiant_mid[0]['heroId']], 'steamAccountId' : radiant_mid[0]['steamAccountId']}
            heroes_left.append(radiant_mid[1])
        elif zero_networth < first_networth and zero_cs < first_cs:
            for player in id_to_name.egb:
                if radiant_mid[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 2' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        R_pos_strng[radiant_mid[1]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[radiant_mid[1]["heroId"]]} pos 2'

            radiant['pos 2']= {'hero_id': radiant_mid[1]['heroId'], 'hero_name': id_to_name.translate[radiant_mid[1]['heroId']], 'steamAccountId' : radiant_mid[1]['steamAccountId']}
            heroes_left.append(radiant_mid[0])
    if len(dire_mid) == 1:
        for player in id_to_name.egb:
            if dire_mid[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                if 'pos 2' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                    D_pos_strng[dire_mid[0]['steamAccountId']] = f'{player} играет не на своей роли:{id_to_name.translate[dire_mid[0]["heroId"]]} pos 2'

        dire['pos 2']= {'hero_id': dire_mid[0]['heroId'], 'hero_name': id_to_name.translate[dire_mid[0]['heroId']], 'steamAccountId' : dire_mid[0]['steamAccountId']}
    elif len(dire_mid) == 2:
        zero_networth, first_networth, zero_cs, first_cs = 0, 0, 0, 0
        for event in dire_mid[0]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                zero_networth = event['networth']
                break
        for event in dire_mid[1]['playbackData']['goldEvents']:
            if event['time'] > check_time:
                first_networth = event['networth']
                break
        for event in dire_mid[0]['playbackData']['csEvents']:
            if event['time'] < check_time:
                zero_cs += 1
            else:
                break
        for event in dire_mid[1]['playbackData']['csEvents']:
            if event['time'] < check_time:
                first_cs += 1
            else:
                break
        if zero_networth > first_networth and zero_cs > first_cs:
            for player in id_to_name.egb:
                if dire_mid[0]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 2' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_mid[0]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[dire_mid[0]["heroId"]]} pos 2'

            dire['pos 2']= {'hero_id': dire_mid[0]['heroId'], 'hero_name': id_to_name.translate[dire_mid[0]['heroId']], 'steamAccountId' : dire_mid[0]['steamAccountId']}
            heroes_left.append(dire_mid[1])
        elif zero_networth < first_networth and zero_cs < first_cs:
            for player in id_to_name.egb:
                if dire_mid[1]['steamAccountId'] in id_to_name.egb[player]['steamId']:
                    if 'pos 2' not in id_to_name.egb[player]['position'] and len( id_to_name.egb[player]['position']) != 0:
                        D_pos_strng[dire_mid[1]['steamAccountId']] = f'{player} играет не на своей роли: {id_to_name.translate[dire_mid[1]["heroId"]]} pos 2'
            dire['pos 2']= {'hero_id': dire_mid[1]['heroId'], 'hero_name': id_to_name.translate[dire_mid[1]['heroId']], 'steamAccountId' : dire_mid[1]['steamAccountId']}
            heroes_left.append(dire_mid[0])
    return radiant, dire, heroes_left, output_message, R_pos_strng, D_pos_strng




def get_picks(check_time, players):

    radiant, dire, heroes_left, index, D_pos_strng, R_pos_strng = {}, {}, [], None,  {}, {}
    radiant_hard, radiant_safe, dire_hard, dire_safe, radiant_mid, dire_mid = [], [], [], [], [], []
    for player in players:
        coordinates = player['playbackData']['positionEvents']
        for time in coordinates:
            if time['time'] >= check_time:
                if time['x'] > 90 and time['x'] < 150 and time['y'] > 110 and time['y'] < 150:
                    if player['isRadiant']:
                        radiant_mid.append(player)
                        break
                    else:
                        dire_mid.append(player)
                        break
                elif time['x'] > 70 and time['x'] < 110 and time['y'] > 130 and time['y'] < 170:
                    if player['isRadiant']:
                        radiant_hard.append(player)
                        break
                    else:
                        dire_safe.append(player)
                        break
                elif time['x'] > 120 and time['x'] < 180 and time['y'] > 70 and time['y'] < 120:
                    if not player['isRadiant']:
                        dire_hard.append(player)
                        break
                    else:
                        radiant_safe.append(player)
                        break
                else:
                    heroes_left.append(player)
                    break
    output_message=''
    radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid = spread_heroes_left(heroes_left, radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid)
    radiant, dire, heroes_left, output_message,R_pos_strng, D_pos_strng = know_the_position(radiant_safe, check_time, radiant_hard, radiant_mid, dire_safe, dire_hard, dire_mid, heroes_left, radiant, dire, output_message,R_pos_strng, D_pos_strng)
    radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid = spread_heroes_left(heroes_left, radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid)
    radiant, dire, heroes_left, output_message,R_pos_strng, D_pos_strng = know_the_position(radiant_safe, check_time, radiant_hard, radiant_mid, dire_safe, dire_hard, dire_mid, heroes_left, radiant, dire, output_message,R_pos_strng, D_pos_strng)
    positions = ['pos 1', 'pos 2', 'pos 3', 'pos 4', 'pos 5']
    if len(radiant) == 4:
        positions_copy = positions.copy()
        for key in radiant:
            positions_copy.remove(key)
        for player in heroes_left:
            if player['isRadiant']:
                radiant[positions_copy[0]]= {'hero_id':player['heroId'] , 'hero_name': id_to_name.translate[player['heroId']], 'steamAccountId' : player['steamAccountId']}

    if len(dire) == 4:
        positions_copy = positions.copy()
        for key in dire:
            positions_copy.remove(key)
        for player in heroes_left:
            if not player['isRadiant']:
                radiant[positions_copy[0]]= {'hero_id': player['heroId'], 'hero_name': id_to_name.translate[player['heroId']], 'steamAccountId' : player['steamAccountId']}
    return radiant, dire, output_message, R_pos_strng, D_pos_strng



def get_picks_and_pos(match_id):
    if if_unique(match_id) is not None:
        response = get_strats_graph_match(match_id)
        players = json.loads(response.text)['data']['live']['match']['players']
        check_time = 75
        while check_time < 400:
            radiant, dire, output_message, R_pos_strng, D_pos_strng = get_picks(check_time, players)
            radiant_heroes = set([item['hero_name'] for pos, item, in radiant.items()])
            dire_heroes = set([item['hero_name'] for pos, item, in dire.items()])
            if len(radiant_heroes) == 5 and len(dire_heroes) == 5:
                return radiant, dire, match_id, output_message, R_pos_strng, D_pos_strng
            else:
                check_time += 15
        print('неудалось выяснить пики')
        return True
    else:
        print('карта уже расчитана')


def check_players_skill(radiant, dire, output_message, R_pos_strng, D_pos_strng):
    radiant_errors_len, dire_errors_len = 0, 0
    radiant_steam_account_ids = [player['steamAccountId'] for player in radiant.values()]
    dire_steam_account_ids = [player['steamAccountId'] for player in dire.values()]
    radiant_hero_ids = [player['hero_id'] for player in radiant.values()]
    dire_hero_ids = [player['hero_id'] for player in dire.values()]
    #radaint
    radiant_impact, dire_impact, players_check = {},{},False
    for hero_ids, steam_account_ids in zip([radiant_hero_ids, dire_hero_ids], [radiant_steam_account_ids, dire_steam_account_ids]):
        player_query = '''
        {
          players(steamAccountIds:%s){
            steamAccountId
                simpleSummary{
              coreCount
              supportCount
              matchCount
            }
            heroesPerformance(request:{startDateTime:1715029200, take: 15,gameModeIds:[22,2], heroIds:%s,positionIds:[POSITION_1, POSITION_2, POSITION_3, POSITION_4, POSITION_5]}){
              positionScore{
                matchCount
                id
                imp
              }
              hero{
                id
              }
              
            }
        
        
          }
        }
         '''% (steam_account_ids, hero_ids)
        headers = {"Authorization": f"Bearer {api_token}"}
        response = requests.post('https://api.stratz.com/graphql', json={"query": player_query}, headers=headers)
        data = json.loads(response.text)
        for player in data['data']['players']:
            steam_account_id = player['steamAccountId']
            if player['steamAccountId'] in radiant_steam_account_ids:
                isRadiant = True
            elif player['steamAccountId'] in dire_steam_account_ids:
                isRadiant = False
            if isRadiant:
                for position in radiant:
                    if radiant[position]['steamAccountId'] == steam_account_id:
                        hero_id = radiant[position]['hero_id']
                        pos = position
            elif not isRadiant:
                for position in dire:
                    if dire[position]['steamAccountId'] == steam_account_id:
                        hero_id = dire[position]['hero_id']
                        pos = position
            for hero_perfomance in player['heroesPerformance']:
                check_hero_id = hero_perfomance['hero']['id']
                for position_score in hero_perfomance['positionScore']:
                    pos_found = position_score['id'].replace('POSITION_', '') == pos.replace('pos ', '')
                    if pos_found and check_hero_id == hero_id and position_score['matchCount'] >=2:
                        impact = position_score['imp']
                        if isRadiant:
                            radiant_impact[steam_account_id] = impact
                        else:
                            dire_impact[steam_account_id] = impact
        if isRadiant:
            if 'errors' in data:
                radiant_errors_len = len(data['errors'])
            for radiant_id in radiant_steam_account_ids:
                if radiant_id not in radiant_impact:
                    if 'errors' in data:
                        if not any(str(radiant_id) in error['message'] for error in data['errors']):
                            for pos in radiant:
                                if radiant[pos]['steamAccountId'] == radiant_id:
                                    if radiant_id not in R_pos_strng:
                                        R_pos_strng[radiant_id] = f'{radiant[pos]["hero_name"]} {pos} играет не на своей позиции'
                                        break
                    else:
                        for pos in radiant:
                            if radiant[pos]['steamAccountId'] == radiant_id:
                                if radiant_id not in R_pos_strng:
                                    R_pos_strng[radiant_id] = f'{radiant[pos]["hero_name"]} {pos} играет не на своей позиции'
                                    break

        elif not isRadiant:
            if 'errors' in data:
                dire_errors_len = len(data['errors'])
            for dire_id in dire_steam_account_ids:
                if dire_id not in dire_impact:
                    if 'errors' in data:
                        if not any(str(dire_id) in error['message'] for error in data['errors']):
                            for pos in dire:
                                if dire[pos]['steamAccountId'] == dire_id:
                                    if dire_id not in D_pos_strng:
                                        D_pos_strng[dire_id] = f'{dire[pos]["hero_name"]} {pos} играет не на своей позиции'
                                        break
                    else:
                        for pos in dire:
                            if dire[pos]['steamAccountId'] == dire_id:
                                if dire_id not in D_pos_strng:
                                    D_pos_strng[dire_id] = f'{dire[pos]["hero_name"]} {pos} играет не на своей позиции'
                                    break
    radiant_message_add, dire_message_add = 'Radiant:' ,'Dire:'
    if len(D_pos_strng) != 0:
        dire_message_add += ''.join(['\n· ' + message for message in D_pos_strng.values()])
    if len(R_pos_strng) != 0:
        radiant_message_add += ''.join(['\n· ' + message for message in R_pos_strng.values()])
    radiant_impactandplayers, dire_impactandplayers, radiant_players_check, dire_players_check, impact_message = False, False, False, False, None
    if len(dire_impact) != 0 and len(radiant_impact) != 0:
        radiant_message_add+=(f'\n· Найдено {len(radiant_impact)}/5 игроков, {radiant_errors_len} из которых скрытые')
        dire_message_add += (f'\n· Найдено {len(dire_impact)}/5 игроков, {dire_errors_len} из которых скрытые')
        radiant_average_impact = sum(radiant_impact.values())/len(radiant_impact)
        dire_average_impact = sum(dire_impact.values())/len(dire_impact)
        if radiant_average_impact > dire_average_impact:
            impact_diff = radiant_average_impact - dire_average_impact
            impact_message = (f'\nRadiant impact лучше в среднем на {impact_diff}')
            if len(R_pos_strng) < len(D_pos_strng):
                radiant_impactandplayers = True
                if impact_diff < 0: impact_diff *= -1
                if impact_diff >= 10:
                    radiant_players_check = True
            elif len(R_pos_strng) <= len(D_pos_strng):
                radiant_impactandplayers = True

        elif radiant_average_impact < dire_average_impact:
            impact_diff = dire_average_impact - radiant_average_impact
            impact_message = (f'\nDire impact лучше в среднем на {impact_diff}')
            if len(D_pos_strng) < len(R_pos_strng):
                dire_impactandplayers = True
                if impact_diff < 0: impact_diff *= -1
                if impact_diff >= 10:
                    dire_players_check = True
            elif len(D_pos_strng) <= len(R_pos_strng):
                dire_impactandplayers = True

        else:
            impact_diff = 0
    else:
        impact_diff = None
    return output_message, impact_diff, R_pos_strng, D_pos_strng, radiant_players_check, dire_players_check, radiant_impactandplayers, dire_impactandplayers, radiant_message_add, dire_message_add, impact_message
