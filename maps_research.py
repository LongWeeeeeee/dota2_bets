from functions import get_maps, research_maps, explore_database
import json
from id_to_name import all_teams_ids, pro_teams, all_teams, top3000EU_top1000SE_ASIA_nonAnon

def update_pro(show_prints=None):
    team_ids = [pro_teams[team]['id'] for team in pro_teams]
    get_maps(maps_to_save='./pro_heroes_data/pro_maps', game_mods=[2], start_date_time=1716508800,
             players_dict='', show_prints=show_prints, team_ids=team_ids)
    research_maps(maps_to_explore='pro_maps', output='pro_output', mkdir='pro_heroes_data', show_prints=show_prints)
    explore_database(mkdir='pro_heroes_data', output='pro_output', start_date_time=1716508800, pro=True, show_prints=show_prints, team_ids= team_ids)


def update_all_teams(show_prints=None, team_names=None):
    if team_names is not None:
        team_ids = []
        for name in team_names:
            team_ids.append(all_teams[name]['id'])
    else:
        team_ids = all_teams_ids
    get_maps(maps_to_save='./all_teams/maps', game_mods=[2], start_date_time=1716508800,
             players_dict='', show_prints=show_prints, team_ids=team_ids, team_names=team_names)
    research_maps(maps_to_explore='maps', output='output', mkdir='all_teams', show_prints=show_prints)
    explore_database(mkdir='all_teams', output='output', start_date_time=1716508800, pro=True, show_prints=show_prints, team_ids= all_teams_ids)



def update_my_protracker(show_prints=None):
    # get_maps(maps_to_save='./1722505765_top600_heroes_data/1722505765_top600_maps', game_mods=[2, 22],
    #          start_date_time=1723670400, players_dict=top3000EU_top1000SE_ASIA_nonAnon, show_prints=show_prints)
    research_maps(mkdir='1722505765_top600_heroes_data', maps_to_explore='1722505765_top600_maps',
                  output='1722505765_top600_output', show_prints=show_prints)
    explore_database(mkdir='1722505765_top600_heroes_data', output='1722505765_top600_output',
                     start_date_time=1723670400, show_prints=show_prints)


def update_heroes_data(database_list=None, mkdir=None):
    # get_maps(maps_to_save='./heroes_data/heroes_data_maps', game_mods=[2, 22], start_date_time=1716508800,
    # players_dict=top_600_asia_europe_nonanon)
    # research_maps(maps_to_explore='heroes_data_maps', output='heroes_data_output', mkdir='heroes_data')
    explore_database(mkdir='heroes_data', output='heroes_data_output', start_date_time=1716508800)

if __name__ == "__main__":
    # with open('teams_stat_dict.txt', 'r+') as f:
    #     data = json.load(f)
    # teams_ids = set()
    # for team in data:
    #     id = data[team]['id']
    #     if id > 0:
    #         teams_ids.add(id)
    # set(teams_ids)
    # pass
    with open('./all_teams/output.txt', 'r+') as f:
        data = json.load(f)
    with open('./pro_heroes_data/pro_output.txt', 'r') as f:
        to_be_merged = json.load(f)
    for map in to_be_merged:
        if map not in data:
            data[map] = to_be_merged[map]
    with open('./all_teams/output.txt', 'w') as f:
        json.dump(data, f)