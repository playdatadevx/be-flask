import json
import boto3


class Price:
    def __init__(self):
        pass

    def set_data(self, price, unit, description):
        self.price = price
        self.unit = unit
        self.description = description

    def get_price(self, response_iterator, sku):
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
                self.set_data(price, unit, description)
        return aws_price

    def get_products(self, service_code, filter_path, sku):
        pricing_client = boto3.client('pricing', region_name='us-east-1')
        paginator = pricing_client.get_paginator('get_products')

        with open(filter_path, 'r') as filters_json:
            filters = json.load(filters_json).get('filters')
        response_iterator = paginator.paginate(
            ServiceCode=service_code,
            Filters=filters,
            PaginationConfig={
                'PageSize': 100
            }
        )

        aws_price = get_price(response_iterator, sku)
        return aws_price
