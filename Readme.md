# Deepgreen-Harvester
Ein Skript, welches Deepgreen auf neue Veröffentlichungen überprüft. Getestet wurde es mit `Python 3.10.12` auf `Ubuntu 22.04.4 LTS`, es sollte aber in anderen Versionen auch funktionieren.

# Nutzung
## Installation
1.  Dieses Repositorium herunterladen (z.B. via `git clone` ). Im Folgenden wird angenommen, dass der Ordner `deepgreen-harvester` heißt.
2.  Linux-Konsole im Ordner `deepgreen-harvester` öffnen
3.  `python3 -m venv venv` zur Erzeugung einer neuen virtuellen Python-Umgebung namens `venv`
4.  `source venv/bin/activate`, um die `venv` zu aktivieren
5.  `pip install -r requirements.txt` zum Installieren der Abhängigkeiten des Skripts in der virtuellen Umgebung. Die Datei `requirements.txt` kann im Anschluss gelöscht werden.
6.  Die Datei `Config.ini` mit der eigenen Account-ID und dem eigenen API-Key befüllen (beides von Deepgreen bereitgestellt)
7.  Den Datenbanknamen sowie die Ordnernamen anpassen (hier sollte der vollständige Pfad angegeben werden, mit einem "/" am Schluss)
* `Loaded_Folder` = Ordner, in welchem die Daten von Deepgreen gespeichert werden
* `Shared_Folder` = Ordner, in welchem die Daten aus dem Loaded_Folder gepackt hinverschoben werden
8.  In den Dateien `Deepgreen_Harvest` und `Deepgreen_Move` muss am Anfang `Config.ini` durch den vollständigen Pfad zur `Config.ini` ersetzt werden, z.B. `/Pfad/zu/deepgreen-harvester/Config.ini`, damit die Ausführung via `cron` funktioniert
## Start
* `/Pfad/zu/deepgreen-harvester/venv/bin/python /Pfad/zu/deepgreen-harvester/Deepgreen_Harvest.py`, um den Download zu starten

* `/Pfad/zu/deepgreen-harvester/venv/bin/python /Pfad/zu/deepgreen-harvester/Deepgreen_Move.py`, um das Verschieben zu starten

# Logiken
## Harvest
Das Skript legt eine Datenbank an, die folgende Daten zu jedem gefundenen Datensatz gespeichert:

* ID = Deepgreen-interne ID des Datensatzes
* Uploaded = Zeitpunkt des Uploads des Datensatzes nach Deepgreen laut Deepgreen
* Downloaded = Zeitpunkt des lokalen Downloads des Datensatzes
* Last_Seen = Wann wurde der Datensatz zuletzt in Deepgreen gefunden
* Content_Size = Größe der Dateien in Byte
* Still_Available = 1, falls die Deepgreen-interne ID beim letzten Lauf des Skriptes gesehen wurde, 0 sonst

Das Skript greift auf die OAI-Schnittstelle von Deepgreen zu und iteriert über alle verfügbaren Datensätze. Es lädt die herunter, die noch nicht in der Datenbank sind, und speichert diese mit ihren Metadaten im `Loaded_Folder`, in einem eigenen Unterodner, der den Namen der Deepgreen-ID erhält. Außerdem wird die Datenbank aktualisiert. Bei einer Exception wird der aktuelle Datensatz übersprungen.

Empfohlen ist die tägliche Ausführung des Skriptes unter Linux via `cron`.

## Move
Das Skript erzeugt eine `.zip`-Datei, die alle Datensätze enthält, die derzeit im `Loaded_Folder` sind, und erzeugt dazu noch eine `.xslx`-Datei, die eine Liste der in den Datensätzen gefundenen DOIs mit Titel und Link enthält, welche auch in die `.zip`gelegt wird. Diese Datei wird dann in den `Shared_Folder` gespeichert. **Der `Loaded_Folder` wird durch Ausführung dieses Skriptes geleert, die Datensätze existieren nur noch in der `.zip`.**
Die `.zip` erhält den Namen `YYYY-MM.zip`, wobei `YYYY` dem Jahr und `MM` dem Monat entspricht, der vor sieben Tag war.

Empfohlen ist die monatliche Ausführung des Skriptes, innerhalb der ersten sechs Tage des Monats unter Linux via `cron`. Dadurch sind in der `.zip` alle Datensätze enthalten, die im letzten Monat neu bei Deepgreen verfügbar geworden sind, mit dem Namen des jeweiligen Monats.