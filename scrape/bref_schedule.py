from basketball_reference_web_scraper import client
import time
import pandas as pd
import os

# first year that works is season ending 1998
# use each season's calendar to add a flag to each game that identifies the season

tmp = client.season_schedule(season_end_year=1998)

def convert_list_of_dicts_to_df(dict_list):
    return pd.concat([pd.DataFrame(current_dict_list, index=[i]) for (i, current_dict_list) in enumerate(dict_list)])

tmp2 = convert_list_of_dicts_to_df(tmp)
tmp2

all_dates = pd.date_range(start_date, end_date)
all_dfs = pd.DataFrame()

for date in all_dates:
    print(date.strftime('%Y-%m-%d'))
    all_player_bs = client.player_box_scores(day=date.day, month=date.month, year=date.year)
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
    all_dfs = pd.concat([all_dfs, all_player_bs_df])

    time.sleep(0.5)

save_filename = 'player_box_scores_{}_thru_{}.txt'.format(start_date, end_date)
save_folder = r'C:\Users\calkinsn\Desktop\box_scores'

all_dfs.to_csv(os.path.join(save_folder, save_filename), sep='\t', index=False)
