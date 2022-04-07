import os
import json as js
import shutil as sh
import requests as req
import threading as th
import traceback as trcb
from datetime import date as dt

# Global Variables
username ='your_PcCloud_username'
password ='your_PcCloud_password'
globalvarList = []

# Functions
def CompressFolder(localFolder):
    try:
       today = dt.today().strftime("%m_%d_%y")
       compressFilePath = localFolder+"\\"+today
       print("compressing folder, please wait... \n")
       sh.make_archive(compressFilePath, 'zip', localFolder)
       print("Folder compressions completed :) \n")
       compressFilePath = compressFilePath+".zip"
       globalvarList.append(compressFilePath)
    except:
       print(trcb.format_exc())
       

def pcCloudApiCall(pcCloudFolder, localFolder):
   try:
      r = req.get("https://api.pcloud.com/login?username="+username+"&password="+password)
      json_login = js.loads(r.text)
      auth = json_login['auth']
      r2 = req.get("https://api.pcloud.com/listfolder?path=/"+pcCloudFolder+"&auth="+auth)
      json_folder = js.loads(r2.text)
      folderID = json_folder['metadata']['folderid']
      globalvarList.append(auth)
      globalvarList.append(str(folderID))
   except:
      print(trcb.format_exc())


def pcCloudSaveFile(pcCloudFolder, compressFilePath):
   print("\n contacting PC Cloud to save file, operation may take several minutes depending on the file size...")
   try:
      with open(globalvarList[0], 'rb') as f:
         data = f.read()
      uri = "https://api.pcloud.com/uploadfile?renameifexists=1&folderid="+globalvarList[2]+"&filename=backup"+str(dt.today().strftime("%m_%d_%y"))+".zip&auth="+globalvarList[1]
      r3 = req.post(uri, data=data, headers = {'Content-Type': 'application/zip'})
      if(r3.status_code==200):
         return True
   except:
       return False



# MAIN
if __name__ == "__main__":
    print("\n Enter the PC Cloud folder name in which you want to save your files (must be in root): \n")
    pcCloudFolder = input()
    print("\n Enter the full path of the local folder to backup on PC Cloud: \n")
    localFolder = input()
    jobs = []
    thread_compress = th.Thread(target=CompressFolder(localFolder))
    jobs.append(thread_compress)
    thread_apicall = th.Thread(target=pcCloudApiCall(pcCloudFolder, localFolder))
    jobs.append(thread_apicall)
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
    isFileSaved = pcCloudSaveFile(pcCloudFolder, globalvarList[0])
    if(isFileSaved):
        print("Backup operation completed Successfully :) ==> you can find your file on Pc Cloud: https://www.pccloud.com ")
    else:
       print("Cannot complete operation, one or more error occurred. Please retry :( ")

    os.remove(globalvarList[0])

