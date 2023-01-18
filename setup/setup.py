############################################################
# WFP-Collector Setup [Tor Browser and Geckodriver]
############################################################

import os
import pathlib
import sys
import time
import tarfile
import math
import requests

# Relative path to the app and crawler directories
APP_PATH = str((pathlib.Path(__file__).parent / '../app/').resolve())
CRAWLER_PATH = str((pathlib.Path(__file__).parent / '../crawler').resolve())

# Import relative modules
sys.path.append(CRAWLER_PATH)
from run import *

# Path related to setup process
SETUP_CONFIG = {}
EXTENSION_PREFERENCES_SOURCE_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), 'extension-preferences.json')


def convert_size(size_bytes: int):
    """" Convert int to proper bytes representation """

    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    integer = int(math.floor(math.log(size_bytes, 1024)))
    power = math.pow(1024, integer)
    rounded = round(size_bytes / power, 2)
    return "%s %s" % (rounded, size_name[integer])


def downloadFile(url: str, filePath: str):
    """ Handle the file downloading process from the internet """

    try:
        startTime = time.time()
        requestObject = requests.get(url, stream=True)

        # Get the response data
        totalSize = int(requestObject.headers.get('content-length'))

        # Start write stream to file
        fileObject = open(filePath, 'wb')
        if totalSize is None:  # no content length header
            fileObject.write(requestObject.content)
        else:
            downloaded = 0
            for chunk in requestObject.iter_content(chunk_size=8192):
                downloaded += len(chunk)
                fileObject.write(chunk)

                # Show download progress
                progress = int(50 * downloaded / totalSize)
                sys.stdout.write("\r[%s%s] %s/s    " % ('=' * progress, ' ' * (50 - progress),
                                 convert_size(downloaded // (time.time() - startTime))))

        print("")  # Push terminal to new line
        return True
    except Exception as error:
        print("SETUP_ERROR: Failed to download -> {}\n{}".format(url, error))
        return False


def download_and_configure_app():
    """ Perform Tor Browser and Geckodriver download and configuration """

    # Parse config
    print("[11] Reading setup config...")
    global SETUP_CONFIG
    SETUP_CONFIG = parse_config_file('setup')
    if SETUP_CONFIG == False:
        return False

    try:
        proceedDownload = True

        # Check for existing Tor Browser
        print("[--] Checking Tor Browser path...")
        if os.path.isdir(config.path.browser):
            if SETUP_CONFIG['overwriteExistingApp'] == False:
                # Tor Browser exist and overwrite is disabled
                print("[--] Tor Browser directory exist, download skipped.")
                proceedDownload = False
            else:
                shutil.rmtree(config.path.browser)
        elif os.path.isfile(config.path.browser):
            # Tor Browser path should be a directory
            if SETUP_CONFIG['overwriteExistingApp'] == False:
                print("Error at:".format(config.path.browser))
                print("SETUP_ERROR: Tor Browser exist, but it is a file and 'overwriteExistingApp' is disabled.")
                return False
            else:
                os.remove(config.path.browser)

        # Download Tor Browser
        if proceedDownload == True:
            print("[--] Downloading the Tor Browser...")
            localFilePath = os.path.join(config.path.app, SETUP_CONFIG['torBrowserDownloadURL'].split('/')[-1])
            if downloadFile(SETUP_CONFIG['torBrowserDownloadURL'], localFilePath) == True:
                # Extract the Tor Browser
                print("[--] Extracting the Tor Browser....")
                archive = tarfile.open(localFilePath)
                archive.extractall(config.path.app)
                archive.close()

                # Configure HAR permission
                if SETUP_CONFIG['configureHARExportTrigger'] == True:
                    print("[--] Downloading the Firefox HAR Export Trigger...")
                    # Set the location for Tor Browser's addons .xpi file
                    firefoxAddonPath = os.path.join(config.path.browser, SETUP_CONFIG['harExportTriggerExtensionPath'])
                    if downloadFile(SETUP_CONFIG['harExportTriggerDownloadURL'], firefoxAddonPath) == True:
                        # Set the location for Tor Browser's extension preferences file
                        print("[--] Copying the Tor Browser's extension preferences....")
                        shutil.copyfile(EXTENSION_PREFERENCES_SOURCE_PATH, os.path.join(
                            config.path.browser, SETUP_CONFIG['torBrowserExtensionPreferencesPath']))

                    else:
                        return False

                # Remove downloaded archive
                if SETUP_CONFIG['removeDownloadedArchive'] == True:
                    os.remove(localFilePath)
            else:
                return False

        proceedDownload = True

        # Check for Geckodriver
        print("[--] Checking Geckodriver path...")
        if os.path.isfile(config.path.gecko):
            if SETUP_CONFIG['overwriteExistingApp'] == False:
                # Geckodriver exist and overwrite is disabled
                print("[--] Geckodriver file exist, download skipped.")
                proceedDownload = False
            else:
                os.remove(config.path.gecko)
        elif os.path.isdir(config.path.gecko):
            # Geckodriver path should be a file
            if SETUP_CONFIG['overwriteExistingApp'] == False:
                print("Error at:".format(config.path.gecko))
                print("SETUP_ERROR: Geckodriver exist, but it is a directory and 'overwriteExistingApp' is disabled.")
                return False
            else:
                shutil.rmtree(config.path.gecko)

        # Download Geckodriver
        if proceedDownload == True:
            print("[--] Downloading the Geckodriver...")
            localFilePath = os.path.join(config.path.app, SETUP_CONFIG['geckodriverDownloadURL'].split('/')[-1])
            if downloadFile(SETUP_CONFIG['geckodriverDownloadURL'], localFilePath) == True:
                # Extract the Geckodriver
                print("[--] Extracting the Geckodriver....")
                archive = tarfile.open(localFilePath)
                archive.extractall(config.path.app)
                archive.close()

                # Remove downloaded archive
                if SETUP_CONFIG['removeDownloadedArchive'] == True:
                    os.remove(localFilePath)
            else:
                return False

        return True
    except Exception as error:
        print("SETUP_ERROR: Failed to setup the Tor Browser and Geckodriver.\n{}".format(error))
        return False


if __name__ == '__main__':
    if download_and_configure_app() == True:
        exit(0)

    # -> Exit with non-zero
    exit(1)
