from functions import *
import os, os, urllib, urllib.request
from shutil import copy2

# Uploading data to cloud
def upload_data(silentMode = False):

    # Copy database file if enable
    if config.data.ENABLE_DATABASE_UPLOAD == True:
        copy2(config.directory.DATABASE_FILE, os.path.join(config.directory.DATA, config.directory.MAIN_STATUS_JSON))

    # Check if called with silent flag
    silentFlag = '' if silentMode == True else '-P'

    # Upload using MOVE or COPY
    if config.data.CLOUD_UPLOAD_DELETE_AFTER == True:
        # Main log should not be deleted (by move command)
        command = 'rclone move -L {} "{}" "{}" --exclude "{}"'.format(silentFlag, config.directory.DATA, config.data.CLOUD_UPLOAD_PATH, config.directory.MAIN_LOG_FILENAME)
        os.system(command)

        # Upload main log seperately
        command = 'rclone copy -L {} "{}" "{}"'.format(silentFlag, os.path.join(config.directory.DATA, config.directory.MAIN_LOG_FILENAME), config.data.CLOUD_UPLOAD_PATH)
        os.system(command)
    else:
        command = 'rclone copy -L {} "{}" "{}"'.format(silentFlag, config.directory.DATA, config.data.CLOUD_UPLOAD_PATH)
        os.system(command)

    


# Verify cloud data
def check_cloud_data():
    # Put "-L" flag for symlinks traversal
    command = "rclone check -L --one-way {} {}".format(config.directory.DATA, config.data.CLOUD_UPLOAD_PATH)
    os.system(command)


# Configure bot notification
def call_notification_bot():
    
    print("[NOTIFY_BOT]")

    # Set alive message
    status = 'Visited' if crawlingInfo.isAllDone == True else 'TERMINATED'
    
    # Calculate done percentage
    if int(crawlingInfo.visitAvailable) > 0:
        progressPercentage = round(int(crawlingInfo.visitCurrent) / int(crawlingInfo.visitAvailable)  * 100)
    else:
        progressPercentage = 0

    # Calculate success percentage
    temp = int(crawlingInfo.visitAll[visitStatus.COMPLETED]) + int(crawlingInfo.visitAll[visitStatus.FAILED])
    if temp > 0 :
        successPercentage = round(int(crawlingInfo.visitAll[visitStatus.COMPLETED]) / temp * 100)
    else:
        successPercentage = 0

    # Build message
    message = "{} | {} | {}\n{}: {}/{} ({}%)\nSuccess: {}%".format(crawlingInfo.hostname,
                                                 crawlingInfo.label,
                                                 crawlingInfo.lastUpdate,
                                                 status,
                                                 crawlingInfo.visitCurrent,
                                                 crawlingInfo.visitAvailable,
                                                 progressPercentage,
                                                 successPercentage)

    # Call Telegram Bot API
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(config.notification.TOKEN, config.notification.CHAT_ID, urllib.parse.quote_plus(message))
    contents = urllib.request.urlopen(url).read()
    print(contents.decode('utf-8'))

