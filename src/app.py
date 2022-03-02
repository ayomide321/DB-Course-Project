import flask
import pymysql
import config.py as cfg

import sys
import warnings

params = []
heading = []
col = int(sys.argv[1])

con = pymysql.connect(host=cfg.mysql['host'], user = cfg.mysql['user'], password = cfg.mysql['password'], database = cfg.mysql['db'])

try:
    cur = con.cursor()
    sql = "UPDATE batting SET CS = 0 WHERE playerID = '" + sys.argv[1] + "'"

    cur.execute(sql)
    print("rowcount", cur.rowcount)
except Exception:
    con.rollback()
    print("Database exception")
    raise