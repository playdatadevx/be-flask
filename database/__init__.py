import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()


class Database:
    
    resources = {1:"cpu",2:"memory",3:"disk",4:"storage",5:"traffic",6:"node"}
    units = {1:"%",2:"%",3:"%",4:"mb",5:"Kbps",6:"개수"}

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
        sql = f'INSERT INTO price (price, unit, aws_service) VALUES ({price}, "{unit}", "{description}")'
        self.curs.execute(sql)
        self.conn.commit()

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


    def insert_days(self):                          # 일별 평균 사용량 Table 명(days_of_usage)
        now = datetime.now().strftime("%Y-%m-%d")
        metric_ids = len(Database.resources.keys())
        for metric_id in range(1,metric_ids+1):
            if metric_id==4: continue   # Storage 부분은 아직 데이터가 없어 생략
            sql = f'select floor(avg(resource_usage)) from resource_usage where ("{now}" = DATE_FORMAT(created_at,"%Y-%m-%d")) and metric_id={metric_id};'
            self.curs.execute(sql)
            result = int(self.curs.fetchall()[0][0])
            sql = f'insert into days_of_usage (metric_id,days_usage,day,unit) VALUES ({metric_id},{result},"{now}","{Database.units[metric_id]}");'
            self.curs.execute(sql)
            self.conn.commit()

    def insert_months(self):                        # 월별 평균 사용량 Table 명 (months_of_usage)
        now = datetime.now().strftime("%Y-%m")
        metric_ids = len(Database.resources.keys())
        for metric_id in range(1,metric_ids+1):
            if metric_id==4: continue   # Storage 부분은 아직 데이터가 없어 생략
            sql = f'select floor(avg(days_usage)) from days_of_usage  where ("{now}" = DATE_FORMAT(day,"%Y-%m")) and metric_id={metric_id};'
            self.curs.execute(sql)
            result = int(self.curs.fetchall()[0][0])
            sql = f'insert into months_of_usage (metric_id,months_usage,month,unit) VALUES ({metric_id},{result},"{now}","{Database.units[metric_id]}");'
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
