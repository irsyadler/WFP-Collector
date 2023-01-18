############################################################
# Common Constants Definition
############################################################

class visitStatus:
    """ Define the state of a webpage visit """
    PENDING = 'PENDING' # Webpage is pending for visit
    COMPLETED = 'COMPLETED' # Webpage visit is completed
    FAILED = 'FAILED' # Webpage visit failed


class share:
    """ Define all key variable for crawler's multi-threading dictionary """
    STATUS = 'STATUS'
    REASON = 'REASON' # Reason for failed status
    DATA = 'DATA'
    PATH = 'PATH'


class browserMode:
    """ Define browser's browsing mode """
    DESKTOP = 'DESKTOP'
    MOBILE = 'MOBILE'
    TABLET = 'TABLET'


class crawlingStatus:
    """ Crawling activity status """
    READY = 'READY' # Crawling activity is ready to be start
    STARTED = 'STARTED' # Crawling activity function called
    BROWSING = 'BROWSING' # Driver "Get" to target webpage called
    COMPLETED = 'COMPLETED' # Crawling activity successfully executed. MUST_BE_SAME_TO: visitStatus
    FAILED = 'FAILED' # Crawling activity failed. MUST_BE_SAME_TO: visitStatus


class screenshot:
    """ Define screenshot collection """
    FULL = 'FULL' # Save the full webpage screenshot (including non-visible section)
    VISIBLE = 'VISIBLE' # Save the visible webpage screenshot
    NO = 'NO' # Do not take webpage screenshot


class file:
    """ Define file handling after visit """
    SAVE = 'SAVE' # Always keep file
    SAVE_COMPRESS = 'SAVE_COMPRESS' # Always keep file
    REMOVE = 'REMOVE' # Always remove file
    REMOVE_SUCCEED = 'REMOVE_SUCCEED' # Remove file on successful visit
    COMPRESS_REMOVE_SUCCEED = 'COMPRESS_REMOVE_SUCCEED' # Remove file on successful visit or compress file on failed visit
    SKIP = 'SKIP' # (Only for HAR and PCAPNG files) Do not collect file
    

class errorCause:
    """ The error cause of a failed webpage visit """
    GET_TIMEOUT = '[GET_TIMEOUT]'
    STEM_TIMEOUT = '[STEM_TIMEOUT]'
    CLOUD_UPLOAD_FAILED = '[CLOUD_UPLOAD_FAILED]'
    NET_CONNFAIL = '[NET_CONNFAIL]'
    NET_RESET = '[NET_RESET]'
    NET_DNSNOTFOUND = '[NET_DNSNOTFOUND]'
    NET_NSSFAIL = '[NET_NSSFAIL]'
    NET_TIMEOUT = '[NET_TIMEOUT]'
    MARION_DECOFAIL = '[MARION_DECOFAIL]'
    DEVICE_NOSPACE = '[DEVICE_NOSPACE]'
    CHECK_LOG = '[CHECK_LOG]' # The error cause has unknown format, for more info please check log
    LOG_UNREADABLE  = '[LOG_UNREADABLE]' # Log file unable to be accessed or read
    LOG_EMPTY  = '[LOG_EMPTY]' # Log file has no content
    HTML_UNREADABLE  = '[HTML_UNREADABLE]' # HTML file unable to be accessed or read
    HTML_EMPTY  = '[HTML_EMPTY]' # HTML file has no content
    MIN_PACKET_COUNT  = '[MIN_PACKET_COUNT]' # Captured packets count lower than the minimum acceptable count
    MIN_FILE_SIZE  = '[MIN_FILE_SIZE]' # File size is lower than the minimum acceptable size
    MISSING_COLLECTED_FILE = '[MISSING_COLLECTED_FILE]' # Expected collected file is missing
    INVALID_JSON  = '[INVALID_JSON]' # Log file has invalid json content
    
    # Unstable status reason
    ALIVE_APP = '[ALIVE_APP]' # There is alive app
    ALIVE_APP_EXECUTER = '[ALIVE_APP_EXECUTER]' # There are alive app and executer
    ALIVE_EXECUTER = '[ALIVE_EXECUTER]' # There is alive executer

    # Error related to Dumpcap
    DUMPCAP_START_FAILED  = '[DUMPCAP_START_FAILED]'
    DUMPCAP_START_TIMEOUT  = '[DUMPCAP_START_TIMEOUT]'
    DUMPCAP_MISSING_FILE  = '[DUMPCAP_MISSING_FILE]'

    # Error related to Tor-blocked / Captcha
    BLOCKED_TOR  = '[BLOCKED_TOR]'
    BLOCKED_CAPTCHA  = '[BLOCKED_CAPTCHA]'
    

class captblock:
    """ Type of captcha or block """
    CAPT_CLOUDFLARE = "[CAPT_CLOUDFLARE]"
    CAPT_HCAPTCHA = "[CAPT_HCAPTCHA]"
    CAPT_IMUNIFY = "[CAPT_IMUNIFY]"
    CAPT_SPECIFIC = "[CAPT_SPECIFIC]" # Captcha specific to website such as amazon / google


class crawlingInfo:
    """ Data class for notification and remote management """
    label = None
    hostname = None
    visitDatabasePath = None
    outputPath = None
    uploadPath = None
    visitStatus = None
    visitAll = None
    visitAvailable = None
    visitCurrent = None
    isAllDone = False # False indicate the crawler activity stopped abruptly
    lastUpdate = None

