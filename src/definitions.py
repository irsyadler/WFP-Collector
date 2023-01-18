############################################################
# Constant Definition Declaration
############################################################

# Define databased visitStatus
class visitStatus:
    PENDING = 'PENDING' # Visit pending for execution
    COMPLETED = 'COMPLETED' # Visit execution completed
    FAILED = 'FAILED' # Visit execution failed

# Define all key variable
class variable:
    STATUS = 'status'
    REASON = 'reason'
    PATH = 'xvfb'

# Browsing mode
class browserMode:
    DESKTOP = 'desktop'
    MOBILE = 'mobile'
    TABLET = 'tablet'

# Crawling activity status
class crawlingStatus:
    READY = 'READY' # Crawling activity is ready to be start
    STARTED = 'STARTED' # Crawling activity function called
    BROWSING = 'BROWSING' # Driver "Get" to target webpage had been called
    COMPLETED = 'COMPLETED' # Crawling activity  successfully executed. MUST_BE_SAME_TO: visitStatus
    FAILED = 'FAILED' # Crawling activity failed. MUST_BE_SAME_TO: visitStatus

# Define removing log condition
class removeLog:
    ALWAYS = 'ALWAYS' # Always remove log
    SUCCEED = 'SUCCEED' # Remove log only on successful visit
    NO = 'No' # Do not remove log

# Visit unstable & error cause
class errorCause:
    GET_DUMMY = '[GET_DUMMY]'
    GET_TIMEOUT = '[GET_TIMEOUT]'
    STEM_TIMEOUT = '[STEM_TIMEOUT]'
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
    HTML_SIZE_ERROR  = '[HTML_SIZE_ERROR]' # HTML file size is not meet the minimum requirement
    INVALID_JSON  = '[INVALID_JSON]' # Log file has invalid json content
    
    # Unstable status reason
    ALIVE_APP = '[ALIVE_APP]' # There is alive app
    ALIVE_APP_EXECUTER = '[ALIVE_APP_EXECUTER]' # There are alive app and executer
    ALIVE_EXECUTER = '[ALIVE_EXECUTER]' # There is alive executer

    # Error realted to Dumpcap
    DUMPCAP_START_TIMEOUT  = '[DUMPCAP_START_TIMEOUT]'
    DUMPCAP_MISSING_FILE  = '[DUMPCAP_MISSING_FILE]'

    # Error realted to Tor-bloced / Captcha
    BLOCKED_TOR  = '[BLOCKED_TOR]'
    BLOCKED_CAPTCHA  = '[BLOCKED_CAPTCHA]'
    

# Type of captcha or block
class captblock:
    CAPT_CLOUDFLARE = "[CAPT_CLOUDFLARE]"
    CAPT_HCAPTCHA = "[CAPT_HCAPTCHA]"
    CAPT_IMUNIFY = "[CAPT_IMUNIFY]"
    CAPT_SPECIFIC = "[CAPT_SPECIFIC]" # Captcha specific to website such as amazon / google


############################################################
# Data class definition
############################################################
# Handling data for botNotification and getCrawlingStatus
class crawlingInfo:
    hostname = None
    label = None
    visitStatus = None # visitStatus Target
    visitAll = None # All DB information
    visitAvailable = None
    visitCurrent = None
    isAllDone = False # False indicating activity stopped abruptly
    lastUpdate = None



