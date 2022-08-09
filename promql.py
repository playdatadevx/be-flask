import os
import requests
from database import Database
from datetime import datetime

today = datetime.now().date()
url = os.environ.get('PROMETHEUS_SERVER')


def promql(query, url=url+'query'):
    if url.split('/')[-1] != 'query':
        response = requests.get(url+query).json()
    else:
        params = {"query": query}
        response = requests.get(url, params=params).json()
    result = response['data']['result']
    return result
