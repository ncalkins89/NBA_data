from basketball_reference_web_scraper import client
import time
import pandas as pd
import numpy as np
import os

# args
# 1998 is first year that works, since team name changes break this API
# season_end_year = 1998
season_end_years = list(range(1998, 2021))
# season_end_years = list(range(1998, 1999))

# start_date = '2019-01-01'
# end_date = '2019-12-31'


def convert_list_of_dicts_to_df(dict_list):
    return pd.concat([pd.DataFrame(current_dict_list, index=[i]) for (i, current_dict_list) in enumerate(dict_list)])

# TODO - test that all years after 1998 have working schedules
# TODO - check out season calendar handles the bubble
# TODO - validate vs external sources
# TODO - backfill to S3
# TODO - schedule a daily incremental load to S3 - OR use RDS since free tier seems like enough


for season_end_year in season_end_years:

    sched = client.season_schedule(season_end_year=season_end_year)
    sched_df = convert_list_of_dicts_to_df(sched)

    all_dfs = pd.DataFrame()
    all_dates = [date.strftime('%Y-%m-%d') for date in sched_df['start_time'].dt.date.unique()]
    # all_dates = [date.strftime('%Y-%m-%d') for date in pd.date_range('1998-04-01', '1998-04-14')]

    season_id = '{}-{}'.format(season_end_year - 1, str(season_end_year)[-2:])

    for date in all_dates:
        print(date)
        all_player_bs = client.player_box_scores(day=pd.to_datetime(date).day, month=pd.to_datetime(date).month,
                                                 year=pd.to_datetime(date).year)
        if len(all_player_bs) == 0:
            continue
        all_player_bs_df = convert_list_of_dicts_to_df(all_player_bs)
        all_player_bs_df['date'] = pd.to_datetime(date)
        all_dfs = pd.concat([all_dfs, all_player_bs_df])

        time.sleep(0.5)

    # post processing
    all_dfs['made_two_point_field_goals'] = (all_dfs['made_field_goals'] -
                                             all_dfs['made_three_point_field_goals'])

    all_dfs['attempted_two_point_field_goals'] = (all_dfs['attempted_field_goals'] -
                                                  all_dfs['attempted_three_point_field_goals'])

    all_dfs['points'] = (2 * all_dfs['made_two_point_field_goals'] +
                         3 * all_dfs['made_three_point_field_goals'] +
                         1 * all_dfs['made_free_throws'])

    all_dfs['total_rebounds'] = all_dfs['defensive_rebounds'] + all_dfs['offensive_rebounds']

    all_dfs['season_id'] = season_id
    all_dfs['season_end_year'] = season_end_year

    # add is playoffs flag
    playoff_start_dates = pd.read_csv('playoff_start_dates.csv')
    playoff_start_dates['playoff_start_date'] = pd.to_datetime(playoff_start_dates['playoff_start_date'])
    all_dfs = all_dfs.merge(playoff_start_dates, how='left', on=['season_end_year'])
    all_dfs['is_playoffs'] = np.where(all_dfs['date'] >= all_dfs['playoff_start_date'], 'Y', 'N')
    all_dfs = all_dfs.drop(columns='playoff_start_date')

    # all_dfs.to_clipboard(index=False)

    save_filename = 'player_box_scores_{}.txt'.format(season_id)
    save_folder = r'C:\Users\calkinsn\Desktop\box_scores'

    all_dfs.to_csv(os.path.join(save_folder, save_filename), sep='\t', index=False, encoding='utf-16')
