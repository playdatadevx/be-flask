import requests
import json
from datetime import datetime
from database import Database

database = Database()


Capacity = {
        'capacity':'avg(avg_over_time((sum without () (kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}) / count without ()(kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}))[1h:]))*100'
        }

Usages = {
        'cpu':'sum((sum by (instance,nodename) (irate(node_cpu_seconds_total{mode!~"guest.*|idle|iowait"}[1h])) + on(instance) group_left(nodename) node_uname_info) - 1)/count(kube_node_created)*100',
        'memory':'avg((node_memory_MemAvailable_bytes + on(instance) group_left(nodename) node_uname_info) / ((node_memory_MemTotal_bytes + on(instance) group_left(nodename) node_uname_info))*100)',
        'disk':'sum(node_filesystem_size_bytes{kubernetes_node=""} - node_filesystem_avail_bytes{kubernetes_node=""}) by (kubernetes_node) / sum(node_filesystem_size_bytes{kubernetes_node=""}) by (kubernetes_node)*100',
        'storage':'sum(kube_persistentvolume_capacity_bytes)/1000000000',
        'traffic':'sum (rate(node_network_receive_bytes_total[1h]))/1000',
        'node':'count(kube_node_created)'
        }

url = "https://pm-server.devxmonitor.click/api/v1/"

def promql(query,url=url+'query'):
    if url.split('/')[-1] != 'query':
        response = requests.get(url+query).json()
    else:
        params = {"query":query}
        response = requests.get(url,params=params).json()
    result = response['data']['result']
    return result


metric_ids = {'cpu':1,'memory':2,'disk':3,'traffic':5,'node':6,'cap':10}
units = {'cpu':'%','memory':'%','disk':'%','traffic':'Kbps', 'node': '개수','cap':'%'}

def get_usage(queries,url=url,period='1h'):
    result = {}
    for key,query in queries.items():
        params = {"query" : query.replace('required',period)}

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

    
    result = {
            'metric_id': metric_ids[key],
            'data': metric,
            'created_at': created_at,
            'unit': units[key],
            'type': key
    }
    return result

def insert_metrics(Usage,url=url,period='1h'):
    metrics = get_usage(Usage,url,period)

    for key,metric in metrics.items():
        res = mapping_metrics(key,metric)
        res.pop('type',None)
        database.insert_metric('usages',list(res.values()))
    return


def insert_capacity(query,url=url,period='1h'):
    capacity = get_usage(query,url,period)
    
    for key,metric in metrics.items():
        res = mapping_metrics(key,metric)
        res.pop('type',None);res.pop('unit',None);res.pop('metric_id')
        database.insert_metric('capacity',list(res.values()))
    return


def insert_days(metric):
    database.insert_days(metric)
    return

def insert_months(metric):
    database.insert_months(metric)
    return

# metrics  ex ) 'price', 'cost', 'capacity', 'usages'

#insert_metrics(Capacity)
#insert_capacity(Capacity)
#insert_days('capacity')
#insert_months('capacity')

