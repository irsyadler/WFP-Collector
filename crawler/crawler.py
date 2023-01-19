############################################################
# Manage Crawling Activity Execution
############################################################

import time
import json
import os
import multiprocessing
import tempfile
import copy
import atexit
from stem.control import Controller
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb, launch_tbb_tor_with_stem
import tbselenium.common as cm
from selenium.webdriver.firefox.options import Options

# Import project module
from functions import *
from validation import *
from uploaderNotifier import *


def execute_webpage_visit_activity(visitData, shareDict):
    """ Execute webpage visit activity """

    # Update visit status for process shared variable
    shareDict[const.share.STATUS] = const.crawlingStatus.STARTED

    # Path for saving files
    FILE_ACT = os.path.join(config.path.output, visitData['name'] + '.act.json')  # Webpage visit activity metadata
    FILE_LOG = os.path.join(config.path.output, visitData['name'] + '.visit.log')  # Log file for this webpage visit activity.
    FILE_TBD = os.path.join(config.path.output, visitData['name'] + '.tbd.log')  # Log file from TBDriver
    FILE_STEM = os.path.join(config.path.output, visitData['name'] + '.stem.log')  # Log file from STEM
    FILE_HTML = os.path.join(config.path.output, visitData['name'] + '.html')  # Webpage HTML file
    FILE_HAR = os.path.join(config.path.output, visitData['name'] + '.har')  # Webpage HAR file
    FILE_IMG = os.path.join(config.path.output, visitData['name'] + '.png')  # Webpage screenshot
    FILE_PCAP = os.path.join(config.path.output, visitData['name'] + '.pcapng')  # PCAP file

    # Pass variable for file checking
    shareDict[const.share.PATH] = {'act': FILE_ACT, 'visit': FILE_LOG, 'tbd': FILE_TBD, 'stem': FILE_STEM,
                                   'html': FILE_HTML, 'har': FILE_HAR, 'img': FILE_IMG, 'pcap': FILE_PCAP}

    # Create activity log file and start logging
    # LOG is for debugging when activity is crashed and activity failed to be written on permanent storage
    LOG = create_logger(FILE_LOG, 'VISIT')
    LOG.info('[VISIT_START]')

    # Enclose all webpage visit activity inside try-catch
    try:

        # -> Setup STEM
        LOG.info('[SETUP_STEM]')
        # Define default Tor configuration file
        torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
                 'SOCKSPort': str(cm.STEM_SOCKS_PORT),
                 'DataDirectory': tempfile.mkdtemp(),
                 'Log': '{} file '.format(config.data.stemLogLevel) + FILE_STEM
                 }
        # Check for set exit node
        if config.crawler.setExitNode == True:
            torrc = set_exit_node(torrc)

        # Set custom torrc value
        for key in config.crawler.torrc:
            torrc[key] = config.crawler.torrc[key]

        # Initiate stem
        torProcess = launch_tbb_tor_with_stem(tbb_path=config.path.browser, torrc=torrc)

        # -> Setup Driver
        LOG.info('[START_DRIVER]')
        # Define preferences for TBDriver (loglevel)
        browserPreferences = {'extensions.torbutton.loglevel': int(config.data.tbdLoglevel), 'extensions.torlauncher.loglevel': int(config.data.tbdLoglevel)}

        # Define & Devtools (for HAR Export Trigger)
        browserOptions = Options()
        if config.data.har != const.file.SKIP:
            browserOptions.add_argument("-devtools")
            browserPreferences['devtools.toolbox.selectedTool'] = 'netmonitor'  # Ensure devtools is in network-tab
            browserPreferences['devtools.toolbox.host'] = 'window'  # Ensure devtools is in separate window

        # Mobile / Tablet preferences
        if visitData['mode'] == const.browserMode.MOBILE or visitData['mode'] == const.browserMode.TABLET:
            LOG.info('[{}_MODE]'.format(visitData['mode'].upper()))
            browserPreferences['privacy.resistFingerprinting'] = False
            browserPreferences['general.useragent.override'] = config.crawler.mobileUserAgent

        # Set custom torrc value
        for key in config.crawler.browserPreferences:
            browserPreferences[key] = config.crawler.browserPreferences[key]

        # Setup Driver
        driver = TorBrowserDriver(tbb_path=config.path.browser, executable_path=config.path.gecko, tor_cfg=cm.USE_STEM,
                                  pref_dict=browserPreferences, tbb_logfile_path=FILE_TBD, options=browserOptions)

        # -> Set windows size
        LOG.info('[RESIZE_BROWSER]')
        if visitData['mode'] == const.browserMode.MOBILE:  # Mobile screen
            driver.set_window_size(config.crawler.screenSizeMobile[0], config.crawler.screenSizeMobile[1])
        elif visitData['mode'] == const.browserMode.TABLET:  # Tablet screen
            driver.set_window_size(config.crawler.screenSizeTablet[0], config.crawler.screenSizeTablet[1])
        else:  # Desktop screen
            driver.set_window_size(config.crawler.screenSizeDesktop[0], config.crawler.screenSizeDesktop[1])

        # -> Wait to ensure window sized correctly
        LOG.info('[SLEEP_RESIZE]')
        time.sleep(config.wait.windowResize)

        # -> Run Dumpcap
        if config.pcap.data != const.file.SKIP:
            LOG.info('[START_DUMPCAP]')
            dumpcapProcess = start_dumpcap_process(FILE_PCAP)
            
            
        # -> Get target webpage
        LOG.info('[VISIT_WEBPAGE]')
        shareDict[const.share.STATUS] = const.crawlingStatus.BROWSING  # Update webpage visit status
        visitData['start'] = get_timestamp(True)  # For network packet tracing
        driver.load_url(visitData['url'])

        # -> Save circuit info
        LOG.info('[SAVE_CIRCUIT]')
        with Controller.from_port(port=cm.STEM_CONTROL_PORT) as controller:
            controller.authenticate()
            LOG.info('[CTRL_AUTHENTICATED]')

            # Get guard list
            visitData['guardList'] = []
            for routerStatus in controller.get_network_statuses():
                if 'Guard' in routerStatus.flags:
                    if routerStatus.address not in visitData['guardList']:
                        visitData['guardList'].append(routerStatus.address)

        # -> Wait for any additional / extra webpage content loading
        LOG.info('[SLEEP_AFTER]')
        time.sleep(config.wait.afterWebpageLoad)

        # Save information
        LOG.info('[SAVE_URL]')
        visitData['pageUrl'] = driver.current_url
        visitData['pageTitle'] = driver.title

        LOG.info('[SAVE_HTML]')
        writeToFile(FILE_HTML, driver.page_source)

        # -> Save HAR file
        if config.data.har != const.file.SKIP:
            LOG.info('[EXPORT_HAR]')
            harData = driver.execute_script("HAR_TEXT = HAR.triggerExport().then( result => { return result;}); return HAR_TEXT;")
            LOG.info('[SAVE_HAR]')
            # Put result under 'log' key to ensure Firefox able to read it later.
            writeToFile(FILE_HAR, json.dumps({'log': harData}, indent=config.data.jsonIndentation))

        # -> Stop Dumpcap
        if config.pcap.data != const.file.SKIP:
            # Kill all dumpcap's child and main processes
            LOG.info('[TERMINATE_DUMPCAP]')
            stop_dumpcap_process(dumpcapProcess)
            
        # -> Save screenshot
        if config.data.saveScreenshot == const.screenshot.FULL:
            LOG.info('[SAVE_SCREENSHOT_FULL]')
            driver.get_full_page_screenshot_as_file(FILE_IMG)
        elif config.data.saveScreenshot == const.screenshot.VISIBLE:
            LOG.info('[SAVE_SCREENSHOT_VISIBLE]')
            driver.get_screenshot_as_file(FILE_IMG)

        # -> Quit browser
        LOG.info('[QUIT_BROWSER]')
        visitData['stop'] = get_timestamp(True)  # For network packet tracing
        driver.quit()

        # -> Terminate Tor process
        LOG.info('[TERMINATE_TOR]')
        torProcess.kill()

        # -> Webpage webpage visit activity completed
        LOG.info('[VISIT_COMPLETED]')

        # Add visitData to shareDict for later validation (this is reference copy)
        shareDict[const.share.DATA] = visitData

        # -> Update webpage visit status
        shareDict[const.share.STATUS] = const.crawlingStatus.COMPLETED

    except ErrorFound as error:  # Catch error that explicitly raised
        LOG.error('[VISIT_ERROR]', exc_info=True)
        shareDict[const.share.STATUS] = const.crawlingStatus.FAILED  # Update webpage visit status
        shareDict[const.share.REASON] = str(error)  # Get error reason
    except Exception as error:
        LOG.error('[VISIT_EXCEPTION]', exc_info=True)
        shareDict[const.share.STATUS] = const.crawlingStatus.FAILED  # Update webpage visit status


def manage_crawling_activity():
    """ Manage the crawling activity of visiting each webpage in the database """

    # Create logger for crawling activity
    LOG = create_logger(os.path.join(config.path.output, config.main.logFilename), 'CRAWLER')

    try:
        LOG.info('[START_CRAWLER]')

        # -> Read database
        LOG.info('[READ_DB]')
        database, query = get_database_query(config.path.database)
        visitCounter, visitDatabase = read_visit_database(database, query, True)

        LOG.info('[VISIT_COUNTER] -> ' + str(visitCounter))
        LOG.info('[VISIT_TARGET] -> ' + config.crawler.visitStatus)

        # Crawling information data (use for notification and remote management)
        crawlingInfo = const.crawlingInfo()
        crawlingInfo.label = config.main.label
        crawlingInfo.hostname = config.main.hostname
        crawlingInfo.visitDatabasePath = config.path.database
        crawlingInfo.outputPath = config.path.output
        crawlingInfo.uploadPath = config.cloud.uploadPath 
        crawlingInfo.visitAll = visitCounter
        crawlingInfo.visitStatus = config.crawler.visitStatus
        crawlingInfo.visitAvailable = len(visitDatabase[config.crawler.visitStatus])
        crawlingInfo.visitCurrent = 0
        crawlingInfo.lastUpdate = get_timestamp()
        crawlingInfoFile = os.path.join(config.path.output, config.main.statusFilename)

        # Enable notification when crawling activity completed
        if config.notification.enable == True:
            atexit.register(notify_crawler_ended, crawlingInfo)

        # -> Check if there available visit
        if crawlingInfo.visitAvailable > 0:

            # Start the virtual display if enable
            if config.crawler.useVirtualDisplay == True:
                LOG.info('[START_VIRTUAL]')
                xvfb_display = start_xvfb(1920, 1080)

            # Loop through the visit database
            for visitData in visitDatabase[config.crawler.visitStatus]:

                # Phase 0 - Updating Crawling Activity Information ################################################################################
                # Skip database read if it is the first round, since there is no update
                if crawlingInfo.visitCurrent != 0:
                    crawlingInfo.visitAll = read_visit_database(database, query)
                    LOG.info('[VISIT_COUNTER] -> ' + str(crawlingInfo.visitAll))

                # Update crawling activity information
                crawlingInfo.visitCurrent += 1
                crawlingInfo.lastUpdate = get_timestamp()
                LOG.info('[CURRENT_VISIT] (' + str(crawlingInfo.visitCurrent) + '/' +
                         str(crawlingInfo.visitAvailable) + ')-> ' + str(visitData))

                # Write crawling activity information
                if config.crawler.writeActivityInformation == True:
                    writeToFile(crawlingInfoFile, json.dumps(crawlingInfoToDictionary(crawlingInfo)))

                # Phase 1 - Skipping Rule ################################################################################
                # -> Define any rule to skip the visit

                # Check to skip if round more than maxVisitRun
                if len(visitData['records']) > config.crawler.maxVisitRepeat:
                    print('SKIP_VISIT -> ' + visitData['name'])
                    continue
                else:
                    visitStartTimestamp = get_timestamp()

                # Phase 2 - Execute Activity Thread ################################################################################
                # -> Setup dictionary (shared variable) to read crawling status
                procManager = multiprocessing.Manager()
                shareDict = procManager.dict()
                shareDict[const.share.STATUS] = const.crawlingStatus.READY  # Initialize dictionary

                # -> Execute crawling activity
                executer = multiprocessing.Process(target=execute_webpage_visit_activity,
                                                   name="execute_crawl", args=(visitData, shareDict))
                executer.start()
                executer.join(config.wait.roundOne)

                # -> If currently in crawling (driver.get), keep waiting
                if shareDict[const.share.STATUS] == const.crawlingStatus.BROWSING:
                    LOG.info('[WAIT_FINAL]')
                    executer.join(config.wait.roundTwo)

                # -> The executor process should be terminated at this point
                executerStillAlive = False
                # Do process cleanup before check the status

                # -> Terminate the executer process if alive
                LOG.info('[CLEAN_THREAD]')
                if executer.is_alive():
                    executerStillAlive = True
                    executer.terminate()  # Terminate process
                    executer.join()  # Cleanup

                # -> Kill Tor, geckodriver & dumpcap running application
                LOG.info('[CLEAN_APP]')
                aliveApplicationCounter = kill_alive_process()

                # -> Check for unexpected alive application when the crawlingStatus supposed to be completed
                if shareDict[const.share.STATUS] == const.crawlingStatus.COMPLETED:
                    # Check for alive application
                    if aliveApplicationCounter > 0:  # There is alive application
                        LOG.warning('[VISIT_UNSTABLE] -> Alive application: ' + aliveApplicationCounter)
                        shareDict[const.share.STATUS] == const.crawlingStatus.FAILED
                        shareDict[const.share.REASON] = const.errorCause.ALIVE_APP

                    # Check for executor status
                    if executerStillAlive == True:  # The executor process still alive
                        LOG.warning('[VISIT_UNSTABLE] -> Alive executer')
                        shareDict[const.share.STATUS] == const.crawlingStatus.FAILED
                        shareDict[const.share.REASON] = const.errorCause.ALIVE_EXECUTER if aliveApplicationCounter > 0 else const.errorCause.ALIVE_APP_EXECUTER

                # Phase 3 - Filter and Validate Collected Data ################################################################################
                
                # -> Proceed only on completed visit
                if shareDict[const.share.STATUS] == const.crawlingStatus.COMPLETED:
                    try:
                        # -> Copy shareDict so it is mutable without sync: https://docs.python.org/3/library/multiprocessing.html#proxy-objects
                        visitData = copy.deepcopy(shareDict[const.share.DATA])

                        # -> Check and filter pcap file
                        if config.pcap.data != const.file.SKIP and config.pcap.filter == True:
                            LOG.info('[FILTER_DUMPCAP]')
                            filter_pcap_file(shareDict[const.share.PATH]['pcap'], visitData)

                        # -> Check if Webpage is empty, tor-blocked or behind captcha-related page
                        LOG.info('[VALIDATE_WEBPAGE]')
                        validate_webpage_content(shareDict[const.share.PATH]['html'], visitData)
                                
                        # Check captured packets count (after pcap filtered)
                        check_pcap_packet_count(LOG, shareDict[const.share.PATH]['pcap'])

                        # -> Check collected file minimum size
                        check_file_size(LOG, shareDict[const.share.PATH]['html'], config.validate.minSizeHTML)
                        check_file_size(LOG, shareDict[const.share.PATH]['img'], config.validate.minSizeImg)
                        check_file_size(LOG, shareDict[const.share.PATH]['har'], config.validate.minSizeHAR)
                        check_file_size(LOG, shareDict[const.share.PATH]['pcap'], config.validate.minSizePcap)
                        check_file_size(LOG, shareDict[const.share.PATH]['visit'], config.validate.minSizeVisitLog)
                        check_file_size(LOG, shareDict[const.share.PATH]['stem'], config.validate.minSizeStemLog)
                        check_file_size(LOG, shareDict[const.share.PATH]['tbd'], config.validate.minSizeTBDLog)
                        
                    except ErrorFound as error:  # Catch error that explicitly raised
                        LOG.error('[VALIDATION_FAILED]', exc_info=True)
                        shareDict[const.share.STATUS] = const.crawlingStatus.FAILED 
                        shareDict[const.share.REASON] = str(error)
                    except Exception as error:
                        LOG.error('[VALIDATION_EXCEPTION]', exc_info=True)
                        shareDict[const.share.STATUS] = const.crawlingStatus.FAILED  # Update crawling status without errorReason


                # Phase 4 - Post-processing Collected Data & File ################################################################################
                try:
                    # Generate checksum on collected file (before deletion or compression)
                    if config.data.fileChecksum == True:
                        LOG.info('[GENERATE_SHA256]')
                        visitData['sha256'] = generate_file_checksum(shareDict[const.share.PATH])

                    LOG.info('[POST_PROCESS_FILE]')
                    # Process .html
                    process_collected_file(LOG, shareDict[const.share.PATH]['html'], config.data.html, shareDict[const.share.STATUS])
                    # Process .visit.log
                    process_collected_file(LOG, shareDict[const.share.PATH]['visit'], config.data.visitLog, shareDict[const.share.STATUS])
                    # Process .stem.log
                    process_collected_file(LOG, shareDict[const.share.PATH]['stem'], config.data.stemLog, shareDict[const.share.STATUS])
                    # Process .tbd.log
                    process_collected_file(LOG, shareDict[const.share.PATH]['tbd'], config.data.tbdLog, shareDict[const.share.STATUS])
                    # Process .har
                    process_collected_file(LOG, shareDict[const.share.PATH]['har'], config.data.har, shareDict[const.share.STATUS])
                    # Process .pcapng
                    process_collected_file(LOG, shareDict[const.share.PATH]['pcap'], config.pcap.data, shareDict[const.share.STATUS])

                    # -> Remove the IP Addresses of Tor Guard
                    if config.data.saveGuardList != True and 'guardList' in visitData:
                        del visitData['guardList']

                    # -> Remove unnecessary data
                    if 'status' in visitData:
                        del visitData['status']
                    if 'records' in visitData:
                        del visitData['records']
                except Exception as error:
                        LOG.error('[POST_PROCESSING_ERROR]', exc_info=True)
                        visitData['errorPostProcessing'] = str(error)

                # Phase 5 - Update Database & Write act.json ################################################################################
                
                LOG.info('[UPDATE_DATABASE]')
                # -> Check the crawling activity status
                if shareDict[const.share.STATUS] == const.crawlingStatus.COMPLETED:  # Webpage visit activity is completed
                    LOG.info('[VISIT_FINISHED]')
                    database.update({'status': const.visitStatus.COMPLETED}, query.name == visitData['name'])
                    
                else:  # Webpage visit activity failed
                    LOG.warning('[VISIT_FAILED]')
                    database.update({'status': const.visitStatus.FAILED}, query.name == visitData['name'])
                    # Get failed reason if available
                    if const.share.REASON in shareDict:
                        errorReason = shareDict[const.share.REASON]
                    else:
                        # Read last text from .visit.log and record it as errorReason
                        errorReason = read_last_visit_log(shareDict[const.share.PATH]['visit'])

                    # Update error records
                    append_visit_records(database, query, visitData['name'], visitStartTimestamp, errorReason)
                    visitData['failed'] = errorReason
                    
                # -> Save activity json file
                LOG.info('[SAVE_ACTIVITY]')
                writeToFile(shareDict[const.share.PATH]['act'], json.dumps(visitData, indent=config.data.jsonIndentation))

                # Phase 6 - Upload To Cloud ################################################################################

                # Check if cloud enable
                if config.cloud.enable == True:
                    # Check if this is the round to upload
                    if (crawlingInfo.visitCurrent % int(config.cloud.uploadBatch)) == 0:
                        LOG.info('[UPLOADING_DATA]')
                        upload_data()

                # -> Wait before next fetch
                LOG.info('[SLEEP_NEXT]')
                time.sleep(config.wait.beforeNextVisit)
            # End of activity iteration ------------
            # Uploading data
            if config.cloud.enable == True:
                LOG.info('[FINAL_UPLOADING_DATA]')
                upload_data()

            # Update crawling activity information
            crawlingInfo.isAllDone = True
            crawlingInfo.visitAll = read_visit_database(database, query)
            crawlingInfo.lastUpdate = get_timestamp()
            LOG.info('[FINAL_VISIT_COUNTER] -> ' + str(crawlingInfo.visitAll))

            # Write crawling activity information
            if config.crawler.writeActivityInformation == True:
                writeToFile(crawlingInfoFile, json.dumps(crawlingInfoToDictionary(crawlingInfo)))

            # Stop virtual display if enable
            if config.crawler.useVirtualDisplay == True:
                LOG.info('[STOP_VIRTUAL]')
                stop_xvfb(xvfb_display)

            LOG.info('[STOP_CRAWLER]')
        else:  # No visit data for processing
            LOG.info('[NO_VISIT_AVAILABLE] -> QUIT')

    except Exception as error:
        LOG.error('[EXCEPTION_CRAWLER]', exc_info=True)


if __name__ == '__main__':
    print("Please run crawling activity from 'run.py' file.")
