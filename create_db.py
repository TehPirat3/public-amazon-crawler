"""
Creates connection to PostgeSQL database
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE

con = psycopg2.connect(dbname='postgres',
      user='postgres', host='127.0.0.1',
      password='16Sofi@99')

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE

cur = con.cursor()

# Use the psycopg2.sql module instead of string concatenation
# in order to avoid sql injection attacs.
cur.execute(sql.SQL("CREATE DATABASE amazon_crawler"))