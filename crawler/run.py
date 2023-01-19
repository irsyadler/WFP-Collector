############################################################
# Check Crawling Configurations And Start Crawler
############################################################

import argparse

# Import project module
from crawler import *


def init_config(checkArguments=False):
    """ Initialize all necessary configuration """

    # -- Step 1 -> Set default configuration -- #
    # Default crawling activity label
    config.main.label = 'Batch_A'
    # Default visit database filename
    config.main.visitDatabaseFilename = 'visit_database.json'

    # -- Step 2 -> Parse configuration file (config.json) -- #
    if parse_config_file() == False:
        return False

    # -- Step 3 -> Parse command arguments -- #
    if checkArguments:
        # Define arguments parser
        parser = argparse.ArgumentParser(description='Execute crawling activity.', add_help=False)
        parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
        parser.add_argument('-l', '--label', default=config.main.label, help='Crawling activity label')
        parser.add_argument('-d', '--display', action='store_true', help='Execute crawling activity in the physical display')
        parser.add_argument('-rf', '--repeatFail', action='store_true', help='Repeat failed visit')
        parser.add_argument('-mr', '--maxRepeat', default=config.crawler.maxVisitRepeat, type=int,
                            help='The maximum number of repetitions for the FAILED visit to be revisited')
        parser.add_argument('-vd', '--visitDatabase', default=config.path.database,
                            help='File path to the visit database for crawling activity (JSON file)')
        parser.add_argument('-op', '--outputPath', default=config.path.output,
                            help='Directory path to store collected browsing data')
        parser.add_argument('-up', '--uploadPath', default=config.cloud.uploadPath,
                            help='Directory path to upload the collected data')
        parser.add_argument('-t', '--test', action='store_true', default=config.main.test,
                            help='Execute crawling activity in a testing environment')
        args = parser.parse_args()

        # Set arguments config
        if args.repeatFail == True:
            config.crawler.visitStatus = const.visitStatus.FAILED
        if args.display == True:
            config.crawler.useVirtualDisplay = False
        config.main.label = args.label
        config.crawler.maxVisitRepeat = args.maxRepeat
        config.path.database = args.visitDatabase
        config.path.output = args.outputPath
        config.cloud.uploadPath = args.uploadPath
        if args.test == True:
            config.main.test = True

    # -- Step 4 -> Set runtime-related configuration -- #
    if len(config.path.database) == 0:
        config.path.database = os.path.join(config.path.project, 'database', config.main.visitDatabaseFilename)
    if len(config.path.output) == 0:
        config.path.output = os.path.join(config.path.project, 'output', config.main.label)
    if config.cloud.concatenateUploadPath == True and config.main.test == False:
        config.cloud.uploadPath = os.path.join(config.cloud.uploadPath, config.main.hostname, config.main.label)

    return True


def preliminary_check():
    """ Execute preliminary checking before execute crawling activity """

    # Ensure label has no whitespace character
    for character in config.main.label:
        if character.isspace() == True:
            print("[ERROR_LABEL_CHAR] -> Label string (main.config.label) cannot contain whitespace.")
            return False

    # Check if MAX_VISIT_RUN out of range
    if config.crawler.maxVisitRepeat > 100 or config.crawler.maxVisitRepeat < 0:
        print("[ROUND_OUT_OF_RANGE] -> Please set the number of round between 1 and 100.")
        return False

    # Check if visit database is exist
    if not os.path.exists(config.path.database):
        print("[MISSING_VISIT_DATABASE_FILE]")
        return False

    # Check for data folder
    if not os.path.exists(config.path.output):
        if config.data.createDataFolder == True:
            print("Creating crawling collected data folder...")
            try:
                os.mkdir(config.path.output)
            except:
                print("[FAILED_CREATING_CRAWLING_DATA_FOLDER]")
                return False
        else:
            print("[MISSING_CRAWLING_FOLDER]")
            return False

    # Check for network interface operstate
    if os.popen("cat /sys/class/net/{}/operstate".format(config.pcap.networkInterface)).read().strip() != 'up':
        print("[INACTIVE_NETWORK_INTERFACE]")
        return False

    # Check Telegram Bot token if valid
    if config.notification.enable == True:
        if test_telegram_token() == False:
            print("[INVALID_TELEGRAM_BOT_TOKEN]")
            return False

    # Checking succeed
    return True


def start_crawling():
    """ Initiate pre-crawling task """

    # Initiate configuration
    print("Checking config...")
    if init_config(True) == True:

        print("Checking data...")
        if preliminary_check() == True:

            print("Cleaning process...")
            kill_alive_process(True, __file__)

            print("Starting crawling...")
            manage_crawling_activity()


if __name__ == '__main__':
    start_crawling()
