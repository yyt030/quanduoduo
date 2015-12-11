#!/usr/bin/env python
# coding: utf8


# cd quanduoduo
# celery -A schedules.ticket worker --loglevel=info --beat
#



import MySQLdb as mdb
from datetime import datetime, timedelta
from config import load_config
from celery import Celery

celery = Celery('mytask')
config = load_config()
celery.config_from_object(config)

query_sql = '''
        SELECT
            a.user_id,
            a.discount_id
        FROM
            get_ticket_record a,
            discount b
        WHERE
            a.discount_id = b.id
        AND DATEDIFF(CURRENT_TIMESTAMP,a.create_at) > b.usable
        AND a.status != 'usedit'
    '''

update_sql = '''
    update get_ticket_record set status = 'expire' where user_id = %s and discount_id = %s
    '''


@celery.task
def update_ticket_status():
    conn = mdb.connect(host='localhost', db='weshop', user='root', passwd='root',
                       port=3306)
    cursor = conn.cursor()
    conn.autocommit(on=False)
    num_commit = 500
    now = datetime.now()

    cursor.execute(query_sql)
    curr_num = 0
    records = cursor.fetchall()
    for record in records:
        user_id, discount_id = record[0], record[1]
        cursor.execute(update_sql, (user_id, discount_id))
        curr_num += 1
        if curr_num >= num_commit:
            conn.commit()
            curr_num = 0
    conn.commit()
    cursor.close()
    conn.close()
