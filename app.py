
import json
import os
import requests
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from database import Database
from dotenv import load_dotenv
from flask import Flask, request
from keycloak import Client
from price import Price
from types import SimpleNamespace

app = Flask(__name__)
keycloak_client = Client()

load_dotenv()
keycloak_server = os.environ.get('KEYCLOAK_SERVER')
realm = os.environ.get('REALM')
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLENT_SECRET')
secret_key = os.environ.get('SECRET_KEY')
keyclock_endpoint = f'http://{keycloak_server}/auth/realms/{realm}'
keyclock_token_endpoint = keyclock_endpoint + \
    f'/protocol/openid-connect/userinfo'
keyclock_login_endpoint = keyclock_endpoint + \
    f'/protocol/openid-connect/token'
keyclock_logout_endpoint = keyclock_endpoint + \
    f'/protocol/openid-connect/logout'

with open("./price/resources/config.yaml", "r") as config:
    aws_config = yaml.load(config, Loader=yaml.FullLoader)


def insert_data_to_db():
    service_code_ec2 = aws_config.get('service_code_ec2')
    service_code_eks = aws_config.get('service_code_eks')
    ec2_filter_path = aws_config.get('ec2_filter_path')
    ebs_filter_path = aws_config.get('ebs_filter_path')
    eks_filter_path = aws_config.get('eks_filter_path')
    ec2_sku = aws_config.get('ec2_sku')
    ebs_sku = aws_config.get('ebs_sku')
    eks_sku = aws_config.get('eks_sku')

    ec2_price = Price()
    ebs_price = Price()
    eks_price = Price()

    ec2_price.get_products(service_code_ec2, ec2_filter_path, ec2_sku)
    ebs_price.get_products(service_code_ec2, ebs_filter_path, ebs_sku)
    eks_price.get_products(service_code_eks, eks_filter_path, eks_sku)

    database = Database()
    database.insert_price(ec2_price.price, ec2_price.unit,
                          ec2_price.description)
    database.insert_price(ebs_price.price, ebs_price.unit,
                          ebs_price.description)
    database.insert_price(eks_price.price, eks_price.unit,
                          eks_price.description)


@app.route('/login', methods=['POST'])
def login():
    params = json.loads(request.get_data(),
                        object_hook=lambda d: SimpleNamespace(**d))
    if len(str(params)) == 0:
        return 'Bad Request', 400
    response = requests.post(keyclock_login_endpoint,
                             headers={
                                 'Content-Type': 'application/x-www-form-urlencoded'},
                             data={
                                 'username': params.username,
                                 'password': params.password,
                                 'client_id': client_id,
                                 'client_secret': client_secret,
                                 'grant_type': 'password'
                             }
                             )
    if not response.ok:
        return "Unauthorized", 401
    return str(response), 200


@ app.route('/logout', methods=['POST'])
def logout():
    token = request.headers.get('Authorization')
    params = json.loads(request.get_data(),
                        object_hook=lambda d: SimpleNamespace(**d))
    response = requests.post(keyclock_logout_endpoint,
                             headers={
                                 'Authorization': f'Bearer {token}',
                                 'Content-Type': 'application/x-www-form-urlencoded'},
                             data={
                                 'client_id': client_id,
                                 'refresh_token': params.refresh_token,
                             }
                             )
    if not response.ok:
        return "Unauthorized", 401

    return "Hello, World!", 200


if __name__ == '__main__':
    os.environ['AWS_DEFAULT_REGION'] = aws_config.get('region')
    os.environ['AWS_PROFILE'] = aws_config.get('profile')
    scheduler = BackgroundScheduler()
    scheduler.add_job(insert_data_to_db, 'interval', weeks=2)
    scheduler.start()
    app.run(port=5000)
