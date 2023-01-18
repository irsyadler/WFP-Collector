############################################################
# Common Functions Declaration
############################################################

import os
import shutil
import signal
import logging
import json
import subprocess
import time
import psutil
import hashlib
import ntpath
import gzip
from tinydb import TinyDB, Query
from datetime import datetime

# Import project module
import constants as const
import configurations as config


def parse_config_file(returnOptionProperties=None):
    """ Parse config.json file and set the value """

    # Check config.json file existence
    if os.path.isfile(config.path.configuration):
        # Parse config.len(optionName) == 1
        try:
            fileObject = open(config.path.configuration, "r")
            configDict = json.load(fileObject)
            fileObject.close()

            # Parse main config
            if 'config' in configDict:
                for option in configDict['config']:

                    optionName = option.split('.')
                    # Ensure option has class name and option name. Example: main.HOSTNAME / main.LABEL
                    # And ensure option class exist in configurations.py
                    if len(optionName) > 1 and hasattr(config, optionName[0]):
                        # Ensure option name exist in class of configurations.py
                        if hasattr(getattr(config, optionName[0]), optionName[1]):
                            # Set option value
                            setattr(getattr(config, optionName[0]), optionName[1], configDict['config'][option])
                        else:
                            print("[ERROR_CONFIG_FILE] '{}' option is not exist in '{}' class of configurations.py".format(
                                optionName[1], optionName[0]))
                            return False
                    else:
                        print("[ERROR_CONFIG_FILE] '{}' class is not exist in configurations.py".format(optionName[0]))
                        return False

            # Parse torrc config
            if 'torrc' in configDict:
                for option in configDict['torrc']:
                    config.crawler.torrc[option] = configDict['torrc'][option]

            # Parse torrc config
            if 'browserPreference' in configDict:
                for option in configDict['browserPreference']:
                    config.crawler.browserPreference[option] = configDict['browserPreference'][option]

            if returnOptionProperties == None:  # Return true for normal config parse
                return True
            else:  # Check for additional config
                additionalDict = {}
                if returnOptionProperties in configDict:
                    for option in configDict[returnOptionProperties]:
                        additionalDict[option] = configDict[returnOptionProperties][option]
                else: # Check for additional config
                    print("[ERROR_CONFIG_FILE] Missing '{}' properties in the config file".format(returnOptionProperties))
                    return False
                return additionalDict
        except Exception as error:
            print("[ERROR_CONFIG_FILE] Unable to read: {}\n".format(config.path.configuration), error)
            return False
    else:
        print("[ERROR_CONFIG_FILE] File not found: {}".format(config.path.configuration))
        return False


def get_timestamp(getMilliseconds=False):  # By default, does not return milliseconds
    """ Get current timestamp with proper format """
    if getMilliseconds == True:
        # return time.strftime('%Y-%m-%d %H:%M:%S.%f',  time.localtime(time.time()))
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    else:
        # return time.strftime('%Y-%m-%d %H:%M:%S',  time.localtime(time.time()))
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def writeToFile(filename, data):
    """ Write data to file without catching any error, so the main try-catch will handle """
    file = open(filename, 'w')
    file.write(data)
    file.close()


def get_database_query(dbPath, indent=config.data.jsonIndentation):
    """ Get database and query object with proper format """
    database = TinyDB(dbPath, sort_keys=False, indent=indent, separators=(',', ': '))
    query = Query()
    return database, query


def read_visit_database(database, query, getVisitData=False):
    """ Get all visit data and count from database """
    visitCounter = {
        const.visitStatus.PENDING: database.count(query.status == const.visitStatus.PENDING),
        const.visitStatus.COMPLETED: database.count(query.status == const.visitStatus.COMPLETED),
        const.visitStatus.FAILED: database.count(query.status == const.visitStatus.FAILED),
        'TOTAL': len(database)
    }

    if getVisitData == True:  # Return both counter and visit data
        visitDatabase = {
            const.visitStatus.PENDING: database.search(query.status == const.visitStatus.PENDING),
            const.visitStatus.COMPLETED: database.search(query.status == const.visitStatus.COMPLETED),
            const.visitStatus.FAILED: database.search(query.status == const.visitStatus.FAILED),
        }

        return visitCounter, visitDatabase

    else:
        return visitCounter


def append_visit_records(database, query, visitName, timestamp, cause):
    """ Append non-COMPLETED visit date and reason """
    # Get current record list
    currentRecordList = database.get(query.name == visitName)['records']

    # Append new data and update database
    currentRecordList.append([timestamp, cause])
    database.update({'records': currentRecordList}, query.name == visitName)


def append_activity_json(LOG, filePath, text, error):
    """ Append errorReason to act.json if file exist """
    # TODO: What happen if this process failed / exception occur
    try:
        # Check if act.json exist
        if os.path.isfile(filePath):
            # Parse JSON
            fileObject = open(filePath, 'r')
            data = json.load(fileObject)
            fileObject.close()

            # Add error info
            data.update({'error': error})

            writeToFile(filePath, json.dumps(data, indent=config.data.jsonIndentation))

    except:
        LOG.warning('[UNABLE_TO_PARSE_ACT_JSON]: ' + filePath)


def read_last_crawl_log(crawlLogFile):
    """ Return the last status of crawling activity """

    # Steps to search the log:
    # Step 1 - Get last line that are not empty
    # Step 2 - Return the text after parse using errorReasonFilter()

    try:
        # If the log file is empty, return errorCause
        if os.stat(crawlLogFile).st_size == 0:
            return const.errorCause.LOG_EMPTY

        # -> Read log file and get all lines
        file = open(crawlLogFile, 'r')
        logLines = file.readlines()
        file.close()

        # If there is no lines, return errorCause
        if len(logLines) == 0:
            return const.errorCause.LOG_EMPTY

    except:
        return const.errorCause.LOG_UNREADABLE

    # -> Find formatted log
    for lineNumber, lineText in reversed(list(enumerate(logLines))):
        lineText = lineText.strip()

        if len(lineText) > 0:
            return errorReasonFilter(lineText)

    else:  # If there is only lines with empty text
        return const.errorCause.LOG_EMPTY


def errorReasonFilter(errorText):
    """ Filter errorReason text into indexed/known symbol or key """

    # Check which text exist in the error
    # Start with the most obvious/explicit error that have the highest matches
    if "Timeout loading page after 300000ms" in errorText:
        # FROM -> selenium.common.exceptions.TimeoutException: Message: Timeout loading page after 300000ms
        return const.errorCause.GET_TIMEOUT

    elif "reached a 90 second timeout without success" in errorText:
        # FROM -> OSError: reached a 90 second timeout without success
        return const.errorCause.STEM_TIMEOUT

    elif "about:neterror?e=connectionFailure" in errorText:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=connectionFailure&u=*****&c=UTF-8&d=Firefox can’t establish a connection to the server at *****.
        return const.errorCause.NET_CONNFAIL

    elif "about:neterror?e=netReset" in errorText:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=netReset&u=*****&c=UTF-8&d=The connection to the server was reset while the page was loading.
        return const.errorCause.NET_RESET

    elif "about:neterror?e=dnsNotFound" in errorText:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=dnsNotFound&u=*****&c=UTF-8&d=We can’t connect to the server at *****.
        return const.errorCause.NET_DNSNOTFOUND

    elif "about:neterror?e=nssFailure2" in errorText:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=nssFailure2&u=*****&c=UTF-8&d=%20
        return const.errorCause.NET_NSSFAIL

    elif "about:neterror?e=netTimeout" in errorText:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=netTimeout&u=*****&c=UTF-8&d=The server at ***** is taking too long to respond.
        return const.errorCause.NET_TIMEOUT

    elif "Failed to decode response from marionette" in errorText:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Failed to decode response from marionette
        return const.errorCause.MARION_DECOFAIL

    elif "No space left on device" in errorText:
        # FROM -> OSError: [Errno 28] No space left on device: '*****'
        return const.errorCause.DEVICE_NOSPACE

    else:  # No known text pattern, return 'CHECK_LOG' flag
        return const.errorCause.CHECK_LOG


def create_logger(fileName, logName):
    """ Return a custom logger for individual visit log file """
    # Create new log handler
    fileHandler = logging.FileHandler(fileName)  # Handler for log files
    fileHandler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m-%d %H:%M:%S'))
    consoleHandler = logging.StreamHandler()  # Handler for console log
    consoleHandler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s', datefmt='%m-%d %H:%M:%S'))

    # Create new logger
    logger = logging.getLogger(logName)
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    return logger


def kill_alive_process(killAll=False, excludeFile=None):
    """ Get and kill all alive process """

    appList = []

    if killAll == True:  # Kill all including visit code and xvfb
        # Search alive app based on visit code
        for line in os.popen("ps ax | grep '{}' | grep -v grep".format(config.path.project)):
            if excludeFile not in line:  # Do not kill the caller of this function
                if config.main.test == True and ('test/test' in line or "test.py" in line):
                    pass  # Do not kill the test script
                else:
                    appList.append(line)

        for line in os.popen("ps ax | grep Xvfb | grep -v grep"):  # Search for xvfb
            appList.append(line)

        for line in os.popen("ps ax | grep dumpcap | grep -v grep"):  # Search for dumpcap
            appList.append(line)

    else:
        # Search alive app based on app directory
        for line in os.popen("ps ax | grep '{}' | grep -v grep".format(config.path.app)):
            appList.append(line)

        # Search for alive dumpcap
        for line in os.popen("ps ax | grep dumpcap | grep -v grep"):
            appList.append(line)

    # Iterate over each app to kill it
    for app in appList:
        # Retrieve Process ID from the output
        pid = app.split()[0]

        # Terminating process
        os.kill(int(pid), signal.SIGKILL)

    # Return alive app counter
    return len(appList)


def set_exit_node(torrc):
    """ Set exit node based on available parameters """

    # Check parameters
    if (config.crawler.exitNodeParam[0] == 'country'):  # Exit Node by country
        torrc['GeoIPFile'] = os.path.join(config.path.browser, "Browser/TorBrowser/Data/Tor/geoip")
        torrc['GeoIPv6File'] = os.path.join(config.path.browser, "Browser/TorBrowser/Data/Tor/geoip6")
        torrc['ExitNodes'] = config.crawler.exitNodeParam[1]

    if (config.crawler.exitNodeParam[0] == 'ip'):  # Exit Node by IP address
        torrc['ExitNodes'] = config.crawler.exitNodeParam[1]

    # Return config
    return torrc


def crawlingInfoToDictionary(crawlingInfo: const.crawlingInfo):
    """ Return crawlingInfo class into a dictionary """
    
    return crawlingInfo.__dict__


def get_child_process(parentPid):
    """ Dumpcap: Iterator over the children of a process """

    parent = psutil.Process(parentPid)
    for child in parent.children(recursive=True):
        yield child


def start_dumpcap_process(pcapFilePath):
    """ Execute dumpcap command and ensure it is running """
    dumpcapCommand = 'dumpcap -a duration:{} -a filesize:{} -i {} -s 0 -f "{}" -w "{}"'.format(
        config.pcap.maxDumpDuration, config.pcap.maxDumpSize, config.pcap.networkInterface, config.pcap.filteringRule, pcapFilePath)

    # Execute dumpcap process
    dumpcapProcess = subprocess.Popen(dumpcapCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    dumpcapTimeout = float(config.pcap.startTimeout)

    # Check dumpcap process
    while dumpcapTimeout > 0 and not check_dumpcap_process(dumpcapProcess):
        time.sleep(0.1)
        dumpcapTimeout -= 0.1

    if dumpcapTimeout < 0:
        raise ErrorFound(const.errorCause.DUMPCAP_START_TIMEOUT)
    else:
        return dumpcapProcess


def stop_dumpcap_process(dumpcapProcess):
    """ Stop dumpcap child and main process """

    for child in get_child_process(dumpcapProcess.pid):
        child.kill()
    dumpcapProcess.kill()


def check_dumpcap_process(dumpcapProcess):
    """ Return True if dumpcap is running """

    if "dumpcap" in psutil.Process(dumpcapProcess.pid).cmdline():
        return dumpcapProcess.returncode is None
    for proc in get_child_process(dumpcapProcess.pid):
        if "dumpcap" in proc.cmdline():
            return True
    return False


def generate_file_hash(fileList: dict):
    """ Return dict of collected file with sha256 digest """

    # Will also generate __master__ hash by generating sha256 digest from all files' generated sha256 digest
    # The fileList will be sort based on the filePath

    hashList = {}
    allDigest = ""

    # Iterate each collected file (in filepath ascending order)
    for key, filePath in dict(sorted(fileList.items(), key=lambda file: file[1])).items():
        # Ensure file exist
        if os.path.isfile(filePath):
            digest = hashlib.sha256()
            with open(filePath, "rb") as file:
                while True:
                    data = file.read(65536)
                    if not data:
                        break
                    digest.update(data)

            # Add digest to hashList
            key = ntpath.basename(filePath)
            hashList[key] = digest.hexdigest()
            allDigest += hashList[key]

    # Sort filename and generate master sha256 digest
    hashList['__master__'] = hashlib.sha256(allDigest.encode('UTF-8')).hexdigest()

    return hashList


def compress_file(LOG, filePath, fileName):
    """" GZIP collected file and remove existing file """

    LOG.info("[COMPRESSING_COLLECTED_FILE]: {}".format(fileName))
    compressFilePath = filePath + '.gz'
    try:
        sourceFile = open(filePath, 'rb')
        compressFile = gzip.open(compressFilePath, 'wb')
        shutil.copyfileobj(sourceFile, compressFile)
        compressFile.close()
        sourceFile.close()

        # Remove original file
        os.remove(filePath)
    except Exception as error:
        LOG.warning("[COMPRESSION_ERROR: {}\n".format(fileName), error)
        # Delete if gzip exist
        if os.path.exists(compressFilePath):
            os.remove(compressFilePath)


def process_collected_file(LOG, filePath, fileConfig, visitStatus, missingWarning=False):
    """ Post-process the collected file based on const.file option """

    if fileConfig == const.file.SKIP:
        pass  # Do nothing
    elif os.path.exists(filePath):
        fileName = ntpath.basename(filePath)
        if fileConfig == const.file.SAVE:
            pass  # Do nothing
        elif fileConfig == const.file.SAVE_COMPRESS:
            compress_file(LOG, filePath, fileName)
        elif fileConfig == const.file.COMPRESS_REMOVE_SUCCEED and visitStatus != const.crawlingStatus.COMPLETED:
            compress_file(LOG, filePath, fileName)
        elif (fileConfig == const.file.REMOVE) or ((fileConfig == const.file.REMOVE_SUCCEED or fileConfig == const.file.COMPRESS_REMOVE_SUCCEED) and visitStatus == const.crawlingStatus.COMPLETED):
            LOG.info("[REMOVING_COLLECTED_FILE]: {}".format(fileName))
            os.remove(filePath)
    else:  # File not exist
        if missingWarning == True:
            LOG.warning("[MISSING_COLLECTED_FILE]: {}".format(fileName))


# Custom Exception Class
class ErrorFound(Exception):
    """ Raise custom error """
    pass
