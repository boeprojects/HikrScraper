import requests
import re
import hashlib
import pyodbc

from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime


cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-LAKDS51;DATABASE=HikrDB;Trusted_Connection=yes;')
cur = cnxn.cursor()

URL = "https://www.hikr.org/tour/"
r = requests.get(URL)
print(r.status_code)
if r.status_code == 200:
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.select("#contentmain_swiss .content-list")
    results = []
    print(len(tags))
    for tag in tags:
        result = {}
        title = tag.select_one("strong a").text
        title = title.replace("\n","")
        result["title"] = title
        url = tag.select_one("strong a").get("href")
        result["url"] = url
        result["id"] = hashlib.sha256(url.encode()).hexdigest()#generates hash-id from url
        teaser = tag.select_one(".content-list-intern_div").text
        teaser = teaser.replace("\n"," ")
        teaser = teaser.replace("\t"," ")
        teaser = teaser.replace("\r"," ")
        teaser = re.sub(r"\s{2,}"," ",teaser)
        teaser = teaser.strip()
        result["teaser"] = teaser
        print("-----")
        #nicht generisch sondern exemplarisch Arbeiten hier, um alle Sonderfälle einfach hinzufügen zu können [weniger Aufwand]
        for cell in tag.select(".content-list-intern_table td > span") + tag.select(".content-list-intern_table td > div"):
            attr = cell.get("title")
            if attr == "Wandern Schwierigkeit":
                result["difficulty_type"] = "hiking"
                result["difficulty_value"] = cell.text.strip()
            elif attr is None:
                result["location"] = cell.text.replace("\n","")
            elif attr == "Hochtouren Schwierigkeit":
                result["difficulty_type"] = "touring"
                result["difficulty_value"] = cell.text.strip()
            elif attr == "Klettern Schwierigkeit":
                result["difficulty_type"] = "climbing"
                result["difficulty_value"] = cell.text.strip()
            elif attr == "Tour Datum":
                ts = cell.text.replace("\n","").replace("\t","")
                result["ts"] = ts
                monate = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"]
                for i, monat in enumerate(monate):
                    ts = ts.replace(monat, f'{i+1}')#formatstring rechnet die monate durch und ersetzt 1, 2, usw.
                result["ts_parsed"] = datetime.strptime(ts,"%d %m %y")
            elif attr == "Ski Schwierigkeit":
                result["difficulty_type"] = "skiing"
                result["difficulty_value"] = cell.text.strip()
            elif attr == "Schneeshuhtouren Schwierigkeit": # da Schreibfehler, wäre bei korrekt geschr.Ergebnis hier ein or fällig
                result["difficulty_type"] = "snowshoe"
                result["difficulty_value"] = cell.text.strip()
            elif attr == "Mountainbike Schwierigkeit":
                result["difficulty_type"] = "mtb"
                result["difficulty_value"] = cell.text.strip()
            elif attr == "Ohne Datum": #könnte aktuelles Dat sein, oder pass wenn none sein soll!
                pass
            elif attr == "Klettersteig Schwierigkeit":
                result["difficulty_type"] = "via ferrata"
                result["difficulty_value"] = cell.text.strip()
            else:
                print(cell)
                assert False, f"'{attr}' not implemented"
        if "difficulty_type" not in result and "difficulty_value" not in result:
            result["difficulty_type"] = "unknow"
            result["difficulty_value"] = "unknow"
        results.append(result)
for result in results: #keine (), wir rufen nichts auf (sinnlos)
    pprint(result)# result ist dict und wird im pprint aufgefächert
    #print(len(result["teaser"]))
    #print(len(result["teaser"].encode("latin-1")))
    sql = """
        IF NOT EXISTS (SELECT TOP 1 * FROM posts WHERE id = ?)
        BEGIN
        INSERT INTO posts(
            title,
            url,
            id,
            teaser,
            difficulty_type,
            difficulty_value,
            location,
            ts,
            ts_parsed
        ) values(
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?)--geändert in Formatmethode für strings
        END
        ELSE
        BEGIN
            UPDATE posts
            SET title = ?
            WHERE id = ?;
        END
    """
    cur.execute(sql,
        result["id"],
        result["title"],
        result["url"],
        result["id"],
        result["teaser"],
        result["difficulty_type"],
        result["difficulty_value"],
        result["location"],
        result["ts"],
        result["ts_parsed"],
        result["title"],
        result["id"]
    )

cnxn.commit()#nicht eingerückt aus performancegründen [Transaktionsmodus einer DB]
cnxn.close()