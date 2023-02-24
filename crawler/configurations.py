############################################################
# Common Configurations Declaration
############################################################

import os
import pathlib
import socket
import constants as const


class main:
    """ Main Crawling Activity Configurations """
    # Crawling activity name
    label: str = ''
    # Database filename (ending with ".json")
    visitDatabaseFilename: str = ''
    # Set the system hostname
    hostname: str = socket.gethostname()
    # Log filename for management of crawling activity
    logFilename: str = '__crawler__.log'
    # Status filename (JSON file) for management of crawling activity
    statusFilename: str = '__status__.json'
    # Run crawler execution in testing procedure
    test: bool = False


class path:
    """ Path Configurations """
    # [Directory Path] WFP-Collector project
    project: str = str(pathlib.Path(__file__).parent.parent.resolve())
    # [File Path] JSON configuration file
    configuration = os.path.join(project, 'config.json')
    # [File Path] Python package requirements file
    requirements: str = os.path.join(project, 'requirements.txt')
    # [Directory Path] 3rd-party binaries
    app: str = os.path.join(project, 'app')
    # [Directory Path] Tor Browser
    browser: str = os.path.join(app, 'tor-browser')
    # [Binary File Path] Mozilla Geckodriver
    gecko: str = os.path.join(app, 'geckodriver')
    # [JSON File Path] Visit database file (contains list of visit data)
    database: str = ''
    # [Directory Path] Store collected browsing data
    output: str = ''


class wait:
    """ Waiting Time Configurations """
    # [Value in second] To ensure browsing window sized correctly
    windowResize: int = 1
    # [Value in second] To ensure webpage load completely. Value based on Juarez et al. (2014)
    afterWebpageLoad: int = 5
    # [Value in second] Wait for get.driver completed. STEM timeout is 90, then wait for browser to start etc
    roundOne: int = 120
    # [Value in second] Wait for webpage completely load. Selenium will timeout after 300000ms
    roundTwo: int = 60 * 5
    # [Value in second] Wait between visit instance. Value based on Juarez et al. (2014)
    beforeNextVisit: int = 5


class crawler:
    """ Crawling Configurations """
    # Write crawling activity information file
    writeActivityInformation: bool = True
    # Run crawling activity in virtual display (headless browsing)
    useVirtualDisplay: bool = True
    # Mobile and Tablet User-Agent string
    mobileUserAgent: str = 'Mozilla/5.0 (Android 10; Mobile; rv:102.0) Gecko/102.0 Firefox/102.0'
    # [Value in pixel unit] Desktop screen size (Width, Height)
    screenSizeDesktop: tuple[int, int] = (1920, 1080) # Based on: https://gs.statcounter.com/screen-resolution-stats/desktop/worldwide#monthly-202301-202301-bar
    # [Value in pixel unit] Mobile screen size (Width, Height)
    screenSizeMobile: tuple[int, int] = (360, 800) # Based on: https://gs.statcounter.com/screen-resolution-stats/mobile/worldwide#monthly-202301-202301-bar
    # [Value in pixel unit] Tablet screen size (Width, Height)
    screenSizeTablet: tuple[int, int] = (768, 1024) # Based on: https://gs.statcounter.com/screen-resolution-stats/tablet/worldwide#monthly-202301-202301-bar
    # How many times visit should be repeat. Less than 0 will make PENDING being skipped. This round count override PENDING status
    maxVisitRepeat: int = 2
    # Which visitStatus to execute from database
    visitStatus: const.visitStatus = const.visitStatus.PENDING
    # Modify torrc to include exit node selection
    setExitNode: bool = False
    # Parameter to set exit node. !IMPORTANT: Must be set when SET_EXIT_NODE is enable
    exitNodeParam: tuple[str, ...] = ('country', '{us}')
    # Config for torrc from config.json
    torrc: dict = {}
    # Preference for Tor Browser from config.json
    browserPreferences: dict = {}


class data:
    """ Browsing Data Collection Configurations """
    # Automatically create crawling data folder if not exist
    createDataFolder: bool = True
    # Save webpage HTML file
    html: const.file = const.file.SAVE
    # Will open Developer Tools window (separate window) & collect HAR file
    har: const.file = const.file.SAVE
    # Take the screenshot of the webpage
    saveScreenshot: const.screenshot = const.screenshot.VISIBLE
    # Store the list of Tor Guard's IP Address
    saveGuardList: bool = True
    # Default is 2. None for most compact representation and decrease file size
    jsonIndentation: int = 2
    # Store webpage visit log (.visit.log)
    visitLog: const.file = const.file.SAVE
    # Store Tor Stem log (.stem.log)
    stemLog: const.file = const.file.SAVE
    # Log level for Tor Stem. Possible value: debug, info, notice, warn, and err. Refer: https://manpages.ubuntu.com/manpages/jammy/man1/tor.1.html
    stemLogLevel: str = 'notice'
    # Store Tor Browser Driver log (.tbd.log)
    tbdLog: const.file = const.file.SAVE
    # Log level for Tor Browser Driver. Possible value: 1 until 5. Refer: https://gitlab.torproject.org/tpo/applications/tor-browser/-/wikis/Hacking#enabling-debug-logs-in-extensions
    tbdLoglevel: int = 2
    # Generate SHA256 hash value on collected file
    fileChecksum: bool = True


class pcap:
    """ PCAP Capture Configurations """
    # Enable the pcap capture features
    data: const.file = const.file.SAVE
    # Define the network interface for packet capturing
    networkInterface: str = 'eth0'
    # [Value in byte] Max dump file size for Dumpcap to run
    maxDumpSize: int = 40000
    # [Value in second] Max duration for Dumpcap to run, refer config.wait
    maxDumpDuration: int = 120
    # [Value in second] Time to wait for Dumpcap to start
    startTimeout: float = 10.0
    # Filter the collected pcap file
    filter: bool = True
    # (If filter is enabled) Save the original pcap file
    saveRaw: bool = False
    # Remove TCP payload/data
    removePayload: bool = False
    # Default localhost IP
    localhostIP: str = '127.0.0.1'
    # PCAP filtering rule
    filteringRule: str = 'tcp and not host {} and not tcp port 22 and not tcp port 20'.format(localhostIP)


class validate:
    """ Data Validation Configurations """
    # Check for CAPTCHA or similar robot-blocker
    webpageCaptcha: bool = True
    # Check for Tor-blocked webpage
    webpageBlocked: bool = True
    # Minimum number of packets in the captured pcapng file
    minCapturePackets: int = 0
    # [Value in byte] Minimum file size for .html file.
    minSizeHTML: int = 0
    # [Value in byte] Minimum file size for .png file.
    minSizeImg: int = 0
    # [Value in byte] Minimum file size for .har file.
    minSizeHAR: int = 0
    # [Value in byte] Minimum file size for .pcapng file.
    minSizePcap: int = 0
    # [Value in byte] Minimum file size for .visit.log file.
    minSizeVisitLog: int = 0
    # [Value in byte] Minimum file size for .stem.log file.
    minSizeStemLog: int = 0
    # [Value in byte] Minimum file size for .tbd.log file.
    minSizeTBDLog: int = 0


class cloud:
    """ Cloud Upload Configurations """
    # Enable data upload to the cloud
    enable: bool = False
    # [Directory Path] Cloud upload path. Please include the Rclone's remote cloud storage name
    uploadPath: str = ''
    # Append config.main.hostname and config.main.label into the config.cloud.uploadPath
    concatenateUploadPath: bool = True
    # Define how many completed webpage visits before cloud upload will be triggered
    uploadBatch: int = 1
    # Delete local data file after uploaded to cloud
    deleteUploaded: bool = False
    # Enable database file to be copied to data folder and uploaded to cloud
    uploadDatabase: bool = True
    # Send notification on cloud upload failed
    notifyOnFailed: bool = True
    # Stop crawler visit when cloud upload failed
    stopCrawlingOnFailed: bool = True


class notification:
    """ Telegram Notification Configurations """
    # Enable Telegram notification using Telegram Bot API
    enable: bool = False
    # Telegram Bot Chat ID
    chatID: str = ""
    # Telegram Bot token
    token: str = ""
