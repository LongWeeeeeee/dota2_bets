import id_to_name
import importlib
from keys import api_token
import json
import time
from dltv_cyberscore import dota2protracker, if_unique, send_message
import requests


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
    player_names = [player.replace("'s", '') for player in players if 'enemy' not in player]
    dire_and_radiant['radiant'] = players[0]
    dire_and_radiant['dire'] = players[1]
    print(bet['game_label'])
    players_ids = []
    if len(player_names) == 2:
        if player_names[0] not in id_to_name.blacklist_players and player_names[1] not in id_to_name.blacklist_players:
            if player_names[0] in id_to_name.egb or player_names[1] in id_to_name.egb:
                if player_names[0] in id_to_name.egb:
                    players_ids.append(id_to_name.egb[player_names[0]])
                elif player_names[1] in id_to_name.egb:
                    players_ids.append(id_to_name.egb[player_names[1]])
            else:
                print(f'{player_names[0]} и {player_names[1]} не найдны')
                send_message(f'{player_names[0]} и {player_names[1]} не найдны')
                return
        else:
            print('blacklisted')
            return True
    elif len(player_names) == 1:
        if player_names[0] not in id_to_name.blacklist_players:
            if player_names[0] in id_to_name.egb:
                players_ids.append(id_to_name.egb[player_names[0]])
            else:
                print(f'{player_names[0]} не найден')
                send_message(f'{player_names[0]} не найден')
                return
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

def know_the_position(radiant_safe, check_time, radiant_hard, radiant_mid, dire_safe, dire_hard, dire_mid, heroes_left, radiant, dire):
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
            radiant['pos 1'] = id_to_name.translate[radiant_safe[0]['heroId']]
            radiant['pos 5'] = id_to_name.translate[radiant_safe[1]['heroId']]
        elif zero_networth < first_networth and zero_cs < first_cs:
            radiant['pos 1'] = id_to_name.translate[radiant_safe[1]['heroId']]
            radiant['pos 5'] = id_to_name.translate[radiant_safe[0]['heroId']]
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
            radiant['pos 3'] = id_to_name.translate[radiant_hard[0]['heroId']]
            radiant['pos 4'] = id_to_name.translate[radiant_hard[1]['heroId']]
        if zero_networth < first_networth and zero_cs < first_cs:
            radiant['pos 3'] = id_to_name.translate[radiant_hard[1]['heroId']]
            radiant['pos 4'] = id_to_name.translate[radiant_hard[0]['heroId']]
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
            dire['pos 1'] = id_to_name.translate[dire_safe[0]['heroId']]
            dire['pos 5'] = id_to_name.translate[dire_safe[1]['heroId']]
        if zero_networth < first_networth and zero_cs < first_cs:
            dire['pos 1'] = id_to_name.translate[dire_safe[1]['heroId']]
            dire['pos 5'] = id_to_name.translate[dire_safe[0]['heroId']]
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
            dire['pos 3'] = id_to_name.translate[dire_hard[0]['heroId']]
            dire['pos 4'] = id_to_name.translate[dire_hard[1]['heroId']]
        if zero_networth < first_networth and zero_cs < first_cs:
            dire['pos 3'] = id_to_name.translate[dire_hard[1]['heroId']]
            dire['pos 4'] = id_to_name.translate[dire_hard[0]['heroId']]
    if len(radiant_mid) == 1:
        radiant['pos 2'] = id_to_name.translate[radiant_mid[0]['heroId']]
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
            radiant['pos 2'] = id_to_name.translate[radiant_mid[0]['heroId']]
            heroes_left.append(radiant_mid[1])
        if zero_networth < first_networth and zero_cs < first_cs:
            radiant['pos 2'] = id_to_name.translate[radiant_mid[1]['heroId']]
            heroes_left.append(radiant_mid[0])
    if len(dire_mid) == 1:
        dire['pos 2'] = id_to_name.translate[dire_mid[0]['heroId']]
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
            dire['pos 2'] = id_to_name.translate[dire_mid[0]['heroId']]
            heroes_left.append(dire_mid[1])
        if zero_networth < first_networth and zero_cs < first_cs:
            dire['pos 2'] = id_to_name.translate[dire_mid[1]['heroId']]
            heroes_left.append(dire_mid[0])
    return radiant, dire, heroes_left




def get_picks(check_time, players):
    radiant, dire, heroes_left, index = {}, {}, [], None
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

    radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid = spread_heroes_left(heroes_left, radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid)
    radiant, dire, heroes_left = know_the_position(radiant_safe, check_time, radiant_hard, radiant_mid, dire_safe, dire_hard, dire_mid, heroes_left, radiant, dire)
    radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid = spread_heroes_left(heroes_left, radiant_hard, radiant_safe, radiant_mid, dire_hard, dire_safe, dire_mid)
    radiant, dire, heroes_left = know_the_position(radiant_safe, check_time, radiant_hard, radiant_mid, dire_safe, dire_hard, dire_mid, heroes_left, radiant, dire)
    positions = ['pos 1', 'pos 2', 'pos 3', 'pos 4', 'pos 5']
    if len(radiant) == 4:
        positions_copy = positions.copy()
        for key in radiant:
            positions_copy.remove(key)
        for player in heroes_left:
            if player['isRadiant']:
                radiant[positions_copy[0]] = id_to_name.translate[player['heroId']]

    if len(dire) == 4:
        positions_copy = positions.copy()
        for key in dire:
            positions_copy.remove(key)
        for player in heroes_left:
            if not player['isRadiant']:
                radiant[positions_copy[0]] = id_to_name.translate[player['heroId']]
    return radiant, dire



def get_picks_and_pos(match_id):
    if if_unique(match_id) is not None:
        response = get_strats_graph_match(match_id)
        players = json.loads(response.text)['data']['live']['match']['players']
        check_time = 75
        while check_time < 400:
            radiant, dire = get_picks(check_time, players)
            if len(radiant) == 5 and len(dire) == 5:
                print(f"https://stratz.com/matches/{match_id}/live")
                return radiant, dire, match_id
            else:
                check_time += 15
        print('неудалось выяснить пики')
        return True
    else:
        print('карта уже расчитана')


while True:
    map = False
    importlib.reload(id_to_name)
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        for bet in data['bets']:
            if bet['esports'] and bet['streams_enabled'] and bet['game'] == 'Dota 2' and bet['tourn'] in ['Incubator','Ladder Games']:
                answer = get_players(bet)
                if answer is not None:
                    if answer != True:
                        players_ids, dire_and_radiant = answer
                        response = get_strats_graph_match()
                        exac_match = get_exac_match(response, players_ids)
                        if exac_match is not None:
                            answer = get_picks_and_pos(match_id=exac_match['matchId'])
                            if answer is not None:
                                if answer != True:
                                    radiant, dire, match_id = answer
                                    print(f'Radint pick: {radiant}\nDire pick: {dire}')
                                    dota2protracker(radiant_heroes_and_positions=radiant, dire_heroes_and_positions=dire, radiant_team_name=dire_and_radiant['radiant'], dire_team_name=dire_and_radiant['dire'], antiplagiat_url=match_id, score = [0,0], egb=True)
                                else:
                                    map = True
                        else:
                            print('карта не найдена, вероятно, матч только начался')
                            map = True
    if map:
        print('сплю 30 секунд')
        time.sleep(30)
    else:
        print('сплю 3 минуты')
        time.sleep(160)
# answer = get_picks_and_pos(match_id=7781964303)
# if answer is not None:
#     radiant, dire, match_id = answer
#     dota2protracker(radiant_heroes_and_positions=radiant, dire_heroes_and_positions=dire, radiant_team_name='radiant', dire_team_name='dire', antiplagiat_url=match_id, tier=2)
