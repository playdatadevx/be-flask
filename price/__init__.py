import boto3
import json
import os
import yaml


with open("./price/resources/config.yaml", "r") as config:
    aws_config = yaml.load(config, Loader=yaml.FullLoader)

os.environ['AWS_DEFAULT_REGION'] = aws_config.get('region')
os.environ['AWS_PROFILE'] = aws_config.get('profile')

service_codes = {
    'ec2': aws_config.get('service_code_ec2'),
    'ebs': aws_config.get('service_code_ec2'),
    'eks': aws_config.get('service_code_eks')
}

filter_paths = {
    'ec2': aws_config.get('ec2_filter_path'),
    'ebs': aws_config.get('ebs_filter_path'),
    'eks': aws_config.get('eks_filter_path')
}
skus = {
    'ec2': aws_config.get('ec2_sku'),
    'ebs': aws_config.get('ebs_sku'),
    'eks': aws_config.get('eks_sku')
}


class Price:
    def __init__(self, price, unit, description):
        self.price = price
        self.unit = unit
        self.description = description


def get_products(aws_service):
    pricing_client = boto3.client('pricing', region_name='us-east-1')

    paginator = pricing_client.get_paginator('get_products')

    filter_path = filter_paths.get(aws_service)
    service_code = service_codes.get(aws_service)
    sku = skus.get(aws_service)

    with open(filter_path, 'r') as filters_json:
        filters = json.load(filters_json).get('filters')

    response_iterator = paginator.paginate(
        ServiceCode=service_code,
        Filters=filters,
        PaginationConfig={
            'PageSize': 100
        }
    )

    for response in response_iterator:
        for priceItem_json in response["PriceList"]:
            priceItems = json.loads(priceItem_json)
            priceItem = priceItems.get('terms', {}).get('OnDemand', {}).get(f'{sku}.JRTCKXETXF', {}).get(
                'priceDimensions', {}).get(f'{sku}.JRTCKXETXF.6YS6EN2CT7', {})
            if priceItem == {}:
                break
            description = priceItem.get('description', {})
            price_per_unit = priceItem.get('pricePerUnit', {})
            unit = list(price_per_unit.keys())[0]
            price = price_per_unit.get(unit)
            return Price(price, unit, description)
