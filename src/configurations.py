import os, pathlib, socket

from definitions import *

############################################################
# Common Config Declaration 
############################################################
class config:
    # Directory Configuration
    class directory:
        PROJECT = str(pathlib.Path(__file__).parent.parent.absolute())
        APP = os.path.join(PROJECT, "app")
        TBB = os.path.join(APP, "tor-browser_en-US")  # TBB Directory # !IMPORTANT: Should not have space
        GECKO = os.path.join(APP, "geckodriver")  # Mozilla Geckodriver Directory
        DATABASE_FILE = '' # Database JSON file path
        DATA = ''  # Directory to save browsing data and information
        MAIN_LOG_FILENAME = '0.main.log' # The log filename for management of crawling activity
        MAIN_STATUS_JSON = '0.status.json' # The status filename (json) for management of crawling activity

    # Timing Configuration
    class wait:
        RESIZE_WINDOW = 1 # To ensure browsing window sized correctly
        AFTER_GET = 5 # To ensure webpage load completely # Value based on Juarez (2014).
        EXECUTER_INITIAL = 120 # Wait for get.driver completed. # STEM timeout is 90, then wait for browser to start etc
        EXECUTER_FINAL = 60 * 5 # Wait for webpage completely load # Selenium will timeout after 300000ms
        NEXT_VISIT = 5 # Wait between visit instance # Value based on Juarez (2014).

    # Bot Configuration
    class notification:
        ENABLE = False # Enable completion notification using Telegram Bot
        CHAT_ID = "" # Telegram Bot Chat ID
        TOKEN = "" # Telegram Bot token
        
    # Browsing configuration (for drivers)
    class crawling:
        MOBILE_UA = "Mozilla/5.0 (Android 10; Mobile; rv:102.0) Gecko/102.0 Firefox/102.0" # Mobile UserAgent
        SCREEN_SIZE_DESKTOP = (1920, 1080) # Width x Height
        SCREEN_SIZE_MOBILE = (480, 854) # Width x Height
        SCREEN_SIZE_TABLET = (1200, 1600) # Width x Height
        MAX_VISIT_RUN = 2 # How many times visit should be repeat. Less than 0 will make PENDING being skipped. This round count override PENDING status
        VISIT_STATUS = visitStatus.PENDING # Which visitStatus to execute from database
        SET_EXIT_NODE = False # Modify torrc to include exit node selection
        EXIT_NODE_VALUE = ('country', '{sg}') # Parameter to set exit node. !IMPORTANT: Must be set when SET_EXIT_NODE is enable
        ENABLE_VIRTUAL_DISPLAY = True
        ENABLE_WRITE_INFORMATION = True # Write crawling activity information file
    
    # Configuration on browsing information extraction
    class data:
        CREATE_CRAWLING_FOLDER = True # Automatically create crawling activity folder if not exist
        HTML = True
        HAR = False # Will open Developer Tools window (seperate window) & extract HAR file
        SCREENSHOT = True
        JSON_INDENTION = 2 # Default is 2. None for most compact representation and decrease file size
        REMOVE_CA_LOG = removeLog.NO
        REMOVE_STEM_LOG = removeLog.NO
        REMOVE_TBD_LOG = removeLog.NO
        ENABLE_CLOUD_UPLOAD = False # Enable data upload to the cloud
        CLOUD_UPLOAD_PATH = '' # String for cloud upload path. Please inclue the rclone's remote cloud storage name
        CLOUD_UPLOAD_VISIT_BATCH = 1 # Define how many completed webpage visits before data upload to cloud will be triggered
        CLOUD_UPLOAD_DELETE_AFTER = False # Delete local data file after uploaded to cloud
        ENABLE_DATABASE_UPLOAD = True # Enable database file to be copied to data folder and uploaded to cloud
        CHECK_WEBPAGE = True # Enable webpage check. Ensure HTML file is not empty
        CHECK_WEBPAGE_SIZE = True # Enable webpage size check
        CHECK_WEBPAGE_CAPTCHA = True # Check for CAPTCHA or similar robot-blocker
        CHECK_WEBPAGE_BLOCKED = True # Check for Tor-blocked webpage
    
    # Define pcap capture confifuration
    class pcap:
        ENABLE = True # Enable the pcap capture features
        NET_INTEFACE = 'eth0' # Define the network interface for packet capturing
        LOCALHOST_IP = "127.0.0.1"  # default localhost IP
        FILTER = 'tcp and not host %s and not tcp port 22 and not tcp port 20' % LOCALHOST_IP
        MAX_DUMP_SIZE = 40000 # Max dump file size for dumpcap to run
        MAX_DUMP_DURATION = 120 # Duration for dumpcap to run, Refer wait config
        START_TIMEOUT = 10.0 # in seconds, Time out to wait for dumpcap to start
        KEEP_RAW = False # Save the orignal pcap file
        REMOVE_TCP_PAYLOAD = True # Remove TCP payload/data
        KEEP_GUARD_LIST = False # Enable the pcap capture features. Does't not depend pcap.

    # Define activity configuration
    class main:
        LABEL = '' # Set output "data" folder name
        DATABASE = ''
        HOSTNAME = socket.gethostname()


