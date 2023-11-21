from typing import Tuple
import pandas as pd
from datetime import datetime
from scipy.special import inv_boxcox

# week_no 1년(52주) 중 해당 날짜가 속한 주
# week_int 월별 주차정보 (1~5)
# dayno 1 : 일 / 2 : 월 / 3 : 화 / 4 : 수 / 5 : 목 / 6 : 금 / 7 : 토
# regihour : 시간
# regiminute : 초 제거하고 '분'로 변환 Ex. 10:06:38 -> 10:06:00 -> 10*60 + 6 = 606
# regisecond : 시간을 모두 '초'로 변환 Ex.10:06:38 -> 10*3600+60*6+38=36398

async def transform_dataframe(request_body: dict) -> pd.DataFrame():

    date_str, time_str = request_body['regidatetime'].split(' ')
    regihour, regiminute, regisecond = transform_time(time_str)

    df = pd.DataFrame([{
        'plantcode_L' : transform_plantcode(request_body['plantcode']),
        'week_no' : extract_week(date_str),
        'waitingno' : request_body['waitingno'],
        'dayno' : extract_dayno(date_str),
        'daytype' : request_body['daytype'],
        'regihour' : regihour,
        'regiminute' : regiminute,
        'regisecond' : regisecond,
        'teamahead' : request_body['teamahead'],
        'customercnt' : request_body['customercnt'],
        'customergroupcnt' : request_body['customergroupcnt'],
    }])
    return df

async def transform_boxcox(predict: int) -> int:
    # 1. Box-cox 변환
    lambda_value = 0.20776504963895437
    predict_boxcox = inv_boxcox(predict[0], lambda_value)
    # 2. (분) 환산 (올림)
    prediction = int(predict_boxcox/60)+1
    return prediction

def transform_plantcode(plantcode: str) -> int:
    plantcode_mapping = {
        'AL108' : 0, 
        'AL132' : 1, 
        'AL133' : 2, 
        'AL184' : 3, 
        'AL210' : 4, 
        'AL297' : 5, 
        'AL304' : 6, 
        'AL326' : 7, 
        'AL333' : 8, 
        'AL343' : 9, 
        'JB013' : 10, 
        'PM241' : 11, 
        'RI110' : 12, 
        'RU019' : 13,
    }
    return plantcode_mapping.get(plantcode, -1)

def transform_time(date_str: str) -> Tuple[int, int, int]:
    hour, minute, second = map(int, date_str.split(':'))
    regihour = hour
    regiminute = hour * 60 + minute
    regisecond = hour * 3600 + minute * 60 + second
    return regihour, regiminute, regisecond

def extract_week(date_str: str) -> int:
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    iso_week_number = date_obj.isocalendar()[1]
    return iso_week_number

def extract_dayno(date_str: str) -> int:
      return (datetime.strptime(date_str, '%Y-%m-%d').weekday() + 2) % 7 or 7
