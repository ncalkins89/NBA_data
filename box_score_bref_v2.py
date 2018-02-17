from bs4 import BeautifulSoup
import re
import requests
import pandas as pd
import numpy as np
import datetime
import scraper_utilities as su

# TODO: restructure the passing around of identifiers (date, team, etc.) so that script can more effecively
# be run for SINGLE games.  Currently, all ID columns can only be added if scraping all games for the given day.

# CSS TAGS:

# #box_lal_basic
# #box_lal_advanced
# #box_det_advanced
# #box_det_advanced

# http://www.pythonforbeginners.com/python-on-the-web/web-scraping-with-beautifulsoup/
# https://www.dataquest.io/blog/web-scraping-tutorial-python/
# NOTE: when scraping from the box scores page, make the request once.  So pass in the request, not the URL.
# TODO: try to get the # of minutes remaining in the game in order to show what stats each player is on pace for
# TODO: time out error handling
# TODO: schedule to run daily and store the results.  MySQL database?
# TODO: function: for a given day, get the games played that day (home and away)


# get the urls for the day.
# TODO: also return list of teams who played
def get_box_score_urls(year, month, day):
    url = r'https://www.basketball-reference.com/boxscores/?month={}&day={}&year={}'.format(
        str(month), str(day), str(year))
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'lxml')
    link_list = []
    for link in soup.find_all('a'):
        link_list.append(link.get('href'))
    bs = set([l for l in link_list if l.startswith(r'/boxscores/' + str(year))])
    bs_urls = [r'https://www.basketball-reference.com' + l for l in bs]
    return bs_urls


def get_raw_table(req, selector):
    soup = BeautifulSoup(req.text, 'lxml')
    df = pd.read_html(soup.select(selector)[0].prettify())[0]
    return df


# workaround to id that beautifulsoup can't find for some reason, from:
# https://stackoverflow.com/questions/44424690/python-beautifulsoup-cannot-find-table-id
# TODO: evaluate whether this will break, e.g. multiple IDs with same name?
def get_raw_table_by_id(req, id):
    soup = BeautifulSoup(req.text, 'lxml')
    html = soup.find(string=re.compile('id="{}"'.format(id)))
    new_soup = BeautifulSoup(html, "html.parser")
    df = pd.read_html(new_soup.table.prettify())[0]
    return df


# req is the results of requests.get(url) for a box score url.  Pulls from table w/ scoring by quarter
def get_team_names(req):
    # TODO: parse raw line score and preserve the scoring by quarter
    raw_line_score = get_raw_table_by_id(req, id='line_score')
    away_team = raw_line_score.loc[2, 0]
    home_team = raw_line_score.loc[3, 0]
    return away_team, home_team


# works for both basic and advanced stats
def parse_raw_box_scores(df):
    # TODO: convert minutes played to a float
    # column names are shifted to the right 2
    # THIS MAY HAVE CHANGED
    # df.columns = list(df.columns[2:]) + ['null1', 'null2']
    df.columns = df.columns.droplevel()
    df.rename(columns={'Starters': 'player_name', '+/-': 'plus_minus'}, inplace=True)
    # drop row that says reserves, and team totals
    rows_to_drop = df.loc[df['player_name'].isin(['Reserves', 'Team Totals'])].index
    df.drop(rows_to_drop, inplace=True)
    # assuming first 5 rows are starters and all else are reserves
    df['is_starter'] = np.NaN
    df.loc[:4, 'is_starter'] = 'Y'
    df.loc[5:, 'is_starter'] = 'N'
    # drop the null columns (no longer needed)
    # df.drop(['null1', 'null2'], axis=1, inplace=True)
    # if did not play, set minutes to 0.  Remaining stats left as null
    df['MP'] = df['MP'].map(lambda t: su.mp_convert(t))
    df.columns = [su.col_name_clean(c) for c in df.columns]
    return df


# get basic and advanced stats for team and merge
def get_combined_box_score(req, team):
    basic = get_raw_table(req, selector='#box_{}_basic'.format(team.lower()))
    basic = parse_raw_box_scores(basic)
    adv = get_raw_table(req, selector='#box_{}_advanced'.format(team.lower()))
    adv = parse_raw_box_scores(adv)

    combined = basic.merge(adv, how='outer', on='player_name', suffixes=('', '_drop_this'))
    combined.drop(labels=[c for c in combined.columns if c.endswith('_drop_this')], axis=1, inplace=True)

    return combined


# return the combined box scores for both teams, as a dict that maps from team to df
def scrape_url(url):
    req = requests.get(url)
    away_team, home_team = get_team_names(req)
    game_matchup_id = away_team + ' @ ' + home_team
    box_score = {}
    for team in [away_team, home_team]:
        bs = get_combined_box_score(req, team=team)
        # add a bunch of identifier columns
        bs['team_abbrev'] = team
        bs['away_team_abbrev'] = away_team
        bs['home_team_abbrev'] = home_team
        bs['game_matchup_id'] = game_matchup_id
        bs['source'] = 'bref'
        box_score[team] = bs
    return box_score, game_matchup_id


# get all the box scores for a given day.  returns a nested dictionary: game id -> team name -> box score df
def scrape_all_box_scores(year, month, day, unpacked=True):
    # TODO: add random pause and/or other mechanisms to dodge bot detection.  Ask Ben
    # get the urls for that day
    date_str = '-'.join([str(year), str(month).zfill(2), str(day).zfill(2)])
    print('Getting list of URLs for ' + date_str + '...')
    bs_urls = get_box_score_urls(year, month, day)
    all_box_scores = {}
    for url in bs_urls:
        print('Scraping from ' + url + '...')
        box_score, game_matchup_id = scrape_url(url)
        for k, df in box_score.items():
            df['date'] = date_str
        all_box_scores[game_matchup_id] = box_score
    print('Done.')
    if unpacked:
        return su.box_scores_dicts_unpack(all_box_scores)
    else:
        return all_box_scores


if __name__ == '__main__':
    daily_box_scores = scrape_all_box_scores(year=datetime.datetime.today().year,
                                             month=datetime.datetime.today().month,
                                             day=datetime.datetime.today().day - 1)
