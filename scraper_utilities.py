import pandas as pd


def col_name_clean(c):
    return c.lower().replace('%', '_pct')


def box_scores_dicts_unpack(bs_dicts):
    return pd.concat([bs_dicts[game][team] for game in bs_dicts.keys()
                      for team in bs_dicts[game].keys()])


# TODO: fix bug where if a player has more than 60 min, shows as e.g. 63:00 and overflows .striptime
# TODO: clean up broad exception clause
def mp_convert(t):
    try:
        result = float(t.split(':')[0]) + float(t.split(':')[1]) / 60.
    except:
        result = None
    return result
