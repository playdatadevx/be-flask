import calendar
import json
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from database import Database
from dotenv import load_dotenv
from flask import Flask, Response, request
from price import Price, get_products
from types import SimpleNamespace
import logging
from datetime import datetime
from flask_cors import CORS
from cron_insert import insert_cost, start_insert

range_ = {"min": "5m", "time": "1h", "day": "1d", "week": "1w", "year": "1y"}

today = datetime.now().date()
logging.basicConfig(filename=f'./logs/{today}.log')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv()

keycloak_server = os.environ.get('KEYCLOAK_SERVER')
realm = os.environ.get('REALM')
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLENT_SECRET')
secret_key = os.environ.get('SECRET_KEY')
keyclock_endpoint = f'http://{keycloak_server}/auth/realms/{realm}/protocol/openid-connect'
keyclock_userinfo_endpoint = keyclock_endpoint + '/userinfo'
keyclock_login_endpoint = keyclock_endpoint + '/token'
keyclock_logout_endpoint = keyclock_endpoint + '/logout'

bad_request_error = Response(
    '{"code": 400,"message": "Bad Request"}', status=400)
unauthorized_error = Response(
    '{"code": 401,"message": "Unauthorized"}', status=401)
unexpected_error = Response(
    '{"code": 500,"message": "Unexpected Error"}', status=500)


def check_auth(request):
    token = request.headers.get('Authorization')
    keycloak_response = requests.post(keyclock_userinfo_endpoint,
                                      headers={
                                          'Authorization': f'Bearer {token}',
                                          'Content-Type': 'application/x-www-form-urlencoded'},
                                      data={
                                          'client_id': client_id,
                                      })
    return keycloak_response


def insert_price_to_db():
    ec2_price = get_products('ec2')
    ebs_price = get_products('ebs')
    eks_price = get_products('eks')

    database = Database()
    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")
    database.insert_metric(
        'price', [ec2_price.price, created_at, ec2_price.unit, ec2_price.description])
    database.insert_metric(
        'price', [ebs_price.price, created_at, ebs_price.unit, ebs_price.description])
    database.insert_metric(
        'price', [eks_price.price, created_at, eks_price.unit, eks_price.description])


def insert_days_of_data_to_db():
    database = Database()
    database.insert_days('cost')
    database.insert_days('usages')
    database.insert_days('capacity')


def insert_months_of_data_to_db():
    database = Database()
    database.insert_months('cost')
    database.insert_months('usages')
    database.insert_months('capacity')


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_data()
        params = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        keycloak_response = requests.post(keyclock_login_endpoint,
                                          headers={
                                              'Content-Type': 'application/x-www-form-urlencoded'},
                                          data={
                                              'username': params.username,
                                              'password': params.password,
                                              'client_id': client_id,
                                              'client_secret': client_secret,
                                              'grant_type': 'password'
                                          })
        if keycloak_response.status_code == 400:
            return bad_request_error
        elif keycloak_response.status_code == 401:
            return unauthorized_error
    except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
        logging.exception(e)
        return bad_request_error
    except Exception as e:
        logging.exception(e)
        return unexpected_error
    return keycloak_response.text


@ app.route('/logout', methods=['POST'])
def logout():
    try:
        token = request.headers.get('Authorization')
        params = json.loads(request.get_data(),
                            object_hook=lambda d: SimpleNamespace(**d))
        keycloak_response = requests.post(keyclock_logout_endpoint,
                                          headers={
                                              'Authorization': f'Bearer {token}',
                                              'Content-Type': 'application/x-www-form-urlencoded'},
                                          data={
                                              'client_id': client_id,
                                              'refresh_token': params.refresh_token,
                                          })
        if keycloak_response.status_code == 400:
            return bad_request_error
        elif keycloak_response.status_code == 401:
            return unauthorized_error
    except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
        logging.exception(e)
        return bad_request_error
    except Exception as e:
        logging.exception(e)
        return unexpected_error
    return str(keycloak_response)


@ app.route('/cost', methods=['GET'])
def cost():
    try:
        keycloak_response = check_auth(request)
        if keycloak_response.status_code == 400:
            return bad_request_error
        elif keycloak_response.status_code == 401:
            return unauthorized_error
        period = request.args.get('period')
        db = Database()
        res = db.select_usages('cost', period)
        data = [val[0] for val in res]
        unit = res[-1][1]
        created_at = res[-1][2].strftime("%Y-%m-%d %H:%M:%S")
        response = {
            "unit": unit,
            "data": data,
            "created_at": created_at
        }
    except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
        logging.exception(e)
        return bad_request_error
    except Exception as e:
        logging.exception(e)
        return unexpected_error
    return response


@ app.route('/exp-cost', methods=['GET'])
def exp_cost():
    try:
        keycloak_response = check_auth(request)
        if keycloak_response.status_code == 400:
            return bad_request_error
        elif keycloak_response.status_code == 401:
            return unauthorized_error
        database = Database()
        result = database.select_expcost()
        today = datetime.today()
        number_of_days = calendar.monthrange(today.year, today.month)[1]
        sum_cost = result[0][0]
        unit = result[0][1]
        if(sum_cost != int):
            last_month_cost = database.select_last_month_cost()
            if(len(last_month_cost) == 0):
                exp_cost = 0
                unit = ''
            else:
                exp_cost = last_month_cost[0][0]
                unit = last_month_cost[0][1]
        else:
            exp_cost = sum_cost + ((sum_cost / today.day) * number_of_days)
        response = {
            "data": [exp_cost],
            "unit": unit,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
        logging.exception(e)
        return bad_request_error
    except Exception as e:
        logging.exception(e)
        return unexpected_error
    return response


@app.route('/usage', methods=['GET'])
def resource_usage():
    try:
        keycloak_response = check_auth(request)
        if keycloak_response.status_code == 400:
            return bad_request_error
        elif keycloak_response.status_code == 401:
            return unauthorized_error
        period = request.args.get('period')
        metric = request.args.get('type')

        db = Database()
        res = db.select_usages('usages', period, metric)
        data = [val[0] for val in res]
        unit = res[-1][1]
        created_at = res[-1][2].strftime("%Y-%m-%d %H:%M:%S")
        response = {
            "type": metric,
            "unit": unit,
            "data": data,
            "created_at": created_at
        }
    except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
        logging.exception(e)
        return bad_request_error
    except Exception as e:
        logging.exception(e)
        return unexpected_error
    return response


@app.route('/capacity', methods=['GET'])
def capacity():
    try:
        keycloak_response = check_auth(request)
        if keycloak_response.status_code == 400:
            return bad_request_error
        elif keycloak_response.status_code == 401:
            return unauthorized_error
        period = request.args.get('period')

        db = Database()
        res = db.select_usages('capacity', period)
        data = [val[0] for val in res]
        unit = '%'
        created_at = res[-1][1].strftime("%Y-%m-%d %H:%M:%S")
        response = {
            "unit": unit,
            "data": data,
            "created_at": created_at
        }
    except (AttributeError, TypeError, json.decoder.JSONDecodeError) as e:
        logging.exception(e)
        return bad_request_error
    except Exception as e:
        logging.exception(e)
        return unexpected_error
    return response


scheduler = BackgroundScheduler(
    timezone='Asia/Seoul', misfire_grace_time=6000)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

scheduler.add_job(insert_price_to_db, 'cron', hour=0, minute=0)
scheduler.add_job(start_insert, 'cron', minute=1)
scheduler.add_job(insert_cost, 'cron', minute=2)
scheduler.add_job(insert_days_of_data_to_db, 'cron', hour=0, minute=3)
scheduler.add_job(insert_months_of_data_to_db, 'cron', day=1, hour=0, minute=4)
scheduler.start()

insert_price_to_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
