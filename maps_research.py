from functions import research_maps, explore_database, get_maps_new
import json
from id_to_name import pro_teams, all_teams, top4000EU_top2000ASIA ,top_1000EU_top100_ASIA, top_2000EU_top1000_ASIA_uniq
import asyncio, aiohttp

def update_pro(show_prints=None, game_mods=None, only_in_ids=None):
    if only_in_ids is not None:
        team_ids = set()
        for name in only_in_ids:
            team_ids.add(all_teams[name.lower()]['id'])
    else:
        team_ids = [pro_teams[team]['id'] for team in pro_teams]
    get_maps_new(maps_to_save='./pro_heroes_data/pro_maps', show_prints=show_prints,
                 ids=team_ids, game_mods=game_mods, only_in_ids=True)
    research_maps(maps_to_explore='pro_maps', file_name='pro_output', mkdir='pro_heroes_data', show_prints=show_prints)
    explore_database(mkdir='pro_heroes_data', file_name='pro_output', pro=True,
                     show_prints=show_prints, time_kills=True)


def update_all_teams(show_prints=None, only_in_ids=None):
    team_ids = set()
    if only_in_ids is not None:
        for name in only_in_ids:
            team_ids.add(all_teams[name.lower()]['id'])
    else:
        for team in all_teams:
            team_ids.add(all_teams[team]['id'])
    get_maps_new(maps_to_save='./all_teams/maps', game_mods=[2],
                 show_prints=show_prints, ids=team_ids, only_in_ids=only_in_ids)
    research_maps(maps_to_explore='maps', file_name='output', mkdir='all_teams', show_prints=show_prints)
    explore_database(mkdir='all_teams', file_name='output', pro=True,
                     show_prints=show_prints, time_kills=True, total_time_kills_teams=True)


def update_my_protracker(show_prints=None):
    # get_maps_new(maps_to_save='./1722505765_top600_heroes_data/1722505765_top600_maps', game_mods=[2, 22],
    #              show_prints=show_prints, ids=list(top4000EU_top2000ASIA.keys()) + list(top_1000EU_top100_ASIA.keys()) + list(top_2000EU_top1000_ASIA_uniq.keys()))
    # research_maps(mkdir='1722505765_top600_heroes_data', maps_to_explore='1722505765_top600_maps',
    #               file_name='1722505765_top600_output', show_prints=show_prints)
    # #
    explore_database(mkdir='1722505765_top600_heroes_data', file_name='1722505765_top600_output',
                     show_prints=show_prints, lane=True, over35=True,
                     over45=True, protracker=True)


# def update_heroes_data(database_list=None, mkdir=None):
#     get_maps_new(maps_to_save='./heroes_data/heroes_data_maps', game_mods=[2, 22], start_date_time=1716508800,
#     players_dict=top_600_asia_europe_nonanon)
#     research_maps(maps_to_explore='heroes_data_maps', output='heroes_data_output', mkdir='heroes_data')
#     explore_database(mkdir='heroes_data', output='heroes_data_output', start_date_time=1716508800)

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
    for map_id in to_be_merged:
        if map_id not in data:
            data[map_id] = to_be_merged[map_id]
    with open('./all_teams/output.txt', 'w') as f:
        json.dump(data, f)
