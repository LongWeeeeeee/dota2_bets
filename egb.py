from id_to_name import translate
from keys import api_token
import json
import requests
import time
from dltv_cyberscore import dota2protracker, if_unique, add_url
import requests
from id_to_name import egb

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
    "Sec-GPC": "1",
}
def get_players(bet):
    dire_and_radiant = {}
    players = [player for player in bet['game_label'].lower().replace(' team', '').split(' vs ')]
    player_names = [player for player in players if 'enemy' not in player]
    dire_and_radiant['radiant'] = players[0]
    dire_and_radiant['dire'] = players[1]
    print(bet['game_label'])
    players_ids = [egb[player] for player in player_names]
    return players_ids, dire_and_radiant


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
                    heroId
                    isRadiant
                    numLastHits
                    playbackData{
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


def get_picks_and_pos(exac_match,):
    match_id = exac_match['matchId']
    if if_unique(match_id) is not None:
        response = get_strats_graph_match(match_id)
        players = json.loads(response.text)['data']['live']['match']['players']
        players = sorted(players, key=lambda x: x['numLastHits'], reverse=True)
        radiant_hard, radiant_safe, dire_hard, dire_safe, radiant_mid, dire_mid = [],[],[],[],[],[]
        radiant, dire, heroes_left, index = {}, {}, [], None
        for player in players:
            coordinates = player['playbackData']['positionEvents']
            for time in coordinates:
                if time['time']/60 > 2.5 and time['time']/60 < 8:
                    index = coordinates.index(time)
                    print(time['time']/60)
                    break
        if index is not None:
            try:
                for player in players:
                    hero = translate[player['heroId']]
                    coordinates = player['playbackData']['positionEvents']
                    if coordinates[index]['x'] > 90 and coordinates[index]['x'] < 150 and coordinates[index]['y'] > 110 and coordinates[index]['y'] < 150:
                        if player['isRadiant']:
                            radiant_mid.append(player)
                        else:
                            dire_mid.append(player)
                    elif coordinates[index]['x'] > 70 and coordinates[index]['x'] < 110 and coordinates[index]['y'] > 130 and coordinates[index]['y'] < 170:
                        if player['isRadiant']:
                            radiant_hard.append(player)
                        else:
                            dire_safe.append(player)
                    elif coordinates[index]['x'] > 120 and coordinates[index]['x'] < 180 and coordinates[index]['y'] > 70 and coordinates[index]['y'] < 120:
                        if not player['isRadiant']:
                            dire_hard.append(player)
                        else:
                            radiant_safe.append(player)

                    else:
                        heroes_left.append(player)
            except:
                return None

            for player in heroes_left:
                if player['isRadiant']:
                    if len(radiant_hard) != 2:
                        radiant_hard.append(player)
                    elif len(radiant_safe) != 2:
                        radiant_safe.append(player)
                    elif len(radiant_mid) == 0:
                        radiant_mid.append(player)
            for player in heroes_left:
                if not player['isRadiant']:
                    if len(dire_hard) != 2:
                        dire_hard.append(player)
                    elif len(dire_safe) != 2:
                        dire_safe.append(player)
                    elif len(dire_mid) == 0:
                        dire_mid.append(player)
            if len(radiant_safe) == 2:
                if radiant_safe[0]['numLastHits'] > radiant_safe[1]['numLastHits']:
                    radiant['pos 1'] = translate[radiant_safe[0]['heroId']]
                    radiant['pos 5'] = translate[radiant_safe[1]['heroId']]
                else:
                    radiant['pos 1'] = translate[radiant_safe[1]['heroId']]
                    radiant['pos 5'] = translate[radiant_safe[0]['heroId']]
            if len(radiant_hard) == 2:
                if radiant_hard[0]['numLastHits'] > radiant_hard[1]['numLastHits']:
                    radiant['pos 3'] = translate[radiant_hard[0]['heroId']]
                    radiant['pos 4'] = translate[radiant_hard[1]['heroId']]
                else:
                    radiant['pos 3'] = translate[radiant_hard[1]['heroId']]
                    radiant['pos 4'] = translate[radiant_hard[0]['heroId']]
            if len(dire_safe) == 2:
                if dire_safe[0]['numLastHits'] > dire_safe[1]['numLastHits']:
                    dire['pos 1'] = translate[dire_safe[0]['heroId']]
                    dire['pos 5'] = translate[dire_safe[1]['heroId']]
                else:
                    dire['pos 1'] = translate[dire_safe[1]['heroId']]
                    dire['pos 5'] = translate[dire_safe[0]['heroId']]
            if len(dire_hard) == 2:
                if dire_hard[0]['numLastHits'] > dire_hard[1]['numLastHits']:
                    dire['pos 3'] = translate[dire_hard[0]['heroId']]
                    dire['pos 4'] = translate[dire_hard[1]['heroId']]
                else:
                    dire['pos 3'] = translate[dire_hard[1]['heroId']]
                    dire['pos 4'] = translate[dire_hard[0]['heroId']]
            if len(radiant_mid) == 1:
                radiant['pos 2'] = translate[radiant_mid[0]['heroId']]
            else:
                if radiant_mid[0]['numLastHits'] > radiant_mid[1]['numLastHits']:
                    radiant['pos 2'] = translate[radiant_mid[0]['heroId']]
                    heroes_left.append(radiant_mid[1])
                else:
                    radiant['pos 2'] = translate[radiant_mid[1]['heroId']]
                    heroes_left.append(radiant_mid[0])
            if len(dire_mid) == 1:
                dire['pos 2'] = translate[dire_mid[0]['heroId']]
            else:
                if dire_mid[0]['numLastHits'] > dire_mid[1]['numLastHits']:
                    dire['pos 2'] = translate[dire_mid[0]['heroId']]
                    heroes_left.append(dire_mid[1])
                else:
                    dire['pos 2'] = translate[dire_mid[1]['heroId']]
                    heroes_left.append(dire_mid[0])
            for player in heroes_left:
                if player['isRadiant']:
                    if len(radiant_hard) != 2:
                        radiant_hard.append(player)
                    elif len(radiant_safe) != 2:
                        radiant_safe.append(player)
                    elif len(radiant_mid) == 0:
                        radiant_mid.append(player)
            for player in heroes_left:
                if not player['isRadiant']:
                    if len(dire_hard) != 2:
                        dire_hard.append(player)
                    elif len(dire_safe) != 2:
                        dire_safe.append(player)
                    elif len(dire_mid) == 0:
                        dire_mid.append(player)
            if len(radiant_safe) == 2:
                if radiant_safe[0]['numLastHits'] > radiant_safe[1]['numLastHits']:
                    radiant['pos 1'] = translate[radiant_safe[0]['heroId']]
                    radiant['pos 5'] = translate[radiant_safe[1]['heroId']]
                else:
                    radiant['pos 1'] = translate[radiant_safe[1]['heroId']]
                    radiant['pos 5'] = translate[radiant_safe[0]['heroId']]
            if len(radiant_hard) == 2:
                if radiant_hard[0]['numLastHits'] > radiant_hard[1]['numLastHits']:
                    radiant['pos 3'] = translate[radiant_hard[0]['heroId']]
                    radiant['pos 4'] = translate[radiant_hard[1]['heroId']]
                else:
                    radiant['pos 3'] = translate[radiant_hard[1]['heroId']]
                    radiant['pos 4'] = translate[radiant_hard[0]['heroId']]
            if len(dire_safe) == 2:
                if dire_safe[0]['numLastHits'] > dire_safe[1]['numLastHits']:
                    dire['pos 1'] = translate[dire_safe[0]['heroId']]
                    dire['pos 5'] = translate[dire_safe[1]['heroId']]
                else:
                    dire['pos 1'] = translate[dire_safe[1]['heroId']]
                    dire['pos 5'] = translate[dire_safe[0]['heroId']]
            if len(dire_hard) == 2:
                if dire_hard[0]['numLastHits'] > dire_hard[1]['numLastHits']:
                    dire['pos 3'] = translate[dire_hard[0]['heroId']]
                    dire['pos 4'] = translate[dire_hard[1]['heroId']]
                else:
                    dire['pos 3'] = translate[dire_hard[1]['heroId']]
                    dire['pos 4'] = translate[dire_hard[0]['heroId']]
            if len(radiant_mid) == 1:
                radiant['pos 2'] = translate[radiant_mid[0]['heroId']]
            else:
                if radiant_mid[0]['numLastHits'] > radiant_mid[1]['numLastHits']:
                    radiant['pos 2'] = translate[radiant_mid[0]['heroId']]
                    heroes_left.append(radiant_mid[1])
                else:
                    radiant['pos 2'] = translate[radiant_mid[1]['heroId']]
                    heroes_left.append(radiant_mid[0])
            if len(dire_mid) == 1:
                dire['pos 2'] = translate[dire_mid[0]['heroId']]
            else:
                if dire_mid[0]['numLastHits'] > dire_mid[1]['numLastHits']:
                    dire['pos 2'] = translate[dire_mid[0]['heroId']]
                    heroes_left.append(dire_mid[1])
                else:
                    dire['pos 2'] = translate[dire_mid[1]['heroId']]
                    heroes_left.append(dire_mid[0])


        else:
            print('игра только началась или stratz Залагал')
            return None
    else:
        print('карта уже расчитана')
        return None
    positions = ['pos 1', 'pos 2', 'pos 3', 'pos 4', 'pos 5']
    if len(radiant) == 4:
        positions_copy = positions.copy()
        for key in radiant:
            positions_copy.remove(key)
        for player in heroes_left:
            if player['isRadiant']:
                radiant[positions_copy[0]] = translate[player['heroId']]

    if len(dire) == 4:
        positions_copy = positions.copy()
        for key in dire:
            positions_copy.remove(key)
        for player in heroes_left:
            if not player['isRadiant']:
                radiant[positions_copy[0]] = translate[player['heroId']]

    if len(radiant) == 5 and len(dire) == 5:
        print(f"https://stratz.com/matches/{match_id}/live\n{radiant}\n{dire}")
        return radiant, dire, match_id
    else:
        print(f'пики не полные\n{radiant}\n{dire}')


# response = get_strats_graph_match()
# data = json.loads(response.text)
# for match in data['data']['live']['matches']:
#     get_picks_and_pos(match)
while True:
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            for bet in data['bets']:
                if bet['esports'] and bet['streams_enabled'] and bet['game'] == 'Dota 2' and bet['tourn'] in ['Incubator','Ladder Games']:
                    players_ids, dire_and_radiant = get_players(bet)
                    response = get_strats_graph_match()
                    exac_match = get_exac_match(response, players_ids)
                    if exac_match is not None:
                        answer = get_picks_and_pos(exac_match)
                        if answer is not None:
                            radiant, dire, match_id = answer
                            dota2protracker(radiant_heroes_and_positions=radiant, dire_heroes_and_positions=dire, radiant_team_name=dire_and_radiant['radiant'], dire_team_name=dire_and_radiant['dire'], antiplagiat_url=match_id)
                    else:
                        print('карта не найдена, вероятно, матч только начался')
    except: pass
    print('сплю 2 минуты')
    time.sleep(120)