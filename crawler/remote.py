############################################################
# Perform Management Task From Remote Location
############################################################

import argparse
import json
import os

# Import project module
from run import *


def cleanServerProcess():
    """ Find active process to kill """

    print("Cleaning active process...")

    # Kill all process including crawling activity
    aliveProcessCounter = kill_alive_process(True, __file__)

    # Print the feedback
    print("Alive process: {}".format(aliveProcessCounter))


def getCrawlingStatus():
    """ Find active crawling activity and read database counter """

    # Initiate configuration
    init_config()

    # Set visitInfoFile location
    visitInfoFile = os.path.join(config.path.output, '0.status.json')
    statusData, error = None, None

    # Try to read the file
    try:
        # If the log file is empty, return errorCause
        if os.stat(visitInfoFile).st_size == 0:
            error = const.errorCause.LOG_EMPTY
        else:
            # -> Read log file and get all lines
            file = open(visitInfoFile, 'r')

            # Parse the data to json
            try:
                statusData = json.load(file)
            except:
                error = const.errorCause.INVALID_JSON
            finally:
                file.close()

    except:
        error = const.errorCause.LOG_UNREADABLE

    # Check for visitInfoFile error
    if statusData == None:
        statusData = {'error': error}

    # List for alive crawling activity
    appList = []

    # Search alive crawling activity
    for line in os.popen("ps ax | grep 'codes/run.py' | grep -v grep"):
        # Check if this is linux screen arguments ->  SCREEN -dmS mula sh -c cd /home/awan/nextawan; ls; python3 codes/run.py; exec bash
        if "SCREEN -dmS mula sh" not in line:
            appList.append(line)

    # Check if there is alive crawling activity
    if len(appList) > 0:
        statusData['alive'] = True
    else:
        statusData['alive'] = False

    # Print the data in json string
    print(json.dumps(statusData))


def serverUploader():
    """ Trigger upload data method """

    # Init configuration
    init_config()

    print("Uploading...")
    upload_data(silentMode=True)

    print("Checking...")
    check_cloud_data()


if __name__ == '__main__':

    # Check arguments
    parser = argparse.ArgumentParser(description='Remotely perform server-side action')
    parser.add_argument('-a', '--action', choices=['clean', 'status', 'upload'])
    args = parser.parse_args()

    if args.action == 'clean':
        cleanServerProcess()
    elif args.action == 'status':
        getCrawlingStatus()
    elif args.action == 'upload':
        serverUploader()
    else:
        print("ERROR: MISSING_ACTION")

