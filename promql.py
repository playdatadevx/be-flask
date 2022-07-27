import requests
import json
from datetime import datetime
from database import Database

database = Database()

Capacity = {'cap':'avg(avg_over_time((sum without () (kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}) / count without ()(kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}))[1h:]))*100'}

Usage={
 'disk':'sum(node_filesystem_size_bytes{kubernetes_node=""} - node_filesystem_avail_bytes{kubernetes_node=""}) by (kubernetes_node) / sum(node_filesystem_avail_bytes{kubernetes_node=""}) by (kubrenetes_node)*100',
 'memory':'avg((node_memory_MemAvailable_bytes + on(instance) group_left(nodename) node_uname_info) / ((node_memory_MemTotal_bytes + on(instance) group_left(nodename) node_uname_info))*100)',
 'cpu':'((sum by (instance,nodename) (irate(node_cpu_seconds_total{mode!~"guest.*|idle|iowait"}[1h])) + on(instance) group_left(nodename) node_uname_info) - 1)*100',
 'traffic':'sum (rate(node_network_receive_bytes_total[1h]))/1000',
 'node':'count(kube_node_created)'
}

url = "https://pm-server.devxmonitor.click/api/v1/query"

def get_usage(url,queries):
    result = {}
    for key,query in queries.items():
        params = {"query" : query}
        raw = requests.get(url, params=params).json()
        try:
            total = 0
            raw_datas = raw['data']['result']
            for raw_data in raw_datas:    
                data = round(float(raw_data['value'][1]))
                total += int(data)
            value = total//len(raw_datas)
            result[key]=value            
        except:
            print("ERROR")
    return result 

def mapping_metrics(key,metric):
    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    metric_ids = {'cpu':1,'memory':2,'disk':3,'traffic':5,'node':6,'cap':10}
    units = {'cpu':'%','memory':'%','disk':'%','traffic':'Kbps', 'node': '개수','cap':'%'}
    
    result = {
            'metric_id': metric_ids[key],
            'type': key,
            'unit': units[key],
            'data': metric,
            'created_at': created_at
    }
    return result

def insert_metrics(url,Usage):

    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    metrics = get_usage(url,Usage)
    metric_ids = {'cpu':1,'memory':2,'disk':3,'traffic':5,'node':6}
    units = {'cpu':'%','memory':'%','disk':'%','traffic':'Kbps', 'node': '개수'}
    sql_rows = []

    for key,metric in metrics.items():
        res = mapping_metrics(key,metric)
        database.insert_metric('resource_usage',res['data'],res['metric_id'],res['created_at'],res['unit'])
    return



def insert_capacity(url,query):
    capacity = get_usage(url,query)
    print(capacity)
    res = mapping_metrics(*capacity.keys(),*capacity.values())
    database.insert_metric('capacity',res['data'],res['created_at'])
    return
# insert_capacity(url,Capacity)


def insert_days():
    database.insert_days()
    return

def insert_months():
    database.insert_months()
    return

