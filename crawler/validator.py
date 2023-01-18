############################################################
# Validate Collected Data From Crawling Activity
############################################################

import ntpath
import os
from scapy.all import PcapReader, wrpcap
from shutil import copyfile

# Import project module
import constants as const
import configurations as config
from functions import *


def check_captcha_webpage(webpageContent, visitData):
    """ Check for captcha webpage """

    # Return True if no captcha/blocked detected
    # Return String (reason of captcha/blocked)

    # Check page title for known captcha/blocked
    if "Attention Required! | Cloudflare" in visitData['pageTitle']:
        return const.captblock.CAPT_CLOUDFLARE
    elif "Captcha Challenge" in visitData['pageTitle']:
        return const.captblock.CAPT_HCAPTCHA
    elif "Captcha" in visitData['pageTitle']:
        return const.captblock.CAPT_IMUNIFY
    # From 105:Walmart.com
    elif "Verify your identity" in visitData['pageTitle']:
        return const.captblock.CAPT_SPECIFIC
    # elif visitData['url'].replace('https://', '').replace('www.', '') in visitData['pageTitle'].lower(): # Google & Amazon - The title has the domain name
    # Google & Amazon - The title has the URL value
    elif visitData['url'] in visitData['pageTitle'].lower():
        return const.captblock.CAPT_SPECIFIC

    return True


def check_tor_blocked(webpageContent, visitData):
    """ Check for webpage that block Tor """

    if "access denied" in visitData['pageTitle'].lower():  # 248:cnbc.com
        return const.errorCause.BLOCKED_TOR
    elif "blocked" in visitData['pageTitle'].lower():
        return const.errorCause.BLOCKED_TOR
    elif "not found" in visitData['pageTitle'].lower():
        return const.errorCause.BLOCKED_TOR
    elif "forbidden" in visitData['pageTitle'].lower():
        return const.errorCause.BLOCKED_TOR
    elif "error" in visitData['pageTitle'].lower():
        return const.errorCause.BLOCKED_TOR

    # Return True if no block
    return True


def validate_webpage_content(webpageFilePath, visitData):
    """ Handler for validate collected webpage data """

    # Check webpage file
    if os.stat(webpageFilePath).st_size == 0:
        raise ErrorFound(const.errorCause.HTML_EMPTY)

    # Read webpage file
    webpageFile = open(webpageFilePath, 'r')
    webpageContent = webpageFile.read()
    webpageFile.close()

    # Check for captcha blocking content
    if config.validate.webpageCaptcha == True:
        checkStatus = check_captcha_webpage(webpageContent, visitData)
        if checkStatus != True:
            raise ErrorFound(checkStatus)

    # Check for Tor-blocked content
    if config.validate.webpageBlocked == True:
        checkStatus = check_tor_blocked(webpageContent, visitData)
        if checkStatus != True:
            raise ErrorFound(checkStatus)


def filter_pcap_file(pcapFilePath, visitData):
    """ Filter PCAP file """
    
    if os.path.isfile(pcapFilePath):
        visitData['pcapRawSize'] = os.path.getsize(pcapFilePath)

        # Save raw pcap
        if config.pcap.saveRaw == True:
            pcapRaw = os.path.splitext(pcapFilePath)[0]+'.raw.pcapng'
            copyfile(pcapFilePath, pcapRaw)

        # Read and filter pcap
        pcapFiltered = []
        with PcapReader(pcapFilePath) as pcapReader:
            for packet in pcapReader:
                if 'TCP' in packet:
                    ip = packet.payload
                    if ip.dst in visitData['guardList'] or ip.src in visitData['guardList']:
                        # Remove TCP payload
                        if config.pcap.removePayload == True:
                            tcp = ip.payload
                            tcp.remove_payload()

                        pcapFiltered.append(packet)
        wrpcap(pcapFilePath, pcapFiltered)

        visitData['pcapSize'] = os.path.getsize(pcapFilePath)
    else:
        raise ErrorFound(const.errorCause.DUMPCAP_MISSING_FILE)


def check_pcap_packet_count(LOG, pcapFilePath):
    """ Check number of packet captured and raise error if smaller than minimumCount """
    
    if os.path.isfile(pcapFilePath):
        packetCount = 0
        with PcapReader(pcapFilePath) as pcapReader:
            for packet in pcapReader:
                packetCount += 1

        if packetCount < config.validate.minCapturePackets:
            LOG.error("{}: Captured packets ({}) is lower than {}".format(const.errorCause.MIN_PACKET_COUNT, packetCount, config.validate.minCapturePackets))
            raise ErrorFound(const.errorCause.MIN_PACKET_COUNT)
    else:
        raise ErrorFound(const.errorCause.DUMPCAP_MISSING_FILE)


def check_file_size(LOG, filePath, minimumSize, missingError=False):
    """ Check the collected file's size and raise error if smaller than minimumSize """

    fileName = ntpath.basename(filePath)
    if os.path.isfile(filePath):
        # Compare the minimum size
        if os.stat(filePath).st_size < minimumSize:
            LOG.error("{}: {} is smaller than {} bytes".format(const.errorCause.MIN_FILE_SIZE, fileName, minimumSize))
            raise ErrorFound(const.errorCause.MIN_FILE_SIZE)

    else:  # File not exist
        if missingError == True:
            LOG.error("{}: {}".format(const.errorCause.MISSING_COLLECTED_FILE, fileName))
            raise ErrorFound(const.errorCause.MISSING_COLLECTED_FILE)
