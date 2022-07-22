import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        host = os.environ.get('HOST')
        user = os.environ.get('USER')
        password = os.environ.get('PASSWORD')
        database = os.environ.get('DATABASE')
        port = int(os.environ.get('PORT'))
        self.conn = pymysql.connect(
            host=host, user=user, password=password, db=database, port=port, charset='utf8')
        self.curs = self.conn.cursor()

    def insert_price(self, price, unit, description):
        sql = f'INSERT INTO price (price, unit, aws_service) VALUES ({price}, {unit}, {description})'
        self.curs.execute(sql)
        self.conn.commit()

    def select_price(self):
        sql = f'SELECT * FROM price'
        self.curs.execute(sql)
        self.conn.commit()

    def select_resource_usage(self):
        sql = f'SELECT * FROM resource_usage '
        self.curs.execute(sql)
        self.conn.commit()

    def select_capacity(self):
        sql = f'SELECT * FROM capacity'
        self.curs.execute(sql)
        self.conn.commit()

    def select_metric(self):
        sql = f'SELECT * FROM metric'
        self.curs.execute(sql)
        self.conn.commit()
