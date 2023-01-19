############################################################
# Create Visit Database For Crawling Activity
############################################################

import collections
import argparse
import time
import os.path
import sys
import pathlib
import csv
import string
import urllib

# Import relative modules
sys.path.append(str((pathlib.Path(__file__).parent / '../crawler').resolve()))
from functions import *
from run import init_config

# Max number of rounds
MAX_NUMBER_OF_INSTANCE = 3000

# Filename for visit database source
SOURCE_FILENAME = 'ats_global_500.csv'

# Valid character for visit name
SAFE_CHARACTERS = string.ascii_letters + string.digits + " -_.[]();"


def safeFilename(text):
    """ Ensure visit name is safe to be use as a filename """

    # Iterate each character to ensure all are safe characters
    for char in text:
        if char not in SAFE_CHARACTERS:
            # Found unsafe character
            return False

    return True  # All characters are safe


def create_crawler_visit_database(sourcePath, visitDatabasePath, args):
    """ Create visit database for crawling activity """

    processTime = time.time()

    # Parse CSV file
    fileObject = open(sourcePath, "r")
    csvReader = csv.reader(fileObject, delimiter=',')
    csvList = [row for row in csvReader]
    fileObject.close()

    # Init database file
    database, query = get_database_query(visitDatabasePath)
    visitDatabase = []

    # Ensure top value is lower than available line in the csv file
    if args.top > len(csvList):
        print("ERROR: The top value ({}) is higher than available lines ({}) of the source csv file : {}".format(
            args.top, len(csvList), sourcePath))
        return False

    instanceCount = 0
    while instanceCount < args.instance:

        # Increment round counter
        instanceCount += 1
        lineCount = 0

        for item in csvList[0:args.top]:
            lineCount += 1

            # Check line content
            if len(item) < 2:
                print("ERROR_CSV_FILE: Line number {} is missing the webpage url.".format(lineCount))
                return False

            # String line content
            item[0] = item[0].strip()
            item[1] = item[1].strip()

            # Check empty content
            if len(item[0]) == 0:
                print("ERROR_CSV_FILE: Line number {} has an empty visit name.".format(lineCount))
                return False
            elif len(item[1]) == 0:
                print("ERROR_CSV_FILE: Line {} has an empty webpage url.".format(lineCount))
                return False

            # Ensure visit name contain safe character for filename
            if safeFilename(item[0]) == False:
                print("ERROR_CSV_FILE: Line number {} contain unsafe character(s) for the visit name.".format(lineCount))
                return False

            # Append leading 0 if the visit name is a number
            item[0] = str(item[0]).zfill(len(str(args.top))) if item[0].isdigit() else item[0]
            # Set proper URL with HTML quote
            if item[1].startswith(('http://', 'https://')) == False:
                item[1] = 'https://' + urllib.parse.quote(item[1])
            else:
                item[1] = urllib.parse.quote(item[1])
            # Append leading 0 to instance number
            instance = str(instanceCount).zfill(len(str(args.instance)))

            # Build visit data format
            visitData = {'status': const.visitStatus.PENDING, 'name': "{}_,_{}".format(
                item[0], instance), 'mode': None, 'url': item[1], 'records': []}

            # Iterate each mode and append to visitDatabase
            for mode in args.mode:
                if mode == 'desktop':
                    visitData['name'] = visitData['name'].replace(",", "d")
                    visitData['mode'] = const.browserMode.DESKTOP
                    visitDatabase.append(visitData.copy())
                elif mode == 'mobile':
                    visitData['name'] = visitData['name'].replace(",", "m")
                    visitData['mode'] = const.browserMode.MOBILE
                    visitDatabase.append(visitData.copy())
                elif mode == 'tablet':
                    visitData['name'] = visitData['name'].replace(",", "t")
                    visitData['mode'] = const.browserMode.TABLET
                    visitDatabase.append(visitData.copy())

    # Add items to database
    database.insert_multiple(visitDatabase)

    # Result
    print("Source file: {}".format(sourcePath))
    print("Total created visit data: {}".format(len(database)))
    print("Creation time: {} seconds".format(round(time.time() - processTime, 2)))
    print("{} URL(s) in {} mode was created for {} instance(s).".format(args.top, args.mode, args.instance))
    print("Visit database file: {}".format(args.visitDatabase))

    return True

def check_creation_config():
    """ Validate the config and command argument before create visit database """
    # Init all config
    init_config()

    # Check arguments
    parser = argparse.ArgumentParser(description='Create a visit database for crawling activity.', add_help=False)
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    parser.add_argument('-t', '--top', default=100, type=int, help='Set the number of URLs (from the top) to be included in the visit database')
    parser.add_argument('-m', '--mode', nargs='+', default=['desktop'],
                        choices=['desktop', 'mobile', 'tablet'], help='Set the browsing mode: desktop, mobile, or tablet')
    parser.add_argument('-i', '--instance', default=1, type=int, help='Set the number of instances for each URL')
    parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite existing visit database')
    parser.add_argument('-sp', '--sourcePath', help='Path to a CSV source file for visit database creation')
    parser.add_argument('-vd', '--visitDatabase', default=config.path.database,
                        help='Path to save the created visit database (JSON file)')
    args = parser.parse_args()

    sourcePath = args.sourcePath if args.sourcePath is not None else str(
        (pathlib.Path(__file__).parent / SOURCE_FILENAME).resolve())
    config.path.database = args.visitDatabase

    proceed = True
    # Check duplicate in mode's value
    duplicateMode = [mode for mode, count in collections.Counter(args.mode).items() if count > 1]
    if len(duplicateMode) > 0:
        print("ERROR: The following mode has duplicate entry: '{}'.".format("', '".join(duplicateMode)))
        proceed = False

    # Check if csv source file exist
    if os.path.isfile(sourcePath) != True:
        print("ERROR: Visit database source file not found: {}".format(sourcePath))
        proceed = False

    # Check if visit database file already exist
    if os.path.isfile(config.path.database):
        # Check if overwrite is not enable
        if not args.overwrite:
            print("ERROR: Visit database file '{}' already exist. Please use '-o' argument to overwrite existing database file.".format(config.path.database))
            proceed = False
        else:
            os.unlink(config.path.database)

    # Check if the number of round exceed the limit.
    if args.instance < 1 or args.instance > MAX_NUMBER_OF_INSTANCE:
        print("ERROR: The number of INSTANCE should be between 1 and {}.".format(MAX_NUMBER_OF_INSTANCE))
        proceed = False

    if proceed:
        return create_crawler_visit_database(sourcePath, config.path.database, args)
    else:
        return False

if __name__ == '__main__':
    if check_creation_config() == False:
        exit(1)
