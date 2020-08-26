from basketball_reference_web_scraper import client
import time
import pandas as pd
import os

# args
# 1998 is first year that works, since team name changes break this API
season_end_year = 1998

# start_date = '2019-01-01'
# end_date = '2019-12-31'


def convert_list_of_dicts_to_df(dict_list):
    return pd.concat([pd.DataFrame(current_dict_list, index=[i]) for (i, current_dict_list) in enumerate(dict_list)])

# TODO - test that all years after 1998 have working schedules
# TODO - manually identify the start date for each playoff year and use it to add an is_playoffs flag to box scores
# TODO - check out season calendar handles the bubble
# TODO - validate vs external sources
# TODO - backfill to S3
# TODO - schedule a daily incremental load to S3 - OR use RDS since free tier seems like enough


sched = client.season_schedule(season_end_year=season_end_year)
sched_df = convert_list_of_dicts_to_df(sched)

# # instead of requesting all dates in range, only use distinct dates in schedule
# start_date = sched_df['start_time'].dt.date.min().strftime('%Y-%m-%d')
# end_date = sched_df['start_time'].dt.date.max().strftime('%Y-%m-%d')
# all_dates = pd.date_range(start_date, end_date)

all_dfs = pd.DataFrame()
all_dates = [date.strftime('%Y-%m-%d') for date in sched_df['start_time'].dt.date.unique()]
season_id = '{}-{}'.format(season_end_year, str(season_end_year + 1)[-2:])

for date in all_dates:
    print(date)
    all_player_bs = client.player_box_scores(day=pd.to_datetime(date).day, month=pd.to_datetime(date).month,
                                             year=pd.to_datetime(date).year)
    if len(all_player_bs) == 0:
        continue
    all_player_bs_df = convert_list_of_dicts_to_df(all_player_bs)
    all_player_bs_df['made_two_point_field_goals'] = (all_player_bs_df['made_field_goals'] -
                                                        all_player_bs_df['made_three_point_field_goals'])

    all_player_bs_df['attempted_two_point_field_goals'] = (all_player_bs_df['attempted_field_goals'] -
                                                      all_player_bs_df['attempted_three_point_field_goals'])

    all_player_bs_df['points'] = (2 * all_player_bs_df['made_two_point_field_goals'] +
                                  3 * all_player_bs_df['made_three_point_field_goals'] +
                                  1 * all_player_bs_df['made_free_throws'])

    all_player_bs_df['date'] = date
    all_player_bs_df['season_id'] = season_id
    all_dfs = pd.concat([all_dfs, all_player_bs_df])

    time.sleep(0.5)

save_filename = 'player_box_scores_{}.txt'.format(season_id)
save_folder = r'C:\Users\calkinsn\Desktop\box_scores'

all_dfs.to_csv(os.path.join(save_folder, save_filename), sep='\t', index=False)
