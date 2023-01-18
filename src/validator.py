from scapy.all import PcapReader, wrpcap
from shutil import copyfile

from configurations import *


############################################################
# Collected data validator
############################################################

# Check for webpage size
def check_webpage_size(webpageFilePath):
    
    # Webpage should be bigger than 100 bytes
    if os.stat(webpageFilePath).st_size < 100:
        return errorCause.HTML_SIZE_ERROR
    
    return True


# Check for captcha blocked
def check_captcha_blocked(webpageContent, visitData):
    # Return True if no captcha/blocked detected
    # Return String (reason of captcha/blocked)


    # Check page title for known captcha/blocked
    if "Attention Required! | Cloudflare" in visitData['pageTitle']:
        return captblock.CAPT_CLOUDFLARE
    elif "Captcha Challenge" in visitData['pageTitle']:
        return captblock.CAPT_HCAPTCHA
    elif "Captcha" in visitData['pageTitle']:
        return captblock.CAPT_IMUNIFY
    elif "Verify your identity" in visitData['pageTitle']: # From 105:Walmart.com
        return captblock.CAPT_SPECIFIC
    #elif visitData['url'].replace('https://', '').replace('www.', '') in visitData['pageTitle'].lower(): # Google & Amazon - The title has the domain name
    elif visitData['url'] in visitData['pageTitle'].lower(): # Google & Amazon - The title has the URL value
        return captblock.CAPT_SPECIFIC 

    return True


# Check for webpage that block Tor
def check_tor_blocked(webpageContent, visitData):

    if "access denied" in visitData['pageTitle'].lower(): # 248:cnbc.com
        return errorCause.BLOCKED_TOR
    elif "blocked" in visitData['pageTitle'].lower(): # 
        return errorCause.BLOCKED_TOR
    elif "not found" in visitData['pageTitle'].lower(): # 
        return errorCause.BLOCKED_TOR
    elif "forbidden" in visitData['pageTitle'].lower(): # 
        return errorCause.BLOCKED_TOR
    elif "error" in visitData['pageTitle'].lower(): # 
        return errorCause.BLOCKED_TOR

        
    # Return True if no block
    return True


# Main handler for validate collected webpage data
# Return True if no problem occcur, else return errorCause
def validate_webpage(webpageFilePath, visitData):

    # Read webpage content
    try:
        if os.stat(webpageFilePath).st_size == 0:
            return errorCause.HTML_EMPTY

        # -> Read file
        webpageFile = open(webpageFilePath, 'r')
        webpageContent = webpageFile.read()
        webpageFile.close()

        # Check for webpage size
        if config.data.CHECK_WEBPAGE_SIZE == True:
            checkStatus = check_webpage_size(webpageFilePath)
            if checkStatus != True:
                return checkStatus

        # Check for captcha blocking content
        if config.data.CHECK_WEBPAGE_CAPTCHA == True:
            checkStatus = check_captcha_blocked(webpageContent, visitData)
            if checkStatus != True:
                return checkStatus

        # Check for Tor-blocked content
        if config.data.CHECK_WEBPAGE_BLOCKED == True:
            checkStatus = check_tor_blocked(webpageContent, visitData)
            if checkStatus != True:
                return checkStatus

        # Validation is pass
        return True
        
    except:
        return errorCause.HTML_UNREADABLE

  

def filter_pcap_file(pcapFilePath, visitData, guardList):
    if os.path.isfile(pcapFilePath):
        visitData['pcapRawSize'] = os.path.getsize(pcapFilePath)

        # Save raw pcap
        if config.pcap.KEEP_RAW == True:
            pcapRaw = os.path.splitext(pcapFilePath)[0]+'.raw.pcapng'
            copyfile(pcapFilePath, pcapRaw)
        
        # Read and filter pcap
        pcapFiltered = []
        with PcapReader(pcapFilePath) as preader:
            for p in preader:
                if 'TCP' in p:
                    ip = p.payload
                    if ip.dst in guardList or ip.src in guardList:
                        # Remove TCP payload
                        if config.pcap.REMOVE_TCP_PAYLOAD == True:
                            tcp = ip.payload
                            tcp.remove_payload()

                        pcapFiltered.append(p)
        wrpcap(pcapFilePath, pcapFiltered)

        visitData['pcapSize'] = os.path.getsize(pcapFilePath)
    else:
        raise Exception(errorCause.DUMPCAP_MISSING_FILE)
