import json

def count_indicators(data):
    data = json.loads(data)
    keywords = data['response']['keywords']

    indicators_count = 0
    for kw in keywords:
        if kw['type'] == 'indicators':
            indicators_count += 1
    
    return indicators_count