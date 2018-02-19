import box_score_bref_v2 as box
import datetime
import pandas as pd
import os
import time
import numpy as np
import argparse

# use yesterday as default start and end date
yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--start_date', help='start date in format YYYY-MM-DD', default=yesterday, metavar='')
parser.add_argument('-e', '--end_date', help='end date in format YYYY-MM-DD', default=yesterday, metavar='')
parser.add_argument('-f', '--folder', help='name of destination folder relative to wd', default='box_bref', metavar='')
args = parser.parse_args()
folder_path = os.path.join(os.getcwd(), args.folder)

# generate list of days between start date and end date
dates = list(pd.date_range(start=args.start_date, end=args.end_date, freq='D'))
dates.sort(reverse=True)

# loop through all dates, attempt to scrape, and save as .txt
for cur_date in dates:
    try:
        df = box.scrape_all_box_scores(cur_date.year, cur_date.month, cur_date.day)
        export_path = os.path.join(folder_path, cur_date.strftime('%Y%m%d') + '.txt')
        df.to_csv(export_path, sep='\t', index=False)
    except ValueError:
        print('The following date caused an error and was skipped.  '
              'This may be because there were no games that day.')
        print(cur_date.strftime('%Y%m%d'))
    print('Sleeping for about 10 seconds...')
    sec = max(0, np.random.normal(10, 3))
    time.sleep(sec)
