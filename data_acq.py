import sqlite3
from sqlite3 import Error
from datetime import datetime
from init import DB_NAME

def ts():
    return str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))).split('.')[0]

def connect(db_file=DB_NAME):
    try:
        return sqlite3.connect(db_file)
    except Error as e:
        print(e); return None

def init_db():
    conn = connect(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS data(
        name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        value TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS iot_devices(
        sys_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        dev_type TEXT NOT NULL,
        last_updated TEXT NOT NULL,
        dev_pub_topic TEXT NOT NULL,
        dev_sub_topic TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        message TEXT NOT NULL
    )""")
    conn.commit(); conn.close()

def add_data(name, value):
    conn = connect(); c = conn.cursor()
    c.execute('INSERT INTO data(name,timestamp,value) VALUES(?,?,?)', (name, ts(), str(value)))
    conn.commit(); conn.close()

def add_alert(level, message):
    conn = connect(); c = conn.cursor()
    c.execute('INSERT INTO alerts(timestamp,level,message) VALUES(?,?,?)', (ts(), level, message))
    conn.commit(); conn.close()
