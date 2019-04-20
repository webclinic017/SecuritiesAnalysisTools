import pandas as pd 
import numpy as np 

def local_extrema(filtered: list) -> dict:
    extrema = {}
    extrema['max'] = []
    extrema['min'] = []
    direct = 0
    for i in range(1, len(filtered)):
        if direct == 0:
            if filtered[i] > filtered[i-1]:
                direct = 1
            else:
                direct = -1
        elif direct == 1:
            if filtered[i] < filtered[i-1]:
                direct = -1
                extrema['max'].append(i-1)
        else:
            if filtered[i] > filtered[i-1]:
                direct = 1
                extrema['min'].append(i-1)

    return extrema


def reconstruct_extrema(original, extrema: dict, ma_size: int) -> dict:
    """ 
    Function to find true extrema on 'original', especially when 'extrema' is generated
    from a filtered / averaged signal (moving averages introduce time shifting)
    """

    recon = {}
    recon['max'] = []
    recon['min'] = []
    olist = list(original)

    for _max in extrema['max']:
        start = _max - ma_size
        if start < 0:
            start = 0
        recon['max'].append([olist.index(np.max(olist[start:_max]), start, _max), np.max(olist[start:_max+1])])

    for _min in extrema['min']:
        start = _min - ma_size
        if start < 0:
            start = 0
        recon['min'].append([olist.index(np.min(olist[start:_min]), start, _min), np.min(olist[start:_min+1])])
    
    return recon



def remove_duplicates(recon: dict, threshold=0.01) -> dict:
    """ 
    Removes duplicates of extrema (due to equal tops, errors, those w/in a threshold of its neighbor)
    """
    most_recent = 0
    newlist = []
    for i in range(len(recon['max'])):
        if (recon['max'][i][0] != most_recent) and ((recon['max'][i][1] > recon['max'][i-1][1] * (1+threshold)) or (recon['max'][i][1] < recon['max'][i-1][1] * (1-threshold))):
            most_recent = recon['max'][i][0]
            newlist.append(recon['max'][i])
    recon['max'] = newlist
    newlist = []
    most_recent = 0
    for i in range(len(recon['min'])):
        if (recon['min'][i][0] != most_recent) and ((recon['min'][i][1] > recon['min'][i-1][1] * (1+threshold)) or (recon['min'][i][1] < recon['min'][i-1][1] * (1-threshold))):
            most_recent = recon['min'][i][0]
            newlist.append(recon['min'][i])
    recon['min'] = newlist

    return recon 



def add_daterange(original: pd.DataFrame, extrema: dict, num_feature_points: int) -> dict:
    """
    Looks at index ranges of 'extrema' and adds actual dates from 'original' to 'extrema'
    """
    for feat in extrema['features']:
        if feat:
            first_ind = feat['indexes'][0][0]
            last_ind = feat['indexes'][num_feature_points-1][0]
            start = str(original['Date'][first_ind])
            end = str(original['Date'][last_ind])
            feat['daterange'] = start + ' : ' + end

    return extrema


def remove_empty_keys(dictionary: dict) -> dict:
    """ 
    Cleans and removes empty dictionary or list parameters for concise structuring
    """
    new_dict = {}
    new_dict['min'] = dictionary['min']
    new_dict['max'] = dictionary['max']
    new_dict['features'] = []
    for feat in dictionary['features']:
        if feat:
            # essentially, if not empty
            new_dict['features'].append(feat)

    return new_dict        