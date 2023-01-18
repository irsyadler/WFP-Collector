import os, signal, os, logging, json
import psutil
from tinydb import TinyDB, Query
from datetime import datetime
from shutil import copy2

from configurations import *

############################################################
# Common Functions Declaration
############################################################

# Get current timestamp with proper format
def get_timestamp(getMiliseconds = False): # By default, does not return miliseconds
    if getMiliseconds == True:
        # return time.strftime('%Y-%m-%d %H:%M:%S.%f',  time.localtime(time.time()))
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    else:
        # return time.strftime('%Y-%m-%d %H:%M:%S',  time.localtime(time.time()))
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# Write data to file without catching any error, so the main try-catch will handle
def writeToFile(filename, data):
    file = open(filename,'w')
    file.write(data)
    file.close()


# Get database and query object with proper format
def get_database_query(dbPath, indent=config.data.JSON_INDENTION):
    database = TinyDB(dbPath, sort_keys=False, indent=indent, separators=(',', ': '))
    query = Query()
    return database, query


# Get all visit item and count from database
def read_visit_database(database, query, getvisitList = False):
    
    visitCounter = {
        visitStatus.PENDING: database.count(query.status == visitStatus.PENDING),
        visitStatus.COMPLETED: database.count(query.status == visitStatus.COMPLETED),
        visitStatus.FAILED: database.count(query.status == visitStatus.FAILED),
        'TOTAL': len(database)
    }
    
    if getvisitList == True: # Return both counter and visit list
        visitList = {
            visitStatus.PENDING: database.search(query.status == visitStatus.PENDING),
            visitStatus.COMPLETED: database.search(query.status == visitStatus.COMPLETED),
            visitStatus.FAILED: database.search(query.status == visitStatus.FAILED),
        }
        
        return visitCounter, visitList

    else:
        return visitCounter


# Append non-COMPLETED visit date and reason
def append_visit_records(database, query, visitName, timestamp, cause):
    # Get current record list
    currentRecordList = database.get(query.name == visitName)['records']

    # Append new data and update database
    currentRecordList.append([timestamp, cause])
    database.update({'records': currentRecordList}, query.name == visitName)


# Return the last status of ba
def get_last_ba_log_status(baLogFile):
    # Return -> None with errorCause if there is nothing to return
    # Return -> Text (non-formatted log) with None if there is no formatted log

    # Steps to search the log:
    # Step 1 - Get last line that are not empty
    # Step 2a - If that line is formatted, return the status
    # Step 2b - If that line is in non-formatted, mark that line and iterate until we fine the formatted
    # Step 3 - If there is no formatted log, return None or Text if available

    try:
        # If the log file is empty, return errorCause
        if os.stat(baLogFile).st_size == 0:
            return None, errorCause.LOG_EMPTY

        # -> Read log file and get all lines
        file = open(baLogFile, 'r')
        logLines = file.readlines() 
        file.close()

        # If there is no lines, return errorCause
        if len(logLines) == 0:
            return None, errorCause.LOG_EMPTY

    except:
        return None, errorCause.LOG_UNREADABLE

    

    lastLineContainText = None
    # print(str(no) + ' - ' + line)

    # -> Find ba formatted log
    for lineNumber, lineText in reversed(list(enumerate(logLines))):
        lineText = lineText.strip()
        
        if len(lineText) == 0:
            # Just skip this line
            pass

        # Validate the time format
        elif ((len(lineText) > 25) and
                (lineText[0] == '[') and
                (lineText[3] == '-') and
                (lineText[6] == ' ') and
                (lineText[9] == ':') and
                (lineText[12] == ':') and
                (lineText[15] == ']') and
                (lineText[16] == ' ')):
            
            # Check the third content of the split
            lineSplit = lineText.split()
            if len(lineSplit) == 4:
                # Validate the status format
                if (lineSplit[3][0] == '[') and (lineSplit[3][-1] == ']'):
                    # Return the status
                    return lineSplit[3], lastLineContainText

        elif lastLineContainText == None:
            # lastLineContainText still not marked, current line is non-formatted and non-empty
            lastLineContainText = lineText

    # At the end of the iteration, there is no formatted status in the log file
    if lastLineContainText != None:
        return lastLineContainText, None
    else: # If there is only lines with empty text
        return None, errorCause.LOG_EMPTY
      

# Filter errorReason text into indexed/known symbol or key
def errorReasonFilter(errorReason):
    # Check which text exist in the error
    # Start with the most obvious/explicit error that have the highest matches
    if "Timeout loading page after 300000ms" in errorReason:
        # FROM -> selenium.common.exceptions.TimeoutException: Message: Timeout loading page after 300000ms
        return errorCause.GET_TIMEOUT

    elif "reached a 90 second timeout without success" in errorReason:
        # FROM -> OSError: reached a 90 second timeout without success
        return errorCause.STEM_TIMEOUT

    elif "about:neterror?e=connectionFailure" in errorReason:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=connectionFailure&u=*****&c=UTF-8&d=Firefox can’t establish a connection to the server at *****.
        return errorCause.NET_CONNFAIL

    elif "about:neterror?e=netReset" in errorReason:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=netReset&u=*****&c=UTF-8&d=The connection to the server was reset while the page was loading.
        return errorCause.NET_RESET

    elif "about:neterror?e=dnsNotFound" in errorReason:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=dnsNotFound&u=*****&c=UTF-8&d=We can’t connect to the server at *****.
        return errorCause.NET_DNSNOTFOUND

    elif "about:neterror?e=nssFailure2" in errorReason:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=nssFailure2&u=*****&c=UTF-8&d=%20
        return errorCause.NET_NSSFAIL

    elif "about:neterror?e=netTimeout" in errorReason:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Reached error page: about:neterror?e=netTimeout&u=*****&c=UTF-8&d=The server at ***** is taking too long to respond.
        return errorCause.NET_TIMEOUT

    elif "Failed to decode response from marionette" in errorReason:
        # FROM -> selenium.common.exceptions.WebDriverException: Message: Failed to decode response from marionette
        return errorCause.MARION_DECOFAIL

    elif "No space left on device" in errorReason:
        # FROM -> OSError: [Errno 28] No space left on device: '*****'
        return errorCause.DEVICE_NOSPACE

    elif "[DUMPCAP_START_TIMEOUT]" in errorReason:
        # FROM -> Raise manually: Dumpcap start timeout
        return errorCause.DUMPCAP_START_TIMEOUT

    elif "[DUMPCAP_MISSING_FILE]" in errorReason:
        # FROM -> Raise manually: Pcap file missing
        return errorCause.DUMPCAP_MISSING_FILE

    

    else: # No known text pattern, return 'CHECK_LOG' flag
        return errorCause.CHECK_LOG


# Parse JSON file and return the result, None. If error, Return None, errorCouse
def parse_json_file(jsonFile):
    # Return -> None with errorCause if there is nothing to return or json is invalid
    # Return -> json (dictionary) with None if json is valid

    try:
        # If the log file is empty, return errorCause
        if os.stat(jsonFile).st_size == 0:
            return None, errorCause.LOG_EMPTY

        # -> Get file
        file = open(jsonFile, 'r')
        
        # Parse the data to json
        try:
            jsonDictionary = json.load(file)
            file.close()
            return jsonDictionary, None

        except:
            file.close()
            return None, errorCause.INVALID_JSON
  
    except:
        return None, errorCause.LOG_UNREADABLE


# Return a custom logger for individual visit log file
def create_logger(fileName, logName):
    
    # Create new log handler
    fileHandler = logging.FileHandler(fileName) # Handler for log files
    fileHandler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m-%d %H:%M:%S'))
    consoleHandler = logging.StreamHandler() # Handler for console log
    consoleHandler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s', datefmt='%m-%d %H:%M:%S'))

    # Create new logger
    logger = logging.getLogger(logName)
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)

    return logger


# Kill alive process
def kill_alive_process(killAll = False, excludeFile = None):

    appList = []

    if killAll == True: # Kill all including visit code and xvfb
        # Search alive app based on visit code
        for line in os.popen("ps ax | grep '" + config.directory.PROJECT + "' | grep -v grep"):
            if excludeFile not in line: # Do not kill serverCleaner.py
                appList.append(line)
        
        for line in os.popen("ps ax | grep Xvfb | grep -v grep"): # Search for xvfb
            appList.append(line)

        for line in os.popen("ps ax | grep dumpcap | grep -v grep"): # Search for dumpcap
            appList.append(line)

    else:
        # Search alive app based on app app directory 
        for line in os.popen("ps ax | grep '" + config.directory.APP + "' | grep -v grep"):
            appList.append(line)


    # Iterate over each app to kill it
    for app in appList:
        # Extracting Process ID from the output
        pid = app.split()[0]  

        # Terminating process 
        os.kill(int(pid), signal.SIGKILL) 
          
    # Return alive app counter
    return len(appList)


# Set exit node based on available parameters
def set_exit_node(torrc):

    # Check parameters
    if(config.crawling.EXIT_NODE_VALUE[0] == 'country'): # Exit Node by country
        torrc['GeoIPFile'] = os.path.join(config.directory.TBB, "Browser/TorBrowser/Data/Tor/geoip")
        torrc['GeoIPv6File'] =  os.path.join(config.directory.TBB, "Browser/TorBrowser/Data/Tor/geoip6")
        torrc['ExitNodes'] =  config.crawling.EXIT_NODE_VALUE[1]

    if(config.crawling.EXIT_NODE_VALUE[0] == 'ip'): # Exit Node by IP adress
        torrc['ExitNodes'] = config.crawling.EXIT_NODE_VALUE[1]
   
    # Return config
    return torrc


# Return crawlingInfo class into a dictionary
def crawlingInfoToDictionary():
    return {
        'hostname': crawlingInfo.hostname,
        'label': crawlingInfo.label,
        'visitAll': crawlingInfo.visitAll,
        'visitStatus': crawlingInfo.visitStatus,
        'visitAvailable': crawlingInfo.visitAvailable,
        'visitCurrent': crawlingInfo.visitCurrent,
        'isAllDone': crawlingInfo.isAllDone,
        'lastUpdate': crawlingInfo.lastUpdate
    }


# Dumpcap: Iterator over the children of a process
def get_child_process(parentPid):
    parent = psutil.Process(parentPid)
    for child in parent.children(recursive=True):
        yield child


# Return TRUE if dumpcap is running
def check_dumpcap_process(dumpcapProcess):
    if "dumpcap" in psutil.Process(dumpcapProcess.pid).cmdline():
        return dumpcapProcess.returncode is None
    for proc in get_child_process(dumpcapProcess.pid):
        if "dumpcap" in proc.cmdline():
            return True
    return False



