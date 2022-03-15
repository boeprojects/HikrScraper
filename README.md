# HikrScraper

Webscraper Implementierung [hikr.org](https://www.hikr.org/) in einem ETL Prozess

Extraction: Data Collection und Extraktion von Daten aus Dokumenten/Posts einer Webseite
Ziel ist, die Daten passend in tabellarische Form aufzubereiten in einer Transformation, um sie in einer Datenbank zu laden.
Der Load wird mittles ODBC Connection in eine SQL Server Datenbank und dem Schreiben der Daten mittels Cursor durchgeführt.

## quickstart

requirements: SQL Server database

Lookup auf das Zielbild in der Datenbank
![Data Overview](bin/data_overview_01.png)

Wir generieren Daten mit einer Scraping-Funktion von einer passenden Webseite, in diesem Fall Hikr.org.
Dazu nutzen wir auch eine genaue Url zur korrekten Darstellung der Webseite ["https://www.hikr.org/tour/"]
Dabei werden die wichtigsten Angaben in Feldern aus dem html-Code extrahiert und sukkzessive exemplarisch als Datenfelder definiert und verarbeitet. (css Selector Extraktion und speichern in Variablen iterativ)
Wir verwenden die google developer tools auf html code Ebene und die Python Library Beautifulsoup [Selektion html Elemente]

Zum Einstieg müssen die Daten flexibel erweiterbar sein bis zur Zielstruktur, wir speichern die Daten in der Variable "result" und im dementsprechend flexiblen Datentyp Dictionary und gehen dann inkrementell vor.


Datenbanktechnisch wird als Primary Key die jewweilige URL eines Post (einer Seite) als Hashkey angelegt, so dass ein eindeutiger Primärschlüssel definiert wird!
```python
result["id"] = hashlib.sha256(url.encode()).hexdigest()#generates hash-id from url
```

Wichtig: Per ODBC Connect auf eine SQL Server Datenbank werden die Daten in der Datenbank geladen.
Mit diesen Mitteln kann sozusagen embedded in die Datenbank in sql geschrieben werden.
Dies hat den Vorteil, dass die gesamte SQL Funktionlität genutzt werde kann, einschließlich Fehlermeldungen aus der Datenbank.
```python
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
```

