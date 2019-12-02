import pandas as pd 
import numpy as np 
import math
import yfinance as yf 

from .formatting import get_daterange, fund_list_extractor


def download_data_indexes(indexes: list, tickers: str, period: str='2y', interval='1d', start=None, end=None, fund_len=None) -> list:
    if (start is not None) and (end is not None):
        data1 = yf.download(tickers=tickers, start=start, end=end, interval='1d', group_by='ticker')
    else:
        data1 = yf.download(tickers=tickers, period=period, interval='1d', group_by='ticker')
    data = data_format(data1, config=None, list_of_funds=indexes, fund_len=fund_len)
    return data, indexes


def download_data(config: dict) -> list:
    period = config.get('period', '2y')
    interval = config.get('interval', '1d')
    tickers = config['tickers']
    ticker_print = config['ticker print']

    if period is None:
        period = '2y'
    if interval is None:
        interval = '1d'
    
    daterange = get_daterange(period=period)
    
    if daterange[0] is None:
        print(f'Fetching data for {ticker_print} for {period} at {interval} intervals...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker')
    else: 
        print(f'Fetching data for {ticker_print} from dates {daterange[0]} to {daterange[1]}...')
        data = yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker', start=daterange[0], end=daterange[1])
    print(" ")

    funds = fund_list_extractor(data, config=config)
    data = data_format(data, config=config)

    return data, funds


def download_single_fund(fund: str, config: dict, fund_len=None) -> dict:
    period = config.get('period', '2y')
    interval = config.get('interval', '1d')
    ticker = fund

    if period is None:
        period = '2y'
    if interval is None:
        interval = '1d'
    
    daterange = get_daterange(period=period)
    
    if daterange[0] is None:
        print(f'Fetching sector data for {ticker}...')
        data = yf.download(tickers=ticker, period=period, interval=interval, group_by='ticker')
    else: 
        print(f'Fetching sector data for {ticker}...')
        data = yf.download(tickers=ticker, period=period, interval=interval, group_by='ticker', start=daterange[0], end=daterange[1])
    print(" ")

    data = data_format(data, config=config, single_fund_name=ticker, fund_len=fund_len)

    return data



def add_status_message(status: list, new_message: str, message_index: int=None, key: str=None) -> str:
    """ adds 'new_message' to status if it isn't added already """
    need_to_add = True
    for i, message in enumerate(status):
        if new_message == message['message']:
            status[i]['count'] += 1
            if key is not None:
                status[i]['info'].append({key: message_index})
            need_to_add = False
    if need_to_add:
        if key is not None:
            status.append({'message': new_message, 'count': 1, 'info': [{key: message_index}]})
        else:
            status.append({'message': new_message, 'count': 1, 'info': []})
    return status


def get_status_message(status: list) -> str:
    message = ''
    info = ''
    for i,item in enumerate(status):
        message += f"{item['message']} ({item['count']})"
        info += f"{item['info']}"
        if i < len(status)-1:
            message += ', '
            info += ', '
    return message, info



def data_format(data: pd.DataFrame, config: dict, list_of_funds=None, single_fund_name=None, fund_len=None) -> dict:
    data_dict = {}
    fund_keys = list_of_funds
    if list_of_funds is None:
        if single_fund_name is None:
            fund_keys = fund_list_extractor(data, config=config)
        else:
            fund_keys = [single_fund_name]
    dates = data.index 

    if 'Open' in data.keys():
        # Singular fund case
        df_dict = {}
        df_dict['Date'] = filter_date(dates.copy(), fund_len=fund_len)
        df_dict['Open'] = filter_nan(data['Open'].copy(), fund_name=fund_keys[0], column_key='Open', fund_len=fund_len)
        df_dict['Close'] = filter_nan(data['Close'].copy(), column_key='Close', fund_len=fund_len)
        df_dict['High'] = filter_nan(data['High'].copy(), column_key='High', fund_len=fund_len)
        df_dict['Low'] = filter_nan(data['Low'].copy(), column_key='Low', fund_len=fund_len)
        df_dict['Adj Close'] = filter_nan(data['Adj Close'].copy(), column_key='Adj Close', fund_len=fund_len)
        df_dict['Volume'] = filter_nan(data['Volume'].copy(), column_key='Volume', fund_len=fund_len)

        df = pd.DataFrame.from_dict(df_dict)
        df = df.set_index('Date')

        data_dict[fund_keys[0]] = df.copy()

    else:
        for fund in fund_keys:
            df_dict = {}
            df_dict['Date'] = filter_date(dates.copy(), fund_len=fund_len)
            df_dict['Open'] = filter_nan(data[fund]['Open'].copy(), fund_name=fund, column_key='Open', fund_len=fund_len)
            df_dict['Close'] = filter_nan(data[fund]['Close'].copy(), column_key='Close', fund_len=fund_len)
            df_dict['High'] = filter_nan(data[fund]['High'].copy(), column_key='High', fund_len=fund_len)
            df_dict['Low'] = filter_nan(data[fund]['Low'].copy(), column_key='Low', fund_len=fund_len)
            df_dict['Adj Close'] = filter_nan(data[fund]['Adj Close'].copy(), column_key='Adj Close', fund_len=fund_len)
            df_dict['Volume'] = filter_nan(data[fund]['Volume'].copy(), column_key='Volume', fund_len=fund_len)

            df = pd.DataFrame.from_dict(df_dict)
            df = df.set_index('Date')

            data_dict[fund] = df.copy()

    return data_dict


def filter_nan(frame_list: pd.DataFrame, fund_name=None, column_key=None, fund_len: dict=None) -> list:
    new_list = list(frame_list.copy())
    nans = list(np.where(pd.isna(frame_list) == True))[0]

    corrected = False
    status = []

    if fund_len is not None:
        if len(new_list) != fund_len['length']:
            if frame_list.index[0] != fund_len['start']:
                newer_list = [float('NaN')]
                newer_list.extend(new_list)
                new_list = newer_list.copy()
                nans = np.append(0, nans)
            elif frame_list.index[len(frame_list)-1] != fund_len['end']:
                new_list.append(float('NaN'))
                nans = np.append(nans, len(frame_list)-1)

    if len(nans) > 0:
        corrected = True
        for na in nans:
            if (na == 0) and (not math.isnan(new_list[na+1])):
                status = add_status_message(status, 'Row-0 nan')
                new_list[na] = new_list[na+1]
            elif (na != 0) and (na != len(new_list)-1) and (not math.isnan(new_list[na-1]) and (not math.isnan(new_list[na+1]))):
                status = add_status_message(status, 'Row-inner nan')
                new_list[na] = np.round(np.mean([new_list[na-1], new_list[na+1]]), 2)
            elif (na == len(new_list)-1) and (not math.isnan(new_list[na-1])):
                status = add_status_message(status, 'Mutual Fund nan')
                new_list[na] = new_list[na-1]
            elif not math.isnan(new_list[na-1]):
                # More general case than above, different error.
                status = add_status_message(status, 'Generic progression nan', na, column_key)
                new_list[na] = new_list[na-1]
            else:
                status = add_status_message(status, 'Unknown/unfixable nan', na, column_key)

    if corrected and (fund_name is not None):
        message, info = get_status_message(status)
        if 'Unknown/unfixable nan' in message:
            print(f"WARNING: 'NaN' found on {fund_name}. Type: '{message}': Correction FAILED.")
            print(f"----> Content: {info}")
        elif 'Generic progression nan' in message:
            print(f"Note: 'NaN' found on {fund_name}. Type: '{message}': Corrected OK.")
            print(f"----> Content: {info}")
        else:
            print(f"Note: 'NaN' found on {fund_name} data. Type: '{message}': Corrected OK.")
        
    return new_list


def filter_date(dates, fund_len: dict=None):
    if fund_len is not None:
        if len(dates) != fund_len['length']:
            if dates[0] != fund_len['start']:
                newer_list = [fund_len['start']]
                newer_list.extend(dates)
                dates = newer_list.copy()
            elif dates[len(dates)-1] != fund_len['end']:
                dates.append(fund_len['end'])
    return dates.copy()