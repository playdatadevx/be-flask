import requests
import json
from datetime import datetime
from database import Database

database = Database()

Capacity = {'cap':'avg(avg_over_time((sum without () (kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}) / count without ()(kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}))[5m:5m]))*100'}

Usage={
 'disk':'sum(node_filesystem_size_bytes{kubernetes_node=""} - node_filesystem_avail_bytes{kubernetes_node=""}) by (kubernetes_node) / sum(node_filesystem_avail_bytes{kubernetes_node=""}) by (kubrenetes_node)*100',
 'mem':'((node_memory_MemTotal_bytes + on(instance) group_left(nodename) node_uname_info) - (node_memory_MemAvailable_bytes + on(instance) group_left(nodename) node_uname_info))/1000000',
 'cpu':'((sum by (instance,nodename) (irate(node_cpu_seconds_total{mode!~"guest.*|idle|iowait"}[5m])) + on(instance) group_left(nodename) node_uname_info) - 1)*100',
 'trf':'sum (rate(node_network_receive_bytes_total[5m]))/1000',
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

def insert_metrics(url,Usage):

    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    metrics = get_usage(url,Usage)
    metric_ids = {'cpu':1,'mem':2,'disk':3,'trf':5,'node':6}
    units = {'cpu':'%','mem':'%','disk':'%','trf':'Kbps', 'node': '개수'}
    sql_rows = []

    for key,metric in metrics.items():
        metric_id = metric_ids[key] 
        unit = units[key]
        resource_usage = metric
        database.insert_metric('resource_usage',resource_usage,metric_id,created_at,unit)
    return


# insert_metrics(url,Usage)

def insert_capacity(url,query):
    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    capacity = get_usage(url,query)
    capacity = capacity['cap']
    database.insert_metric('capacity',capacity,created_at)
    return
insert_capacity(url,Capacity)
