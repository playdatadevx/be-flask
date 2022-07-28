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

    def quotation(x):
        if type(x)==str: return "{}".format(x)
        else: return x


    def insert_metric(self, table,items):
        prop = {
                'price':'price,created_at,unit,aws_service',
                'price':'price,created_at,unit,aws_service',
                'cost':'cost,created_at,unit,app',
                'usages':'metric_id,usages,created_at,unit',
                'capacity':'capacity,created_at',
                'metric':'metric'
                }


        sql_row = str([*map(Database.quotation,items)]).replace('[','(').replace(']',')')

        sql = f'INSERT INTO {table} ({prop[table]}) VALUES '+ sql_row
        self.curs.execute(sql)
        self.conn.commit()

    def avg_usage(self,cycle,table,now,m_id=None):
        def ex(metric_id,string):
            if metric_id==None: return ''
            else: return string


        if cycle=='day': target_table=table; time_formatter="%Y-%m-%d";
        elif cycle=='month': target_table=f'days_of_{table}'; time_formatter="%Y-%m";

        select_sql = f'select floor(avg({table})) from {target_table} where(DATE_FORMAT("{now}","{time_formatter}") = DATE_FORMAT(created_at,"{time_formatter}"))'+ ex(m_id,f' and metric_id={m_id}')+';'

        self.curs.execute(select_sql)
        result = int(self.curs.fetchall()[0][0])

        insert_sql = f'insert into {cycle}s_of_{table} ('+ ex(m_id,'metric_id,') + f'{table},created_at'+ ex(m_id,',unit') + ') VALUES ('+ ex(m_id,f'{m_id},') + f'{result},"{now}"' + ex(m_id,f',"{Database.units[m_id]}"') +');'
        self.curs.execute(insert_sql)
        self.conn.commit()
        return

    def insert_days(self,table):                          # 일별 평균 사용량 Table 명(days_of_usage)
        now = datetime.now().strftime("%Y-%m-%d")
        metric_ids = len(Database.resources.keys())
        if table=='usages':
            for metric_id in range(1,metric_ids+1):
                if metric_id==4: continue   # Storage 부분은 아직 데이터가 없어 생략
                self.avg_usage('day',table,now,m_id=metric_id)
        else:
            self.avg_usage('day',metric,now)

    def insert_months(self,table):                        # 월별 평균 사용량 Table 명 (months_of_usage)
        now = datetime.now().strftime("%Y-%m-%d")
        metric_ids = len(Database.resources.keys())
        if table=='usages':
            for metric_id in range(1,metric_ids+1):
                if metric_id==4: continue   # Storage 부분은 아직 데이터가 없어 생략
                self.avg_usage('month',table,now,m_id=metric_id)
        else:
            self.avg_usage('month',table,now)

    def select_all(self,table):
        sql = f'SELECT * FROM {table}'
        self.curs.execute(sql)
        self.conn.commit()
