from pron_job import *
from database import Database

# metrics , metrics_ids , units , query

db = Database()


def selecting():
    price_sql = 'SELECT price FROM price'
    usages_sql = 'SELECT usages FROM usages WHERE metric_id IN (SELECT id FROM metric WHERE metric IN ("storage_usage","node_num"))and (created_at >= DATE_ADD(NOW(),INTERVAL -1 HOUR))'
    ec2, ebs, eks = db.select_query(price_sql)
    storage, node = db.select_query(usages_sql)
    return ec2[0], ebs[0], eks[0], storage[0], node[0]


def calc_cost():
    ec2, ebs, eks, storage, node = selecting()
    expr = ec2*node + ebs*(node*20+storage) + eks
    return expr


def insert_cost():
    value = round(calc_cost(), 2)
    unit = 'USD'
    table = 'cost'
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item = [value, date, unit]

    print('=======  Start  Insert cost To DATABASE  =======')
    db.insert_metric(table, item)
    print('=======  Finished Inserting cost  =======')
    return


def start_insert(metrics=metrics, op='first'):
    print('=======  Start  Insert metrics To DATABASE  =======')
    for metric in metrics:
        table, item = insert_item(metric, op)
        db.insert_metric(table, item)
    print('=======  Finished Inserting metrics  =======')
    return
