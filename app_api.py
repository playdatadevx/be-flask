from flask import request,jsonify,Blueprint,Flask
from promql import get_usage,mapping_metrics
api = Blueprint('api',__name__)
url = "https://pm-server.devxmonitor.click/api/v1/query"

@api.route('/usage',methods=['GET'])
def resource_usage():
    period = request.args.get('period')
    type = request.args.get('type')
    Usage={
    'disk':'sum(node_filesystem_size_bytes{kubernetes_node=""} - node_filesystem_avail_bytes{kubernetes_node=""}) by (kubernetes_node) / sum(node_filesystem_avail_bytes{kubernetes_node=""}) by (kubrenetes_node)*100',
    'memory':'avg((node_memory_MemAvailable_bytes + on(instance) group_left(nodename) node_uname_info) / ((node_memory_MemTotal_bytes + on(instance) group_left(nodename) node_uname_info))*100)',
    'cpu':'((sum by (instance,nodename) (irate(node_cpu_seconds_total{mode!~"guest.*|idle|iowait"}[required])) + on(instance) group_left(nodename) node_uname_info) - 1)*100',
    'traffic':'sum (rate(node_network_receive_bytes_total[required]))/1000',
    'node':'count(kube_node_created)'}
    range = {"min":"5m","time":"1h","day":"1d","week":"1w","year":"1y"}
    raw = get_usage(url,{type:Usage[type].replace('required',range[period])})
    result = mapping_metrics(*raw.keys(),*raw.values())
    result.pop('metric_id',None)
    result = jsonify(result)
    return result


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(api,url_prefix='/api/v1')
if __name__=='__main__':
    app.run(host='127.0.0.1',port=5252,debug=True)
