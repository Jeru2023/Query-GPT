import json
import csv

def count_indicators(data):
    data = json.loads(data)
    keywords = data['response']['keywords']

    indicators_count = 0
    for kw in keywords:
        if kw['type'] == 'indicators':
            indicators_count += 1
    
    return indicators_count

def count_row_number(result):
    reader = csv.reader(result.split('\n'))
    next(reader) # 跳过标题行

    count = 0
    for row in reader:
        count += 1

    return count

def get_chart_type(data):
    data = json.loads(data)
    chart_type = data['response']['chart_type']
    return chart_type

def get_multi_series(data):
    data = json.loads(data)
    multi_series = data['response']['multi_series']
    return multi_series