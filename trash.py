import json
from collections import defaultdict




def synergy_team_gpt(heroes_and_pos, enemy_heroes_and_pos, output, mkdir, data):
    unique_combinations = set()

    # Предварительная обработка данных героев
    heroes_data = {pos: data.get(str(hero_info['hero_id']), {}).get(pos, {})
                   for pos, hero_info in heroes_and_pos.items()}


    for pos, hero_data in heroes_data.items():
        synergy_duo = hero_data.get('synergy_duo', {})

        for second_pos, second_hero_info in heroes_and_pos.items():
            if pos == second_pos:
                continue
            second_hero_id = str(second_hero_info['hero_id'])
            duo_data = synergy_duo.get(second_hero_id, {}).get(second_pos, {})

            if len(duo_data.get('value', [])) >= 30:
                combo = tuple(sorted([str(heroes_and_pos[pos]['hero_id']), second_hero_id]))
                if combo not in unique_combinations:
                    unique_combinations.add(combo)
                    value = duo_data['value'].count(1) / (
                            duo_data['value'].count(1) + duo_data['value'].count(0))
                    output[f'{mkdir}_duo'].append(value)


def synergy_team_new(heroes_and_pos, enemy_heroes_and_pos, output, mkdir, data):
    unique_combinations = set()
    for pos in heroes_and_pos:
        try:
            hero_id = str(heroes_and_pos[pos]['hero_id'])
            hero_data = data[hero_id][pos]['synergy_duo']
            for second_pos in heroes_and_pos:
                if pos != second_pos:
                    second_hero_id = str(heroes_and_pos[second_pos]['hero_id'])
                    duo_data = hero_data[second_hero_id][second_pos]
                    if len(duo_data['value']) >= 30:
                        combo = tuple(sorted([hero_id, second_hero_id]))
                        if combo not in unique_combinations:
                            unique_combinations.add(combo)
                            value = duo_data['value'].count(1) / (
                                    duo_data['value'].count(1) + duo_data['value'].count(0))
                            output[f'{mkdir}_duo'].append(value)
        except:pass
    return output

radiant_heroes_and_pos = {'pos1': {'hero_id': 6, 'hero_name': 'Drow Ranger', 'steamAccountId': 125445069}, 'pos5': {'hero_id': 34, 'hero_name': 'Tinker', 'steamAccountId': 178692606}, 'pos3': {'hero_id': 2, 'hero_name': 'Axe', 'steamAccountId': 405351356}, 'pos4': {'hero_id': 86, 'hero_name': 'Rubick', 'steamAccountId': 993889913}, 'pos2': {'hero_id': 106, 'hero_name': 'Ember Spirit', 'steamAccountId': 86738694}}
dire_heroes_and_pos = {'pos1': {'hero_id': 73, 'hero_name': 'Alchemist', 'steamAccountId': 1040820193}, 'pos5': {'hero_id': 57, 'hero_name': 'Omniknight', 'steamAccountId': 1066782497}, 'pos3': {'hero_id': 98, 'hero_name': 'Timbersaw', 'steamAccountId': 148215639}, 'pos4': {'hero_id': 52, 'hero_name': 'Leshrac', 'steamAccountId': 1048617659}, 'pos2': {'hero_id': 74, 'hero_name': 'Invoker', 'steamAccountId': 196481318}}
output = {'radiant_synergy_duo': [], 'dire_synergy_duo': [], 'radiant_synergy_trio': [], 'dire_synergy_trio': [],
          'radiant_counterpick_duo': [], 'dire_counterpick_duo': [], 'radiant_synergy_2vs1': [],
          'dire_synergy_2vs1': []}

with open('./1722505765_top600_heroes_data/synergy_and_counterpick_dict.txt', 'r+') as f:
    data = json.load(f)
    data = data['value']

output = synergy_team_new(dire_heroes_and_pos, radiant_heroes_and_pos, output, 'dire_synergy', data)
output_gpt = defaultdict(list)

synergy_team_gpt(radiant_heroes_and_pos, dire_heroes_and_pos, output_gpt, 'radiant_synergy', data)
pass