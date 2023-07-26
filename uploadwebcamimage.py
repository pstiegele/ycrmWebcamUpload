
# This script is uploading new webcam images out of the local ftp space up to the ycrm.de webspace
# to define new webcam images or change the paths just edit the files variable
# 
# Author: Paul Stiegele, 2020, paul@stiegele.name

# todo: notify if offline upload occurs
# todo: create notification if uploads occurs with an delay lesser than 90s
# hint: if python error occurs that host key is missing: just connect once per ssh to server, save host key and thats it


import pysftp
import os
import time
import requests

# ftp credentials for the ycrm.de website are stored here
host = "<host>.1and1-data.host"
username = "<username>"
password = "<password>"
telegramBotID = "<telegramBotID>"
telegramChatID = "<chatID>"
statusFilePath = "/mnt/ramdisk/"

# an array of webcam files which are under observation
# name: just for the .status file name, must be unique
# localFile: where the original image will be uploaded
# uploadPath: where the image should be uploaded (on the remote ftp)
# offlineFile: in case of an error: where the offline file is located
files = [
    {
        "name": "Webcam1",
        "localFile": "/mnt/ramdisk/ycrm01.jpg",
        "setAsOffline": False,
        "uploadPath": "webcam1",
        "offlineFile": "/home/ycrm/ycrmWebcamUpload/offline/ycrm01.jpg"
    },
    {
        "name": "Webcam2",
        "localFile": "/mnt/ramdisk/ycrm02.jpg",
        "setAsOffline": False,
        "uploadPath": "webcam2",
        "offlineFile": "/home/ycrm/ycrmWebcamUpload/offline/ycrm02.jpg"
    },
    {
        "name": "Webcam3",
        "localFile": "/mnt/ramdisk/ycrm03.jpg",
        "setAsOffline": False,
        "uploadPath": "webcam3",
        "offlineFile": "/home/ycrm/ycrmWebcamUpload/offline/ycrm03.jpg"
    }
]

# checks the file date and compares it to the current time. If the
# file is newer than 15s, nothing will happen, if the file is older
# than 600s, an offline file will be uploaded and when it is 
# between these two the actual file will be uploaded
def checkfile(file):
    timediff = time.time() - os.path.getmtime(file["localFile"])
    print("file is {:.0f}s old".format(timediff))
    if timediff > 600 or file["setAsOffline"]:
        print("2: should be offline")
        return 2 # upload offline image
    if timediff > 15:
        print("1: should be uploaded")
        return 1 # upload webcam image
    print("-1: nothing should happen")
    return -1 #upload nothing

# connects to ftp host and uploads the file to the specified path (+ the prefix: webcam/)
# preserve_mtime is to preserve the modification date
def upload(localFile, uploadPath):
    print("upload started for "+file["localFile"])
    with pysftp.Connection(host=host, username=username, password=password) as srv:
        with srv.cd(uploadPath): 
            srv.put(localFile, preserve_mtime=True) 


# to execute the script more often, its looping 3 times with 15s delay
for x in range(3):
    # loop through the files array to handle every webcam
    for file in files:
        print()
        print("----> now: "+str(file))
        # just care about the file if it exists
        # todo: upload offline image when no file exists
        if os.path.isfile(file["localFile"]):
            print("file exists")
            # check if file needs to be uploaded
            fileToUpload = checkfile(file)
            if fileToUpload == 1: #upload
                f = ""
                # opens status file if file was already uploaded
                # the if else is just to create the status file if it does not exist yet
                if os.path.isfile(os.path.join(statusFilePath, "webcam_" + file["name"] + ".status")):
                    f = open(os.path.join(statusFilePath, "webcam_"+file["name"]+".status"), "r")
                else:
                    f = open(os.path.join(statusFilePath, "webcam_"+file["name"]+".status"), "w+")
                fcontent = f.read()
                # if status file has the same timestamp as the file, the file was already
                # uploaded
                if fcontent != str(os.path.getmtime(file["localFile"])):
                    print("status file checked: diff detected")
                    # everything is okay, so upload the file
                    upload(file["localFile"], file["uploadPath"])
                    # file is uploaded, so replace the timestamp in the status file with the
                    # modified date of the current file
                    f.close()
                    f = open(os.path.join(statusFilePath, "webcam_"+file["name"]+".status"), "w+")
                    f.write(str(os.path.getmtime(file["localFile"])))
                else:
                    print("status file checked: no diff detected, abort upload")
                f.close()
            elif fileToUpload == 2: # offline
                # read status file
                if os.path.isfile(os.path.join(statusFilePath, "webcam_"+file["name"]+".status")):
                    f = open(os.path.join(statusFilePath, "webcam_"+file["name"]+".status"), "r")
                else:
                    f = open(os.path.join(statusFilePath,"webcam_"+file["name"]+".status"), "w+")
                fcontent = f.read()
                # if status file already contains "offline" the last upload was the offline file
                # so its not necessary to upload the file again
                if fcontent != "offline":
                    print("status file checked: diff detected")
                    # upload the offline image
                    # todo: check if offline file exists
                    upload(file["offlineFile"], file["uploadPath"])
                    # write in the status file, that the last upload was an offline upload
                    f.close()
                    f = open(os.path.join(statusFilePath, "webcam_"+file["name"]+".status"), "w+")
                    f.write("offline")
                    payload = { 'chat_id' : telegramChatID, 'text' : 'YCRM-Webseite: ' + file["name"] + ' is offline.' }
                    res = requests.post('https://api.telegram.org/bot' + telegramBotID + '/sendMessage', data=payload)
                else:
                    print("status file checked: no diff detected, abort upload")
                f.close()
        else:
            print("file not found")
            payload = { 'chat_id' : telegramChatID, 'text' : 'YCRM-Webseite: ' + file["name"] + ' file not found.' }
            res = requests.post('https://api.telegram.org/bot' + telegramBotID + '/sendMessage', data=payload)
    print()     
    print()
    print()
    print("###### sleep ######")     
    # sleep 15s and then start again               
    time.sleep(15)
