import box_score_bref_v2 as box
import datetime
import pandas as pd
import os
import time
import numpy as np

# configure export location and start date
export_folder = os.path.join(os.getcwd(), 'box_bref')
start_date = '2000-01-01'

# generate list of days between start date and yesterday
yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
dates = pd.date_range(start=start_date, end=yesterday, freq='D').sort_values(ascending=False)

# loop through all dates, attempt to scrape, and save as .txt
for cur_date in dates:
    try:
        df = box.scrape_all_box_scores(cur_date.year, cur_date.month, cur_date.day)
        export_path = os.path.join(export_folder, cur_date.strftime('%Y%m%d') + '.txt')
        df.to_csv(export_path, sep='\t', index=False)
    except ValueError:
        print('The following date caused an error and was skipped.  '
              'This may simply be because there were no games that day.')
        print(cur_date.strftime('%Y%m%d'))
    print('Sleeping for about 10 seconds...')
    sec = max(0, np.random.normal(10, 3))
    time.sleep(sec)
