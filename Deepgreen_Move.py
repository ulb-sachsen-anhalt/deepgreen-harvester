from configparser import ConfigParser
import os
import datetime
import json
import shutil
import openpyxl

CP = ConfigParser()
CP.read("Config.ini")

Loaded_Folder = CP.get("Harvest_Details", "Loaded_Folder")
Shared_Folder = CP.get("Move_Details", "Shared_Folder")

LastMonthDate = datetime.datetime.now() - datetime.timedelta(days=7)
This_Month = str(LastMonthDate.month)
This_Year = str(LastMonthDate.year)
if len(This_Month) < 2:
    This_Month = "0" + This_Month
Filename = This_Year + "-" + This_Month
Foldername = Filename + "/"
os.mkdir(Foldername)
Excellist = []
for subfolder in os.listdir(Loaded_Folder):
    with open(Loaded_Folder + subfolder + "/metadata.json", "rb") as file:
        jsondata = json.load(file)
    for identifier in jsondata["metadata"]["identifier"]:
        if identifier["type"] == "doi":
            doi = identifier["id"]
    title = jsondata["metadata"]["title"]
    Excellist.append((subfolder, doi, title))
    shutil.move(Loaded_Folder + subfolder, Foldername + subfolder)

wb = openpyxl.Workbook()
ws = wb.active
ws.append(["Deepgreen-ID", "DOI", "DOI-Link", "Title"])
for (subfolder, doi, title) in Excellist:
    ws.append([subfolder, doi, '=HYPERLINK("{}", "{}")'.format('https://doi.org/' + doi, doi), title])
wb.save(Foldername + "DOI_Liste.xlsx")
shutil.make_archive(base_dir = Foldername, format = 'zip', base_name = Shared_Folder + Filename)
shutil.rmtree(Foldername)
