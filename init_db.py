from matplotlib.pyplot import table
import pyodbc

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-LAKDS51;DATABASE=HikrDB;Trusted_Connection=yes;')
cur = cnxn.cursor()

sql = """
    create table posts(
        title VARCHAR(128),
        url VARCHAR(256),
        id VARCHAR(64) PRIMARY KEY,
        teaser varchar(1024),
        difficulty_type VARCHAR(32),
        difficulty_value VARCHAR(64),
        location VARCHAR(256),
        ts VARCHAR(64),
        ts_parsed date,
    )
"""
cur.execute(sql)
cnxn.commit() # wir nehmen änderungen an der db vor, wie speichern/schreiben!
