from flask import request,jsonify,Blueprint,Flask,Response
from promql import get_usage,mapping_metrics
import json



url = "https://pm-server.devxmonitor.click/api/v1/query"
range = {"min":"5m","time":"1h","day":"1d","week":"1w","year":"1y"}


app = Flask(__name__)

@app.route('/usage',methods=['GET'])
def resource_usage():
    try:
        period = request.args.get('period')
        type = request.args.get('type')

        raw = get_usage(url,period,{type:Usage[type]})
        result = mapping_metrics(*raw.keys(),*raw.values())
        result.pop('metric_id',None)
        result = jsonify(result)
    except (AttributeError, KeyError, TypeError, json.decoder.JSONDecodeError):
        return Response('{"code": 400,"message": "Bad Request" }', status=400)
    except:
        return Response('{"code": 401,"message": "Unauthorized"}', status=401)
    return result


@app.route('/capacity',methods=['GET'])
def capacity():
    try:
        period = request.args.get('period')
        type = request.args.get('type',default='cap')
        raw = get_usage(url,period,{type,query[type])
        result = mapping_metrics(*raw.keys(),*raw.values())
        result.pop('metric_id',None)
        result.pop('type',None)
        result = jsonify(result)
    except (AttributeError, KeyError, TypeError, json.decoder.JSONDecodeError):
        return Response('{"code": 400,"message": "Bad Request" }', status=400)
    except:
        return Response('{"code": 401,"message": "Unauthorized"}', status=401)
    return result


app.config['JSON_AS_ASCII'] = False
if __name__=='__main__':
    app.run(host='127.0.0.1',port=5252,debug=True)
