
import os
import requests
import time
import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, url_for, request
from database import Database
from price import Price
app = Flask(__name__)

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


if __name__ == '__main__':
    os.environ['AWS_DEFAULT_REGION'] = aws_config.get('region')
    os.environ['AWS_PROFILE'] = aws_config.get('profile')
    scheduler = BackgroundScheduler()
    scheduler.add_job(insert_data_to_db, 'interval', weeks=2)
    scheduler.start()
    app.run(port=5000)
