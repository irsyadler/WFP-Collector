############################################################
# Upload Collected Data And Send Telegram Notification
############################################################

import os
import urllib
import urllib.request
from shutil import copy2

# Import project module
from functions import *


def upload_data(silentMode=False):
    """ Uploading data to cloud using Rclone """

    # Copy database file if enable
    if config.cloud.uploadDatabase == True:
        copy2(config.path.database, os.path.join(config.path.output, config.main.statusFilename))

    # Check if called with silent flag
    silentFlag = '' if silentMode == True else '-P'

    # Upload using MOVE or COPY
    if config.cloud.deleteUploaded == True:
        # Main log should not be deleted (by move command)
        command = 'rclone move -L {} "{}" "{}" --exclude "{}"'.format(
            silentFlag, config.path.output, config.cloud.uploadPath, config.main.logFilename)
        exitCode = os.system(command)

        # Upload main log separately
        command = 'rclone copy -L {} "{}" "{}"'.format(silentFlag, os.path.join(config.path.output,
                                                       config.main.logFilename), config.cloud.uploadPath)
        exitCode = os.system(command)
    else:
        command = 'rclone copy -L {} "{}" "{}"'.format(silentFlag, config.path.output, config.cloud.uploadPath)
        exitCode = os.system(command)

    # Check exit code
    exitCode = os.waitstatus_to_exitcode(exitCode)
    if config.cloud.notifyOnFailed == True and exitCode > 0:
        notify_cloud_upload_failure()
    if config.cloud.stopCrawlingOnFailed == True and exitCode > 0:
        raise Exception(const.errorCause.CLOUD_UPLOAD_FAILED)


def check_cloud_data():
    """ Verify uploaded cloud data """

    # Put "-L" flag for symlinks traversal
    command = 'rclone check -L --one-way "{}" "{}"'.format(config.path.output, config.cloud.uploadPath)
    os.system(command)


def notify_cloud_upload_failure():
    """ Notify upload failure using Telegram Bot API """

    print("[NOTIFY_CLOUD_UPLOAD_FAILURE]")

    # Build message
    message = "[FAILED_CLOUD_UPLOAD] | {} | {} | {}".format(config.main.hostname, config.main.label, get_timestamp())

    # Call Telegram Bot API
    call_telegram_bot_api(message)


def notify_crawler_ended(crawlingInfo):
    """ Prepare and notify crawler ended using Telegram Bot API """

    print("[NOTIFY_CRAWLER_END]")

    # Set alive message
    status = 'Visited' if crawlingInfo.isAllDone == True else 'TERMINATED'

    # Calculate done percentage
    if int(crawlingInfo.visitAvailable) > 0:
        progressPercentage = round(int(crawlingInfo.visitCurrent) / int(crawlingInfo.visitAvailable) * 100)
    else:
        progressPercentage = 0

    # Calculate success percentage
    temp = int(crawlingInfo.visitAll[const.visitStatus.COMPLETED]) + int(crawlingInfo.visitAll[const.visitStatus.FAILED])
    if temp > 0:
        successPercentage = round(int(crawlingInfo.visitAll[const.visitStatus.COMPLETED]) / temp * 100)
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
    call_telegram_bot_api(message)


def call_telegram_bot_api(message, printRequestURL=False):
    """ Perform HTTPS call to the Telegram Bot API """

    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
        config.notification.token, config.notification.chatID, urllib.parse.quote_plus(message))

    if printRequestURL == True:  # For testing
        print("[TELEGRAM_REQUEST_URL]", url, "\n")

    contents = urllib.request.urlopen(url).read()
    print(contents.decode('utf-8'))


def test_telegram_token():
    """ Test the Telegram Bot API token """

    try:
        url = "https://api.telegram.org/bot{}/getMe".format(config.notification.token)
        contents = urllib.request.urlopen(url).read()

        return True
    except Exception as error:
        print(error)
        return False
