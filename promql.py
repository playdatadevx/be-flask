import requests
import json
from datetime import datetime
from database import Database

database = Database()


url = "https://pm-server.devxmonitor.click/api/v1"

def promql(query,url=url+'query'):
    if url.split('/')[-1] != 'query':
        response = requests.get(url+query).json()
    else:
        params = {"query":query}
        response = requests.get(url,params=params).json()
    result = response['data']['result']
    return result


