from configparser import ConfigParser
import sqlite3
import os
import datetime
import requests
import json

CP = ConfigParser()
CP.read("Config.ini")

api_key = "api_key=" + CP.get("General", "API_Key")
account_key = CP.get("General", "AccountID")
Loaded_Folder = CP.get("Harvest_Details", "Loaded_Folder")
Databasefile = CP.get("Harvest_Details", "Database")


if not os.path.exists(Databasefile):
    con = sqlite3.connect(Databasefile)
    cur = con.cursor()
    cur.execute("CREATE TABLE Records(ID PRIMARY KEY, Uploaded, Downloaded, Last_Seen, Content_Size, Still_Available)")
    con.commit()
    con.close()
    ListOfIDs = []
else:
    con = sqlite3.connect(Databasefile)
    cur = con.cursor()
    ListOfIDs = list(map(lambda x:x[0], cur.execute("SELECT ID FROM Records").fetchall())) # Get list of IDs in neat little list
    con.close()

Datestr = "%Y-%m-%d#%H:%M:%S"
Now = datetime.datetime.now().strftime(Datestr)

Deepgreen_URL = "https://www.oa-deepgreen.de/api/v1/routed/" + account_key + "?since=1000-01-01&page=" # Hardcoded base url

Pagenum = 1


while Pagenum > 0:
    r = requests.get(Deepgreen_URL + str(Pagenum))
    Records = json.loads(r.text)["notifications"]
    if not Records:
        Pagenum = -1
    else:
        Pagenum += 1
        for record in Records:
            try:
                Now = datetime.datetime.now().strftime(Datestr)
                con = sqlite3.connect(Databasefile)
                cur = con.cursor()
                ID = record["id"]
                if ID not in ListOfIDs:
                    Downloadlink = record["links"][-1]["url"] + "?" + api_key
                    f = requests.get(Downloadlink)
                    if f.status_code == 200:
                        This_Folder = Loaded_Folder + ID + "/"
                        os.makedirs(This_Folder)
                        with open(This_Folder + "metadata.json", "w", encoding="UTF-8") as file:
                            json.dump(record, file, indent=4)
                        with open(This_Folder + "Files.zip", "wb") as file:
                            file.write(f.content)
                        Content_Size = len(f.content)
                        Uploaded_Date = datetime.datetime.strptime(record["created_date"], "%Y-%m-%dT%H:%M:%SZ")
                        
                        cur.execute("INSERT INTO Records VALUES(?, ?, ?, ?, ?, ?)", (ID, Uploaded_Date.strftime(Datestr), Now, Now, Content_Size, 1))
                else:
                    cur.execute("UPDATE Records SET Last_Seen = '" + Now + "' WHERE ID = '" + ID + "'")
                    ListOfIDs.remove(ID)
                con.commit()
                con.close()
            except Exception as E:
                print(E)
con = sqlite3.connect(Databasefile)
cur = con.cursor()
for ID in ListOfIDs:
    cur.execute("UPDATE Records SET Still_Available = 0 WHERE ID = '" + ID + "'")
con.commit()
con.close()
