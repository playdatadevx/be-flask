from promql import promql
from datetime import datetime


metrics = ['cpu','memory','disk','storage','traffic','node','capacity']

metric_ids = {
        'cpu':1,
        'memory':2,
        'disk':3,
        'storage':4,
        'traffic':5,
        'node':6,
        }
units = {
        'cpu':'%',
        'memory':'%',
        'disk':'%',
        'storage':'GB',
        'traffic':'Kbps',
        'node': '개수',
        }

query = {
        'cpu':'sum((sum by (instance,nodename) (irate(node_cpu_seconds_total{mode!~"guest.*|idle|iowait"}[1h])) + on(instance) group_left(nodename) node_uname_info) - 1)/count(kube_node_created)*100',
        'memory':'avg((node_memory_MemAvailable_bytes + on(instance) group_left(nodename) node_uname_info) / ((node_memory_MemTotal_bytes + on(instance) group_left(nodename) node_uname_info))*100)',
        'disk':'sum(node_filesystem_size_bytes{kubernetes_node=""} - node_filesystem_avail_bytes{kubernetes_node=""}) by (kubernetes_node) / sum(node_filesystem_size_bytes{kubernetes_node=""}) by (kubernetes_node)*100',
        'storage':'sum(kube_persistentvolume_capacity_bytes)/1000000000',
        'traffic':'sum (rate(node_network_receive_bytes_total[1h]))/1000',
        'node':'count(kube_node_created)',
        'capacity':'avg(avg_over_time((sum without () (kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}) / count without ()(kube_pod_container_status_ready{namespace=~"kube-system", pod=~"aws-node.*"}))[1h:]))*100'
        }


# PromQL  쿼리결과 가공 
def make_items(metric):
    raw_response = promql(query[metric])
    items = []
    for response in raw_response:
        items.append(response['value'][1])
    return items

def make_format(metric,op='first'):
    items = make_items(metric) # 값이 여러개 들어있을 때 'avg','sum','first'
    if op=='avg':
        item = [sum(items)/len(items)]
    elif op=='sum':
        item = [sum(items)]
    elif op=='first':
        item = [items[0]]
    else:
        pass
    return item

def insert_item(metric,op='first'):
    value = make_format(metric,op)[0]
    unit = units.get(metric)
    table = 'usages' if not metric == 'capacity' else 'capacity'
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = [ key for key in [value,date,metric_ids.get(metric),unit] if key != None ]
    return item


