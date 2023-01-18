############################################################
# WFP-Collector Testing Script
############################################################

import os
import importlib.util
import pathlib
import subprocess
import sys
import importlib.metadata
import apt
import json
from scapy.all import PcapReader

# Relative path to the WFP-Collector crawler and database creation directories
TEST_PATH = pathlib.Path(__file__).parent
CRAWLER_PATH = str((TEST_PATH / '../crawler').resolve())
DATABASE_CREATOR_PATH = str((TEST_PATH / '../database/create.py').resolve())

# Import relative modules
sys.path.append(CRAWLER_PATH)
from functions import *
from uploaderNotifier import call_telegram_bot_api

# Set the test label and filename prefix
TEST_LABEL = 'TEST_' + str(time.time()).split('.')[0]
TEST_CRAWLER_FILENAME_PREFIX = 'test_d_1'

# Path related to testing process
VISIT_DATABASE_SOURCE_PATH = os.path.join(TEST_PATH.resolve(), 'testVisitDatabaseSource.csv')
CLOUD_UPLOAD_TEST_FILE = os.path.join(TEST_PATH.resolve(), 'testCloudUpload.txt')
CRAWLER_OUTPUT_PATH = os.path.join(TEST_PATH.resolve(), TEST_LABEL)
VISIT_DATABASE_PATH = os.path.join(CRAWLER_OUTPUT_PATH, 'testVisitDatabase.json')
CRAWLER_OUTPUT_CHECK_FILE_PATH = os.path.join(CRAWLER_OUTPUT_PATH, 'test_d_1.act.json')

# Setup configuration
SETUP_CONFIG = {}

# Information URL
HELP_TOR_BROWSER = ""
HELP_GECKODRIVER = ""

# Dumpcap test config
DUMPCAP_PING_ADDRESS = '1.1.1.1'
DUMPCAP_TESTING_SECONDS = 5

# Minimum apps version
MIN_VER = {
    'python3.minor': 10,
    'pip.major': 20,
    'firefox.major': 108,
    'torBrowser.major': 11,
    'geckodriver.minor': 32
}


def check_required_system_applications():
    """ Ensure the required system applications are available """

    proceed = True
    aptCache = apt.Cache()

    # Check Python version
    if sys.version_info.major != 3 or sys.version_info.minor < MIN_VER['python3.minor']:
        proceed = False
        print("ERROR_APPLICATION_VERSION: Python {}.{}\nPlease update it using: apt install python3".format(
            sys.version_info.major, sys.version_info.minor))

    # Check if Python PIP is installed
    try:
        aptCache['python3-pip']

        # Check PIP version
        import pip
        if int(pip.__version__.split('.')[0]) < MIN_VER['pip.major']:
            proceed = False
            print("ERROR_APPLICATION_VERSION: pip {}\nPlease update it using: apt install python3-pip".format(pip.__version__))

    except KeyError:
        proceed = False
        print("ERROR_MISSING_APPLICATION: PIP\nPlease install it using: apt install python3-pip")

    # Check if Firefox is installed
    try:
        aptCache['firefox']

        # Check Firefox version
        try:
            firefoxVersion = subprocess.check_output(
                ['firefox', '--version']).decode(sys.stdout.encoding).strip()  # Example: Mozilla Firefox 108.0.1
            temp = firefoxVersion.split()[2]  # Example: 108.0.1
            temp = temp.split('.')
            if int(temp[0]) < MIN_VER['firefox.major']:
                proceed = False
                print("ERROR_APPLICATION_VERSION: {}\nPlease update it using: apt install firefox && sudo snap refresh firefox".format(firefoxVersion))
        except Exception as e:
            print("VERSION_WARNING: Unable to get Firefox version -> ", e)

    except KeyError:
        proceed = False
        print("ERROR_MISSING_APPLICATION: Firefox\nPlease install it using: apt install firefox")

    # Check if Xvfb is installed
    try:
        aptCache['xvfb']
    except KeyError:
        proceed = False
        print("ERROR_MISSING_APPLICATION: Xvfb\nPlease install it using: apt install xvfb")

    # Check if Wireshark is installed
    try:
        aptCache['wireshark']
    except KeyError:
        proceed = False
        print("ERROR_MISSING_APPLICATION: Xvfb\nPlease install it using: apt install wireshark")

    return proceed


def check_required_tbb_and_gecko():
    """ Ensure the Tor Browser and Geckodriver are available """

    proceed = True

    # Check Tor Browser directory
    if os.path.isdir(config.path.browser):
        # Check Tor Browser version
        jsonFile = os.path.join(config.path.browser, 'Browser/tbb_version.json')

        if os.path.isfile(jsonFile):
            # Parse tbb_version.json and compare the version
            try:
                fileObject = open(jsonFile, "r")
                jsonData = json.load(fileObject)
                fileObject.close()

                if int(jsonData['version'].split('.')[0]) < MIN_VER['torBrowser.major']:
                    proceed = False
                    print("ERROR_BROWSER_VERSION: Tor Browser {}\nPlease refer: {}".format(jsonData['version'], HELP_TOR_BROWSER))

                # Check if HAR extension is exist
                if os.path.isfile(os.path.join(config.path.browser, SETUP_CONFIG['harExportTriggerExtensionPath'])) == False:
                    proceed = False
                    print("ERROR_BROWSER_EXTENSION: Missing HAR Export Trigger extension.\nPlease refer: {}".format(HELP_TOR_BROWSER))

                # Check if HAR enabled in extension preferences
                torBrowserExtensionPreferencesPath = os.path.join(
                    config.path.browser, SETUP_CONFIG['torBrowserExtensionPreferencesPath'])
                if os.path.isfile(torBrowserExtensionPreferencesPath) == True:
                    # Parse extension preferences

                    fileObject = open(torBrowserExtensionPreferencesPath, "r")
                    jsonData = json.load(fileObject)
                    fileObject.close()
                    if ('harexporttrigger@getfirebug.com' in jsonData) and ('permissions' in jsonData['harexporttrigger@getfirebug.com']) and 'internal:privateBrowsingAllowed' in jsonData['harexporttrigger@getfirebug.com']['permissions']:
                        # HAR Export Trigger allowed in Private Window
                        pass
                    else:
                        proceed = False
                        print("ERROR_BROWSER_EXTENSION: HAR Export Trigger extension is 'Disabled' in Private Window.\nPlease refer: {}".format(
                            HELP_TOR_BROWSER))
                else:
                    proceed = False
                    print("ERROR_BROWSER_EXTENSION: Tor Browser's extension preferences is missing.\nPlease refer: {}".format(
                        HELP_TOR_BROWSER))

            except Exception as error:
                proceed = False
                print(error)
                print("ERROR_MALFORMED_BROWSER: Unable to determine the Tor Browser version\nPlease refer: {}".format(HELP_TOR_BROWSER))
        else:
            proceed = False
            print("ERROR_MALFORMED_BROWSER: Unable to read the Tor Browser version\nPlease refer: {}".format(HELP_TOR_BROWSER))

    else:
        proceed = False
        print("ERROR_MISSING_BROWSER: Tor Browser\nPlease refer: {}".format(HELP_TOR_BROWSER))

    # Check Geckodriver binary
    if os.path.isfile(config.path.gecko):
        # Check Geckodriver version
        try:
            commandResult = subprocess.check_output(
                [config.path.gecko, '--version']).decode(sys.stdout.encoding).strip()  # Example: geckodriver 0.32.0 (4563dd583110 2022-10-13 09:22 +0000).....
            commandResult = commandResult.split('\n', 1)[0]  # Example: geckodriver 0.32.0 (4563dd583110 2022-10-13 09:22 +0000)
            geckoVersion = commandResult.split()[1]  # Example: 0.32.0
            # Check if major version is over 0
            if int(geckoVersion.split('.')[0]) > 0:
                pass
            elif int(geckoVersion.split('.')[1]) < MIN_VER['geckodriver.minor']:
                proceed = False
                print("ERROR_BROWSER_VERSION: Geckodriver {}\nPlease refer: {}".format(geckoVersion, HELP_GECKODRIVER))
        except Exception as e:
            proceed = False
            print("ERROR_MALFORMED_BROWSER: Unable to read the Geckodriver version\nPlease refer: {}".format(HELP_GECKODRIVER))

    else:
        proceed = False
        print("ERROR_MISSING_BROWSER: Geckodriver\nPlease refer: {}".format(HELP_GECKODRIVER))

    return proceed


def check_required_packages():
    """ Ensure the required python packages are available """

    proceed = True
    missingPackageList = []
    conflictPackageList = []

    with open(config.path.requirements) as file:
        while (requirement := file.readline().strip()):
            package = requirement.split('==')
            # Check if package exist
            if (spec := importlib.util.find_spec(package[0])) is not None:
                # Check package version
                if importlib.metadata.version(spec.name) != package[1]:
                    conflictPackageList.append(package[0])
            else:
                missingPackageList.append(package[0])

    if len(missingPackageList) > 0:
        print("ERROR_MISSING_PACKAGE: {}".format(', '.join(missingPackageList)))
        proceed = False
    if len(conflictPackageList) > 0:
        print("ERROR_CONFLICTED_PACKAGE_VERSION: {}".format(', '.join(conflictPackageList)))
        proceed = False

    if proceed == False:
        print("To fix the error(s) please execute: pip install -r requirements.txt")

    return proceed


def test_dumpcap():
    """ Ensure dumpcap is working with correct interface and permission """

    try:
        pcapFilePath = os.path.join(CRAWLER_OUTPUT_PATH, 'testDumpcap.pcapng')

        # Start ping process
        pingOutput = subprocess.Popen('ping -c {} {}'.format(DUMPCAP_TESTING_SECONDS, DUMPCAP_PING_ADDRESS),
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        dumpcapCommand = 'dumpcap -a duration:{} -a filesize:{} -i {} -w "{}"'.format(
            DUMPCAP_TESTING_SECONDS, 1024 * 100, config.pcap.networkInterface, pcapFilePath)
        print("[DUMPCAP_TEST_COMMAND]", dumpcapCommand, "\n")

        # Start dumpcap
        dumpcapOutput = os.system(dumpcapCommand)

        # Check dumpcap for error
        if os.waitstatus_to_exitcode(dumpcapOutput) > 0:
            print('ERROR_DUMPCAP_TEST: Dumpcap unable to capture network packet.')
            return False
        else:
            pingError = pingOutput.stderr.read().decode('utf-8')
            # Check if packet exist and has content
            if os.path.isfile(pcapFilePath) and os.stat(pcapFilePath).st_size > 1:
                # Ensure captured packet contain ICMP:DUMPCAP_PING_ADDRESS payload
                with PcapReader(pcapFilePath) as pcapReader:
                    for packet in pcapReader:
                        if 'ICMP' in packet:
                            if packet.payload.dst == DUMPCAP_PING_ADDRESS or packet.payload.src == DUMPCAP_PING_ADDRESS:
                                return True

                # No ping-related packet captured
                print("FAILED_DUMPCAP_TEST: Missing ICMP packet to {}. This most probably due to the incorrect network interface.".format(
                    DUMPCAP_PING_ADDRESS))
                return False
            elif len(pingError) > 0:  # Check if packet exist due to ping error
                print("FAILED_DUMPCAP_TEST: Unable to ping while capturing network packet")
                return False

    except Exception as error:
        print("[FAILED_DUMPCAP_TEST]:", error)
        return False


def test_cloud_upload():
    """ Ensure the cloud upload feature sing clone is functional """

    # Check if Rclone is installed
    try:
        aptCache = apt.Cache()
        aptCache['rclone']
    except KeyError:
        print("ERROR_MISSING_APPLICATION: Rclone\nPlease install it using: apt install rclone")
        return False

    # Try running rclone
    try:
        command = 'rclone copy -L -P "{}" "{}"'.format(CLOUD_UPLOAD_TEST_FILE, config.cloud.uploadPath)
        print("[RCLONE_TEST_COMMAND]", command, "\n")
        exitCode = os.system(command)

        if os.waitstatus_to_exitcode(exitCode) > 0:
            print("ERROR_CLOUD_UPLOAD: Rclone failed to upload the test file.")
            return False
        else:
            return True
    except Exception as error:
        print("ERROR_CLOUD_UPLOAD:", error)
        return False


def test_telegram_notification():
    """ Ensure the Telegram Bot notification feature is functional """

    try:
        message = "{} | {} | {} | Telegram Notification Test".format(
            config.main.hostname, TEST_LABEL, get_timestamp())
        call_telegram_bot_api(message, True)
        return True
    except Exception as error:
        print("ERROR_TELEGRAM_NOTIFICATION:", error)
        return False


def test_database_creation():
    """ Test the visit database creation using custom csv source file """

    try:
        command = 'python3 "{}" -sp "{}" -vd "{}" -t 1'.format(DATABASE_CREATOR_PATH,
                                                               VISIT_DATABASE_SOURCE_PATH, VISIT_DATABASE_PATH)
        print("[DATABASE_CREATION_TEST_COMMAND]", command, "\n")

        exitCode = os.system(command)

        if os.waitstatus_to_exitcode(exitCode) > 0:
            print("ERROR_VISIT_DATABASE_CREATION: create.py failed to create a new visit database.")
            return False
        else:
            return True
    except Exception as error:
        print("ERROR_VISIT_DATABASE_CREATION:", error)
        return False


def test_crawler_activity():
    """ Test the main crawler activity """

    try:
        # command = ['python3', os.path.join(CRAWLER_PATH, 'run.py'), '-l', TEST_LABEL, '-vd',
        #            VISIT_DATABASE_PATH, '-op', CRAWLER_OUTPUT_PATH, '-up', config.cloud.uploadPath, '-t']

        command = 'python3 "{}" -l {} -vd "{}" -op "{}" -up "{}" -t'.format(os.path.join(
            CRAWLER_PATH, 'run.py'), TEST_LABEL, VISIT_DATABASE_PATH, CRAWLER_OUTPUT_PATH, config.cloud.uploadPath)
        print("[CRAWLING_TEST_COMMAND]", command, "\n")

        exitCode = os.system(command)
        # Execute the crawling command
        # crawlerOutput = subprocess.Popen(command)
        # output = crawlerOutput.communicate()

        # Check crawler exit code
        if os.waitstatus_to_exitcode(exitCode) > 0:
            print("ERROR_CRAWLER_TEST: Crawler failed to complete.")
            return False

        # Check the collected .act.json
        if os.path.isfile(CRAWLER_OUTPUT_CHECK_FILE_PATH):
            try:
                fileObject = open(CRAWLER_OUTPUT_CHECK_FILE_PATH, "r")
                activityDict = json.load(fileObject)
                fileObject.close()

                if 'failed' in activityDict:
                    print("ERROR_CRAWLER_TEST: {} -> Visit test is unsuccessful".format(activityDict['failed']))
                    return False
                else:
                    return True
            except Exception as error:
                print("ERROR_CRAWLER_TEST: Unable to read {}.act.json file at: {}".format(
                    TEST_CRAWLER_FILENAME_PREFIX, CRAWLER_OUTPUT_CHECK_FILE_PATH))
                return False
        else:
            print("ERROR_CRAWLER_TEST: Unable to find {}.act.json file at: {}".format(
                TEST_CRAWLER_FILENAME_PREFIX, CRAWLER_OUTPUT_CHECK_FILE_PATH))
            return False

    except Exception as error:
        print("ERROR_CRAWLER_TEST:", error)
        return False


def run_full_testing():
    """ Manage the WFP-Collector tool testing """

    # -> Remove existing test-output folder
    if os.path.isdir(CRAWLER_OUTPUT_PATH):
        shutil.rmtree(CRAWLER_OUTPUT_PATH)
    elif os.path.isfile(CRAWLER_OUTPUT_PATH):
        os.remove(CRAWLER_OUTPUT_PATH)

    # -> Create new test-output folder
    os.makedirs(CRAWLER_OUTPUT_PATH)

    # -> Start the whole test
    print('[LABEL]: ' + TEST_LABEL)
    print("\n[1]-> Checking required application packages...")
    if check_required_system_applications() == True:
        print("\n[2]-> Checking configuration file...")
        global SETUP_CONFIG
        SETUP_CONFIG = parse_config_file('setup')
        if SETUP_CONFIG != False:
            print("\n[3]-> Checking required browser...")
            if check_required_tbb_and_gecko() == True:
                print("\n[4]-> Checking required python packages...")
                if check_required_packages() == True:
                    print("\n[5]-> Testing network packet capturing...")
                    if test_dumpcap() == True:
                        if config.cloud.enable == True:
                            # Add test folder to the upload path
                            config.cloud.uploadPath = os.path.join(config.cloud.uploadPath, TEST_LABEL)
                            print("\n[6]-> Testing cloud upload...")
                            if test_cloud_upload() == False:
                                exit(1)  # Self exit
                        else:
                            print("\n[6]-> Cloud upload is disabled, testing skipped.")

                        if config.notification.enable == True:
                            print("\n[7]-> Testing telegram notification...")
                            if test_telegram_notification() == False:
                                exit(1)  # Self exit
                        else:
                            print("\n[7]-> Telegram notification is disabled, testing skipped.")
                        print("\n[8]-> Testing visit database creation...")
                        if test_database_creation() == True:
                            print("\n[9]-> Testing crawling activity...")
                            if test_crawler_activity() == True:
                                print("[#]-> All test are completed successfully.")
                                exit(0)

    # -> Exit with non-zero
    exit(1)


if __name__ == '__main__':
    run_full_testing()
