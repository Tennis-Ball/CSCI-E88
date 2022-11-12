#!/usr/bin/env python

import logging
import uuid
import random
import datetime
from datetime import date
from datetime import timedelta


log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.util import Date

KEYSPACE = "ks"

# for testing, creates a payment tuple with random values
urls = ["http://example.com/?url=124", "http://example.com/?url=056", "http://example.com/?url=066"]
countries = ["US", "KR", "CA", "FR", "CH"]
def event_click():
    userId = random.randint(0, 3)   
    dt = datetime.datetime(2022, 11, 12, 12, 00) - timedelta(hours=random.randint(1,4))
    print(dt)
    # dt = datetime.now() - timedelta(seconds=random.randint(1,5000))
    uuid_ = str(uuid.uuid4())
    url = urls[random.randrange(0,len(urls))]
    uaBrowser = "Chrome"
    uaOs = "windows"
    responseCode = 200
    ttfb = random.uniform(0, 1)
    country = countries[random.randrange(0, len(countries))]
    return (userId,dt,uuid_,url,uaBrowser, uaOs, responseCode, ttfb, country)

def main():
    # connect to the cluster
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    # if the keyspace already exists then drop it
    rows = session.execute("SELECT keyspace_name FROM system_schema.keyspaces")
    if KEYSPACE in [row[0] for row in rows]:
        log.info("dropping existing keyspace...")
        session.execute("DROP KEYSPACE " + KEYSPACE)

    # create the keyspace
    log.info("creating keyspace...")
    session.execute("""
        CREATE KEYSPACE %s
        WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
        """ % KEYSPACE)

    log.info("setting keyspace...")
    session.set_keyspace(KEYSPACE)

    # create the table
    log.info("creating table...")
    session.execute("""
        CREATE TABLE logs (
            userId int,
            dt timestamp,
            uuid text,
            url text,
            uaBrowser text,
            uaOs text,
            responseCode int,
            ttfb decimal,
            country text,
            PRIMARY KEY (country, url, dt)
        )
        """)

            # PRIMARY KEY (name,dt,uuid)

    # query = SimpleStatement("""
    #     INSERT INTO mytable (thekey, col1, col2)
    #     VALUES (%(key)s, %(a)s, %(b)s)
    #     """, consistency_level=ConsistencyLevel.ONE)

    # prepared statement query to insert values
    prepared = session.prepare("""
        INSERT INTO logs (userId, dt, uuid, url, uaBrowser, uaOs, responseCode, ttfb, country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """)

    # insert rows
    for i in range(100):
        log.info("inserting row %d" % i)
        pmt = event_click()
        session.execute(prepared.bind(pmt))

    # query results, aggregate (sum) amt by name and date (dt)
    future = session.execute_async(\
            "SELECT country, url, count(userId) FROM logs group by country, url WHERE dt <= '2022-11-12 12:00:00' and dt >= '2022-11-12 11:00:00' and userId = 0 and ttfb < 0.4")
            #"SELECT * FROM logs")

    log.info("Results...")

    try:
        rows = future.result()
    except Exception:
        log.exeception()

    # iterate the result rows
    for row in rows:
        # map cols in row to a string type
        row = map(lambda c: str(c),row)
        log.info('\t'.join(row))

    # delete the keyspace when done
    # session.execute("DROP KEYSPACE " + KEYSPACE)

if __name__ == "__main__":
    main()
