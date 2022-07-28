import os
import pymysql
#from dotenv import load_dotenv
from datetime import datetime
#load_dotenv()


class Database:

    resources = {1:"cpu",2:"memory",3:"disk",4:"storage",5:"traffic",6:"node"}
    units = {1:"%",2:"%",3:"%",4:"mb",5:"Kbps",6:"개수"}

    def __init__(self):
        host = '127.0.0.1' #os.environ.get('HOST')
        user = 'devx' #os.environ.get('USER')
        password = 'encore123!' #os.environ.get('PASSWORD')
        database = 'devx' #os.environ.get('DATABASE')
        #port = int(os.environ.get('PORT'))
        self.conn = pymysql.connect(
            host=host, user=user, password=password, db=database, charset='utf8')
        self.curs = self.conn.cursor()

    def quotation(x):
        if type(x)==str: return "{}".format(x)
        else: return x

    def insert_metric(self, table,items):
        prop = {
                'price':'price,created_at,unit,aws_service',
                'cost':'cost,created_at,unit,app',
                'resource_usage':'resource_usage,metric_id,created_at,unit',
                'capacity':'capacity,created_at',
                'metric':'metric'
                }

        sql_row = str([*map(Database.quotation,items)]).replace('[','(').replace(']',')')

        sql = f'INSERT INTO {table} ({prop[table]}) VALUES '+ sql_row
        self.curs.execute(sql)
        self.conn.commit()

    def avg_usage(self,cycle,now,metric_id):
        if cycle=='day': target_usage='resource_usage'; target_table='resource_usage'; target_date='created_at,"%Y-%m-%d"';dest_table="days_of_usage"
        elif cycle=='month': target_usage='days_usage'; target_table='days_of_usage'; target_date='day,"%Y-%m"';dest_table="months_of_usage"

        select_sql = f'select floor(avg({target_usage})) from {target_table} where("{now}" = DATE_FORMAT({target_date})) and metric_id={metric_id};' 
        
        self.curs.execute(select_sql)
        result = int(self.curs.fetchall()[0][0])
        
        insert_sql = f'insert into {dest_table} (metric_id,{cycle}s_usage,{cycle},unit) VALUES ({metric_id},{result},"{now}","{Database.units[metric_id]}");' 

        self.curs.execute(insert_sql)
        self.conn.commit()
        return

    def insert_days(self):                          # 일별 평균 사용량 Table 명(days_of_usage)
        now = datetime.now().strftime("%Y-%m-%d")
        metric_ids = len(Database.resources.keys())
        for metric_id in range(1,metric_ids+1):
            if metric_id==4: continue   # Storage 부분은 아직 데이터가 없어 생략
            self.avg_usage('day',now,metric_id)
            
    def insert_months(self):                        # 월별 평균 사용량 Table 명 (months_of_usage)
        now = datetime.now().strftime("%Y-%m")
        metric_ids = len(Database.resources.keys())
        for metric_id in range(1,metric_ids+1):
            if metric_id==4: continue   # Storage 부분은 아직 데이터가 없어 생략
            self.avg_usage('month',now,metric_id)

    def select_all(self,table):
        sql = f'SELECT * FROM {table}'
        self.curs.execute(sql)
        self.conn.commit()
