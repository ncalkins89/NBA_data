import nba_py.game
import pandas as pd

# TODO: get smarter about headers, wait time...

sb = nba_py.Scoreboard(month=2, day=9, year=2018, league_id='00', offset=0)
sb.available()
sb.series_standings()
sb.game_header()

# get the games for that day
game_ids = list(sb.available().GAME_ID)



game_id = game_ids[0]


# add package level data sets
# package level
# 'Scoreboard': ['available', 'east_conf_standings_by_day', 'game_header', 'last_meeting', 'line_score',
#                'series_standings', 'west_conf_standings_by_day'],

game_data_set_names = {
    'Boxscore': ['player_stats', 'team_starter_bench_stats', 'team_stats'],
    'BoxscoreAdvanced': ['sql_players_advanced', 'sql_team_advanced'],
    'BoxscoreFourFactors': ['sql_players_four_factors', 'sql_players_four_factors'],
    'BoxscoreMisc': ['sql_players_misc', 'sql_team_misc'],
    'BoxscoreScoring': ['sql_players_scoring', 'sql_team_scoring'],
    'BoxscoreSummary': ['available_video', 'game_info', 'game_summary', 'inactive_players', 'last_meeting',
                        'line_score', 'officials', 'other_stats', 'season_series'],
    'BoxscoreUsage': ['sql_players_usage', 'sql_team_usage'],
    'PlayByPlay': ['available_video', 'info'],
    'PlayerTracking': ['info']
}

game_data_set_names = game_data_set_names['Boxscore']

# get all data for all games ever
# in a single year
# on a single day (get the scoreboard for the day, and keep its data)

# for a single game (get ALL the dfs in the class name.  always get all dfs).

# game_data = {} # date, dataset keys, to data

# game id, class name, df name
game_data = {}

class_name = 'Boxscore'
df_name = 'player_stats'

# this might be cleaner: https://stackoverflow.com/questions/3279082/python-chain-getattr-as-a-string
cls = getattr(nba_py.game, 'Boxscore')
inst = cls(game_id)
df = getattr(inst, 'player_stats')()
# create nested structure to store data
game_data[game_id] = {}
game_data[game_id][class_name] = {}
game_data[game_id][class_name][df_name] = df.copy()



game_data[game_id] = {}
# should flatten intead
for class_name, df_names in game_data_set_names.items():
    game_data[game_id][class_name] = {}
    for df_name in df_names:
        print(class_name, df_name)
        cls = getattr(nba_py.game, class_name)
        inst = cls(game_id)
        df = getattr(inst, df_name)()
        game_data[game_id][class_name][df_name] = df.copy()

game_data['0021700820']['Boxscore'].keys()