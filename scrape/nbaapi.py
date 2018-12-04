import requests
import json
import pandas as pd

# TODO: figure out how to get list of game ids for the given day

HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }

# url = 'http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=02%2F27%2F2016'
url = 'https://stats.nba.com/stats/playbyplayv2?GameID=0041300402&StartPeriod=0&EndPeriod=0&tabView=playbyplay'


response = requests.get(url, headers=HEADERS)
pbp_dict = json.loads(response.content)

dataRowList = pbp_dict['resultSets'][0]['rowSet']
dataHeaders = [x.lower() for x in pbp_dict['resultSets'][0]['headers']]

pbp = pd.DataFrame(data=dataRowList, columns=dataHeaders)
pbp['score']


def parse_score(score, pos):
    if score is None:
        return None
    else:
        return score[pos]

pbp['away_score'] = pbp['score'].str.split(' - ').apply(lambda x: parse_score(x, 0))
pbp['home_score'] = pbp['score'].str.split(' - ').apply(lambda x: parse_score(x, 1))

pbp['away_score']
pbp['home_score']

# url = 'https://data.nba.com/data/5s/v2015/json/mobile_teams/nba/2018/scores/00_todays_scores.json'
# url = 'https://stats.nba.com/stats/scoreboard/?GameDate=02/14/2015&LeagueID=00&DayOffset=0'
# url = 'http://stats.nba.com/stats/scoreboardV2?DayOffset=0&LeagueID=00&gameDate=02%2F27%2F2016'
