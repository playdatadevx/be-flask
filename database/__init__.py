import datetime
import os
import pymysql
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()


class Database:
    agg = {'cost': 'SUM', 'capacity': 'AVG', 'usages': 'AVG'}
    resources = {1: "cpu", 2: "memory", 3: "disk",
                 4: "storage", 5: "traffic", 6: "node"}
    metrics_ids = {v: k for k, v in resources.items()}
    units = {1: "%", 2: "%", 3: "%", 4: "GB",
             5: "Kbps", 6: "개수", 'cost': 'USD'}
    period_conditions = {"time": "DAY", "day": "WEEK", "month": "YEAR"}
    columns = {"cost": ["cost", "unit", "created_at"],
               "days_of_cost": ["cost", "unit", "created_at"],
               "months_of_cost": ["cost", "unit", "created_at"],
               "capacity": ["capacity", "created_at"],
               "days_of_capacity": ["capacity", "created_at"],
               "months_of_capacity": ["capacity", "created_at"],
               "usages": ["usages", "unit", "created_at"],
               "days_of_usages": ["usages", "unit", "created_at"],
               "months_of_usages": ["usages", "unit", "created_at"]
               }
    prop = {
        'price': 'price,created_at,unit,aws_service',
        'cost': 'cost,created_at,unit',
        'usages': 'usages,created_at,metric_id,unit',
        'capacity': 'capacity,created_at',
        'metric': 'metric'
    }

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
        if type(x) == str:
            return "{}".format(x)
        else:
            return x

    def insert_metric(self, table, items):
        sql_row = str([*map(Database.quotation, items)]
                      ).replace('[', '(').replace(']', ')')
        sql = f'INSERT INTO {table} ({Database.prop[table]}) VALUES ' + sql_row
        self.curs.execute(sql)
        self.conn.commit()

    # 일별 평균 사용량 Table 명(days_of_usage)

    def insert_days(self, table):  # cost / capacity / usages [type]
        now = datetime.now().strftime("%Y-%m-%d")
        values = []
        sql = f'SELECT {Database.agg[table]}({table}) FROM {table} WHERE (DATE_FORMAT("{now}","%Y-%m-%d") = DATE_FORMAT(created_at,"%Y-%m-%d"))'
        extra_sql = ''
        if table == 'usages':
            metric_ids = int(self.select_query(
                'SELECT MAX(id) FROM metric')[0][0])
            for metric_id in range(1, metric_ids+1):
                extra_sql = f' AND metric_id={metric_id}'
                values.append(float(self.select_query(sql+extra_sql)[0][0]))
        else:
            values.append(float(self.select_query(sql+extra_sql)[0][0]))
        sql = f'INSERT INTO days_of_{table} ({Database.prop[table]}) VALUES '
        if table == 'usages':
            for metric_id in range(1, metric_ids+1):
                item = [values[metric_id-1], now, metric_id,
                        Database.units.get(metric_id)]
                extra_sql = str([*map(Database.quotation, item)]
                                ).replace('[', '(').replace(']', ')')
                self.insert_query(sql+extra_sql)
        else:
            item = [key for key in [values[0], now,
                                    Database.units.get(table, None)] if key != None]
            extra_sql = str([*map(Database.quotation, item)]
                            ).replace('[', '(').replace(']', ')')
            self.insert_query(sql+extra_sql)
        return

    # 월별 평균 사용량 Table 명 (months_of_usage)
    def insert_months(self, table):
        now = datetime.now().strftime("%Y-%m-%d")
        values = []
        sql = f'SELECT {Database.agg[table]}({table}) FROM days_of_{table} WHERE (DATE_FORMAT("{now}","%Y-%m") = DATE_FORMAT(created_at,"%Y-%m"))'
        extra_sql = ''
        if table == 'usages':
            metric_ids = int(self.select_query(
                'SELECT MAX(id) FROM metric')[0][0])
            for metric_id in range(1, metric_ids+1):
                extra_sql = f' AND metric_id={metric_id}'
                values.append(float(self.select_query(sql+extra_sql)[0][0]))
        else:
            values.append(float(self.select_query(sql+extra_sql)[0][0]))
        sql = f'INSERT INTO months_of_{table} ({Database.prop[table]}) VALUES '
        if table == 'usages':
            for metric_id in range(1, metric_ids+1):
                item = [values[metric_id-1], now, metric_id,
                        Database.units.get(metric_id)]
                extra_sql = str([*map(Database.quotation, item)]
                                ).replace('[', '(').replace(']', ')')
                self.insert_query(sql+extra_sql)
        else:
            item = [key for key in [values[0], now,
                                    Database.units.get(table, None)] if key != None]
            extra_sql = str([*map(Database.quotation, item)]
                            ).replace('[', '(').replace(']', ')')
            self.insert_query(sql+extra_sql)
        return

    def insert_query(self, query):
        self.curs.execute(query)
        self.conn.commit()

    def select_query(self, query):
        self.curs.execute(query)
        return self.curs.fetchall()

    def select_cost(self, period):
        tables = {"time": "cost", "day": "days_of_cost",
                  "month": "months_cost"}
        table = tables.get(period)
        column = Database.columns.get(table)
        sql = f'SELECT {",".join(column)} FROM {table} WHERE created_at BETWEEN NOW()- INTERVAL 1 {Database.period_conditions.get(period)} AND NOW() ORDER BY created_at ASC;'
        self.curs.execute(sql)
        result = list(self.curs.fetchall())
        self.conn.commit()
        return result

    def select_expcost(self):
        sql = 'SELECT SUM(cost), unit FROM days_of_cost WHERE created_at BETWEEN LAST_DAY(NOW() - interval 1 month) + interval 1 DAY AND NOW();'
        self.curs.execute(sql)
        result = self.curs.fetchall()
        self.conn.commit()
        return result

    def select_usages(self, table, period, metric=None):
        tables = {"time": table, "day": f"days_of_{table}",
                  "month": f"months_of_{table}"}
        period_table = tables.get(period)
        column = Database.columns.get(period_table)
        now = datetime.strptime(datetime.now().strftime(
            "%Y, %m, %d, %H, %M, %S"), "%Y, %m, %d, %H, %M, %S")
        extra_sql = '' if metric == None else f'metric_id={Database.metrics_ids[metric]} AND '
        sql = f'SELECT {",".join(column)} FROM {table} WHERE '+extra_sql + \
            f'created_at BETWEEN NOW()- INTERVAL 1 {Database.period_conditions.get(period)} AND NOW() ORDER BY created_at ASC;'
        result = list(self.select_query(sql))
        
        if table!=period_table:
            sql = f'SELECT {Database.agg[table]}({table}) FROM {table} WHERE ' + extra_sql + '(DATE_FORMAT(NOW(),"%Y-%m-%d") = DATE_FORMAT(created_at,"%Y-%m-%d"))' 
            res = float(self.select_query(sql)[0][0])
            item = tuple([key for key in [round(res,2),Database.units.get(table if metric==None else Database.metrics_ids[metric],None),now] if key!=None])
            result.append(item)
            
        return result
