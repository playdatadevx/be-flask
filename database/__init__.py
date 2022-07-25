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


    def insert_metric(self, table,*items):
        prop = {'price':['price,created_at,unit,aws_service','({},"{}","{}","{}")'],
        'cost':['cost,created_at,unit,app','({},"{}","{}","{}")'],
        'resource_usage':['resource_usage,metric_id,created_at,unit','({},{},"{}","{}")'],
        'capacity':['capacity,created_at','({},"{}")'],
        'metric':['metric','("{}")']}

        sql_row = prop[table][1].format(*items)

        sql = f'INSERT INTO {table} ({prop[table][0]}) VALUES'+ sql_row
        self.curs.execute(sql)
        self.conn.commit()

    def select_all(self,table):
        sql = f'SELECT * FROM {table}'
        self.curs.execute(sql)
        self.conn.commit()
