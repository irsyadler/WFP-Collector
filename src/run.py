import argparse
from crawler import *

# Initialize all neceessary configuration
def init_config(parseArgument = False):

    # -- Step 1 -> Set required configuration -- #
    config.main.LABEL = "Batch-1" # Browsing simulation label.
    config.main.DATABASE = "websiteVisitList.json" # Filename for generated website visit list
    config.directory.DATABASE_FILE = os.path.join(config.directory.PROJECT, 'database', config.main.DATABASE)
    config.directory.DATA = os.path.join(config.directory.PROJECT, 'data', config.main.LABEL)
    # -- -------------------------------- -- #

    # -- Step 2 -> Check arguments -- #
    if parseArgument:
        parser = argparse.ArgumentParser(description='Execute browsing activity crawling.')
        parser.add_argument('-f', '--fail', action='store_true', help='Repeat failed visit')
        parser.add_argument('-r', '--round', default=config.crawling.MAX_VISIT_RUN, type=int, help='The maximum number of round for the failed-visit to be rerun')
        args = parser.parse_args()

        if args.fail == True:
            config.crawling.VISIT_STATUS = visitStatus.FAILED
        config.crawling.MAX_VISIT_RUN = args.round

    # -- Step 3 -> Override any other configuration (configurations.py) -- #

    # Uncomment to change network interface for packet capturing
    # config.pcap.NET_INTEFACE = 'eth0'

    # Uncomment to change Tor Browser directory name
    # config.directory.TBB = os.path.join(config.directory.APP, "tor-browser_en-US")

    # Uncomment to enable HTTP Archive Export
    # config.data.HAR = True

    # Uncomment to set cloud upload path
    # config.data.CLOUD_UPLOAD_PATH = os.path.join('mycloudstorage:/WFT', config.main.LABEL)
    # Uncomment to enable cloud upload
    # config.data.ENABLE_CLOUD_UPLOAD = True
    # Uncomment to only trigger cloud upload after X number of completed website visits
    # config.data.CLOUD_UPLOAD_VISIT_BATCH = 5

    # Uncomment to set the Telegram Bot token
    # config.notification.TOKEN = "0000000000:XXX....."
    # Uncomment to set the Telegram Bot Chat ID
    # config.notification.CHAT_ID = "-000000000"
    # Uncomment to enable completion notification
    # config.notification.ENABLE = True

    # Uncomment to disabled headless mode
    # config.crawling.ENABLE_VIRTUAL_DISPLAY = False

    # Uncomment to remove crawling activity log for successful visit
    # config.data.REMOVE_CA_LOG = removeLog.SUCCEED
    # Uncomment to remove Stem log for successful visit
    # config.data.REMOVE_STEM_LOG = removeLog.SUCCEED
    # Uncomment to remove Tor Browser log for successful visit
    # config.data.REMOVE_TBD_LOG = removeLog.SUCCEED


    # -- ------------------------------------- --#


# Execute preliminary checking before execute crawling activity
def preliminary_check():

    # Check if MAX_VISIT_RUN out of range
    if config.crawling.MAX_VISIT_RUN > 100 or config.crawling.MAX_VISIT_RUN < 0:
        print("[ROUND_OUT_OF_RANGE] -> Please set the number of round between 1 and 100.")
        return False

    # Check if crawler database is exist
    if not os.path.exists(config.directory.DATABASE_FILE):
        print("[MISSING_DATABASE_FILE]")
        return False

    # Check for data folder
    if not os.path.exists(config.directory.DATA):
        if config.data.CREATE_CRAWLING_FOLDER == True:
            print("Creating crawling activity folder...")
            try:
                os.mkdir(config.directory.DATA)
            except:
                print("[FAILED_CREATING_CRAWLING_FOLDER]")
                return False
        else:
            print("[MISSING_CRAWLING_FOLDER]")
            return False

    # Check other required folder / file
    if not os.path.exists(config.directory.TBB):
        print("[MISSING_TOR_BROWSER]")
        return False

    if not os.path.exists(config.directory.GECKO):
        print("[MISSING_GECKO_DRIVER]")
        return False

    # Check for network interface operstate
    if os.popen("cat /sys/class/net/{}/operstate".format(config.pcap.NET_INTEFACE)).read().strip() != 'up':
        print("[UNACTIVE_NETWORK_INTERFACE]")
        return False
   
    # Check Telegram Bot token if valid
    if config.notification.ENABLE == True:
        try:
            url = "https://api.telegram.org/bot{}/getMe".format(config.notification.TOKEN)
            contents = urllib.request.urlopen(url).read()
        except Exception as e:
            print("[INVALID_TELEGRAM_BOT_TOKEN]")
            return False

    # Checking succeed
    return True



def start_crawling():

    # Initiate configuration
    init_config(True)

    print("Checking data...")

    # Proceed if checking is success
    if preliminary_check() == True:

        print("Cleaning process...")
        kill_alive_process(True, __file__)

        print("Starting crawling...")
        manage_crawling_activity()



if __name__ == '__main__':
    start_crawling()
   
