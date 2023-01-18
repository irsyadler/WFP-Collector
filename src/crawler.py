# Import all neccessary modules
import time, json, os, multiprocessing, tempfile, copy, atexit, subprocess
from stem.control import Controller
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb, launch_tbb_tor_with_stem
import tbselenium.common as cm
from selenium.webdriver.firefox.options import Options


from functions import *
from validator import *
from uploaderNotifier import *

############################################################
# Function Definition
############################################################

# Execute crawling activity
def execute_crawling_activity(visitData, sharedDict):

    # Update crawling status for process shared variable
    sharedDict[variable.STATUS] = crawlingStatus.STARTED

    # Path for saving files
    FILE_ACT = os.path.join(config.directory.DATA, visitData['name'] + '.act.json')
    FILE_LOG = os.path.join(config.directory.DATA, visitData['name'] + '.ca.log') # Log file for this crawling activity. 
    FILE_TBD = os.path.join(config.directory.DATA, visitData['name'] + '.tbd.log') # Log file from TBDriver
    FILE_STM = os.path.join(config.directory.DATA, visitData['name'] + '.stm.log') # Log file from STEM
    FILE_HTM = os.path.join(config.directory.DATA, visitData['name'] + '.html') # Extraction HTML file
    FILE_HAR = os.path.join(config.directory.DATA, visitData['name'] + '.har') # Extraction HAR file
    FILE_IMG = os.path.join(config.directory.DATA, visitData['name'] + '.png') # Webpage screenshot
    FILE_PCP = os.path.join(config.directory.DATA, visitData['name'] + '.pcapng') # PCAP file

    # Pass variable for file deletion
    sharedDict[variable.PATH] = {'ca': FILE_LOG, 'tbd': FILE_TBD, 'stm': FILE_STM}

    # Create activity log file and start logging
    # LOG is for debugging when activity is crashed and activity failed to be written on disk
    LOG = create_logger(FILE_LOG, 'CA')
    LOG.info('[VISIT_START]')


    # Enclose all crawling activity inside try-catch
    try:
        # -> Setup STEM
        LOG.info('[SETUP_STEM]')
        # Define default Tor configuration file
        torrc = {'ControlPort': str(cm.STEM_CONTROL_PORT),
                 'SOCKSPort': str(cm.STEM_SOCKS_PORT),
                 'DataDirectory': tempfile.mkdtemp(),
                 'Log': 'notice file ' + FILE_STM
                }
        # Check for set exit node
        if config.crawling.SET_EXIT_NODE == True:
            torrc = set_exit_node(torrc)

        # Initiate stem
        torProcess = launch_tbb_tor_with_stem(tbb_path=config.directory.TBB, torrc=torrc)


        # -> Setup Driver
        LOG.info('[START_DRIVER]')
        # Define preferences for TBDriver (loglevel)
        browserPreferences = {'extensions.torbutton.loglevel': 2, 'extensions.torlauncher.loglevel': 2}
        
        # Define & Devtools (for HAR Export Trigger)
        browserOptions = Options()
        if config.data.HAR == True:
            browserOptions.add_argument("-devtools")
            browserPreferences['devtools.toolbox.selectedTool'] = 'netmonitor' # Ensure devtools is in network-tab
            browserPreferences['devtools.toolbox.host'] = 'window' # Ensure devtools is in seperate window

        if visitData['mode'] == browserMode.MOBILE or visitData['mode'] == browserMode.TABLET:  # Mobile / Tablet Driver
            LOG.info('[{}_MODE]'.format(visitData['mode'].upper()))
            # Add mobile settings
            browserPreferences['privacy.resistFingerprinting'] = False
            browserPreferences['general.useragent.override'] = config.crawling.MOBILE_UA
            driver = TorBrowserDriver(tbb_path=config.directory.TBB, executable_path=config.directory.GECKO, tor_cfg=cm.USE_STEM, pref_dict=browserPreferences, tbb_logfile_path=FILE_TBD, options=browserOptions)
           
        else:  # Desktop Driver
            driver = TorBrowserDriver(tbb_path=config.directory.TBB, executable_path=config.directory.GECKO, tor_cfg=cm.USE_STEM, pref_dict=browserPreferences, tbb_logfile_path=FILE_TBD, options=browserOptions)
            
        
        # -> Set windows size
        LOG.info('[RESIZE_BROWSER]')
        if visitData['mode'] == browserMode.MOBILE:  # Mobile screen
            driver.set_window_size(config.crawling.SCREEN_SIZE_MOBILE[0], config.crawling.SCREEN_SIZE_MOBILE[1])
        elif visitData['mode'] == browserMode.TABLET:  # Tablet screen
            driver.set_window_size(config.crawling.SCREEN_SIZE_TABLET[0], config.crawling.SCREEN_SIZE_TABLET[1])
        else:  # Desktop screen
            driver.set_window_size(config.crawling.SCREEN_SIZE_DESKTOP[0], config.crawling.SCREEN_SIZE_DESKTOP[1])


        # -> Wait to ensure window sized correctly
        LOG.info('[SLEEP_RESIZE]')
        time.sleep(config.wait.RESIZE_WINDOW)


        # -> Run Dumpcap
        if config.pcap.ENABLE == True:
            LOG.info('[START_DUMPCAP]')
            dumpcapCommand = 'dumpcap -P -a duration:{} -a filesize:{} -i {} -s 0 -f \'{}\' -w \'{}\''.format(config.pcap.MAX_DUMP_DURATION, config.pcap.MAX_DUMP_SIZE, config.pcap.NET_INTEFACE, config.pcap.FILTER, FILE_PCP)
            # Execute dumpcap process
            dumpcapProcess = subprocess.Popen(dumpcapCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            dumpcapTimeout = config.pcap.START_TIMEOUT  
            while dumpcapTimeout > 0 and not check_dumpcap_process(dumpcapProcess):
                time.sleep(0.1)
                dumpcapTimeout -= 0.1
            if dumpcapTimeout < 0:
                raise Exception(errorCause.DUMPCAP_START_TIMEOUT)
            else:
                visitData['pcapStart'] = config.pcap.START_TIMEOUT - dumpcapTimeout


        # -> Get target webpage
        LOG.info('[VISIT_WEBPAGE]')
        sharedDict[variable.STATUS] = crawlingStatus.BROWSING # Update crawling status
        visitData['start'] = get_timestamp(True) # For network packet tracing
        driver.load_url(visitData['url'])


        # -> Save circuit info
        LOG.info('[SAVE_CIRCUIT]')
        with Controller.from_port(port=cm.STEM_CONTROL_PORT) as controller:
            controller.authenticate()
            LOG.info('[CTRL_AUTHENTICATED]')

            # Get guard list
            guardList = []
            for routerStatus in controller.get_network_statuses():
                if 'Guard' in routerStatus.flags:
                    if routerStatus.address not in guardList:
                        guardList.append(routerStatus.address)

            # Save guard list
            if config.pcap.KEEP_GUARD_LIST == True:
                visitData['guards'] = guardList

        # -> Wait for any additional / extra webpage content loading
        LOG.info('[SLEEP_AFTER]')
        time.sleep(config.wait.AFTER_GET)


        # Save information
        LOG.info('[SAVE_URL]')
        visitData['pageUrl'] = driver.current_url
        visitData['pageTitle'] = driver.title


        # Save HTML
        if config.data.HTML == True:
            LOG.info('[SAVE_HTML]')
            writeToFile(FILE_HTM, driver.page_source)
            

        # -> Generate HAR file
        if config.data.HAR == True:
            LOG.info('[EXTRACT_HAR]')
            harData = driver.execute_script("HAR_TEXT = HAR.triggerExport().then( result => { return result;}); return HAR_TEXT;")
            LOG.info('[SAVE_HAR]')
            # Put result under 'log' key to ensure Firefox able to read it later.
            writeToFile(FILE_HAR, json.dumps({'log': harData}, indent=config.data.JSON_INDENTION))
         

        # -> Stop Dumpcap
        if config.pcap.ENABLE == True:
            # Kill all child and main processes
            LOG.info('[TERMINATE_DUMPCAP]')
            for child in get_child_process(dumpcapProcess.pid):
                child.kill()
            dumpcapProcess.kill()


        # -> Save screenshot
        if config.data.SCREENSHOT == True:
            LOG.info('[SAVE_SCREENSHOT]')
            driver.get_screenshot_as_file(FILE_IMG)


        # -> Quit browser
        LOG.info('[QUIT_BROWSER]')
        visitData['stop'] = get_timestamp(True) # For network packet tracing
        driver.quit()


        # -> Terminate Tor process
        LOG.info('[TERMINATE_TOR]')
        torProcess.kill()


        # -> Check and filter pcap file
        if config.pcap.ENABLE == True:
            LOG.info('[FILTER_DUMPCAP]')
            filter_pcap_file(FILE_PCP, visitData, guardList)


        # -> Check if Webpage is tor-blocked or behind captcha-related page
        LOG.info('[CHECK_WEBPAGE]')
        if config.data.CHECK_WEBPAGE == True:
            checkedStatus = validate_webpage(FILE_HTM, visitData)
            if checkedStatus != True:
                raise Exception(checkedStatus)


        # -> Save activity datafile
        LOG.info('[SAVE_ACTIVITY]')
        # Remove status and records key, but ensure not to accidentally remove the obj reference from main
        visitDataToKeep = copy.deepcopy(visitData)
        del visitDataToKeep['status']
        del visitDataToKeep['records']

        writeToFile(FILE_ACT, json.dumps(visitDataToKeep, indent=config.data.JSON_INDENTION))


        # -> Browsing activity completed
        LOG.info('[VISIT_COMPLETED]')


        # -> Update crawling status
        sharedDict[variable.STATUS] = crawlingStatus.COMPLETED

    except Exception as e:
        LOG.error('[VISIT_EXCEPTION]', exc_info=True)
        sharedDict[variable.STATUS] = crawlingStatus.FAILED  # Update crawling status
        sharedDict[variable.REASON] = str(e) # Get error reason
    


# Main function
def manage_crawling_activity():
        
    # Create logger for crawling activity
    LOG = create_logger(os.path.join(config.directory.DATA, config.directory.MAIN_LOG_FILENAME), 'MAIN')

    try:
        LOG.info('[START_MAIN]')

        # -> Read database
        LOG.info('[READ_DB]')
        database, query = get_database_query(config.directory.DATABASE_FILE)
        visitCounter, visitList = read_visit_database(database, query, True)

        LOG.info('[VISIT_COUNTER] -> ' + str(visitCounter))
        LOG.info('[VISIT_TARGET] -> ' + config.crawling.VISIT_STATUS)

        # Crawling information data (use for botNotification and getActivityStatus)
        crawlingInfo.label = config.main.LABEL
        crawlingInfo.hostname = config.main.HOSTNAME
        crawlingInfo.visitAll = visitCounter
        crawlingInfo.visitStatus = config.crawling.VISIT_STATUS
        crawlingInfo.visitAvailable = len(visitList[config.crawling.VISIT_STATUS])
        crawlingInfo.visitCurrent = 0
        crawlingInfo.lastUpdate = get_timestamp()
        crawlingInfoFile = os.path.join(config.directory.DATA, config.directory.MAIN_STATUS_JSON)

        # Enable notification if setted
        if config.notification.ENABLE == True:
            atexit.register(call_notification_bot)

        # -> Check if there available visit
        if crawlingInfo.visitAvailable > 0:

            # Start the virtual display if enable
            if config.crawling.ENABLE_VIRTUAL_DISPLAY == True:
                LOG.info('[START_VIRTUAL]')
                xvfb_display = start_xvfb(1920, 1080)

            # Loop through the list
            for visitData in visitList[config.crawling.VISIT_STATUS]:
                
                # Phase 0 - Updating crawling activity information ################################################################################
                # Skip database read if it is the first round, since there is no update
                if crawlingInfo.visitCurrent != 0:
                    crawlingInfo.visitAll = read_visit_database(database, query)
                    LOG.info('[VISIT_COUNTER] -> ' + str(crawlingInfo.visitAll))

                # Update crawling activity information
                crawlingInfo.visitCurrent += 1
                crawlingInfo.lastUpdate = get_timestamp()
                LOG.info('[CURRENT_VISIT] (' + str(crawlingInfo.visitCurrent)+ '/'+ str(crawlingInfo.visitAvailable) + ')-> ' + str(visitData))

                # Write crawling activity information
                if config.crawling.ENABLE_WRITE_INFORMATION == True:
                    writeToFile(crawlingInfoFile, json.dumps(crawlingInfoToDictionary()))

                # Phase 1 - Skipping rule ################################################################################
                # -> Define any rule to skip the visit

                #### Check to skip if round more than MAX_VISIT_RUN
                if len(visitData['records']) > config.crawling.MAX_VISIT_RUN:
                    print('SKIP_VISIT -> ' + visitData['name'])
                    continue
                else :
                    visitStartTimestamp = get_timestamp()
                    
                # Phase 2 - Execution & cleaning ################################################################################
                # -> Setup dictionary (shared variable) to read crawling status
                procManager = multiprocessing.Manager()
                shareDict = procManager.dict()
                shareDict[variable.STATUS] = crawlingStatus.READY # Initialize dictionary

                # -> Execute crawling activity
                executer = multiprocessing.Process(target=execute_crawling_activity, name="excute_ba", args=(visitData, shareDict))
                executer.start()
                executer.join(config.wait.EXECUTER_INITIAL)

                # -> If currently in crawling (driver.get), keep waiting
                if shareDict[variable.STATUS] == crawlingStatus.BROWSING:
                    LOG.info('[WAIT_FINAL]')
                    executer.join(config.wait.EXECUTER_FINAL)

                # -> The executor process should be terminated at this point
                executerStillAlive = False
                # Do process cleanup before check the status

                # -> Terminate the executer process if alive
                LOG.info('[CLEAN_THREAD]')
                if executer.is_alive():
                    executerStillAlive = True
                    executer.terminate() # Terminate process 
                    executer.join() # Cleanup

                # -> Kill Tor & geckodriver running application
                LOG.info('[CLEAN_APP]')
                aliveApplicationCounter = kill_alive_process()
                
                # Phase 3 - Check & update status ################################################################################
                # -> Check the crawling activity status
                if shareDict[variable.STATUS] == crawlingStatus.COMPLETED: # Browsing activity is completed
                    # Check for unstable state
                    isUnstable = False
                    unstableCause = None
                    
                    # Check for alive application
                    if aliveApplicationCounter > 0: # There is alive application
                        isUnstable = True
                        unstableCause = errorCause.ALIVE_APP
                        LOG.warning('Alive application: ' + aliveApplicationCounter)
                        
                    # Check for executor status
                    if executerStillAlive == True: # The executor process still alive
                        isUnstable = True
                        unstableCause = errorCause.ALIVE_EXECUTER if unstableCause == None else errorCause.ALIVE_APP_EXECUTER

                    # -> Update the activity status to database
                    if isUnstable == True: # It is unstable
                        database.update({'status': visitStatus.FAILED}, query.name == visitData['name'])
                        # Update unstable records
                        append_visit_records(database, query, visitData['name'], visitStartTimestamp, unstableCause)
                        LOG.warning('[VISIT_UNSTABLE] -> ' + unstableCause)
                        # Update status for Phase 4
                        shareDict[variable.STATUS] == crawlingStatus.FAILED

                    else:
                        database.update({'status': visitStatus.COMPLETED}, query.name == visitData['name'])
                        LOG.info('[VISIT_COMPLETED]')
                    
                else: # Browsing activity is failed.
                    database.update({'status': visitStatus.FAILED}, query.name == visitData['name'])
                    # Get failed reason if available
                    if variable.REASON in shareDict:
                        errorReason = errorReasonFilter(shareDict[variable.REASON].strip())

                    else: # Get statusReason from log file
                        # It is expected the last status of .ba.log will be recorded as errorReason
                        errorReason, text = get_last_ba_log_status(os.path.join(config.directory.DATA, visitData['name'] + '.ba.log'))
                        if errorReason == None: # The log has no content or unreadable
                            errorReason = text
                        elif errorReason == '[GET_DUMMY]':
                            errorReason = errorCause.GET_DUMMY # Just to ensure proper formatted
                        elif errorReason != None:
                            pass # The error is in formatted
                        else: # text != None: 
                            errorReason = errorReasonFilter(text.strip()) # Text has content
                        
                    # Update error records
                    append_visit_records(database, query, visitData['name'], visitStartTimestamp, errorReason)
                    LOG.warning('[VISIT_FAILED]')

                # Phase 4 - Processing / Deleting file ################################################################################
                # Remove BA_LOG if enable
                if (config.data.REMOVE_CA_LOG == removeLog.ALWAYS) or (config.data.REMOVE_CA_LOG == removeLog.SUCCEED and shareDict[variable.STATUS] == crawlingStatus.COMPLETED):
                    LOG.info('[REMOVING_BA_LOG]')
                    if os.path.exists(shareDict[variable.PATH]['ca']):
                        os.remove(shareDict[variable.PATH]['ca'])
                    else:
                        LOG.warning('[UNFOUND_BA_LOG]')

                # Remove STM_LOG if enable
                if (config.data.REMOVE_STEM_LOG == removeLog.ALWAYS) or (config.data.REMOVE_STEM_LOG == removeLog.SUCCEED and shareDict[variable.STATUS] == crawlingStatus.COMPLETED):
                    LOG.info('[REMOVING_STEM_LOG]')
                    if os.path.exists(shareDict[variable.PATH]['stm']):
                        os.remove(shareDict[variable.PATH]['stm'])
                    else:
                        LOG.warning('[UNFOUND_STEM_LOG]')

                # Remove TBD_LOG if enable
                if (config.data.REMOVE_TBD_LOG == removeLog.ALWAYS) or (config.data.REMOVE_TBD_LOG == removeLog.SUCCEED and shareDict[variable.STATUS] == crawlingStatus.COMPLETED):
                    LOG.info('[REMOVING_TBD_LOG]')
                    if os.path.exists(shareDict[variable.PATH]['tbd']):
                        os.remove(shareDict[variable.PATH]['tbd'])
                    else:
                        LOG.warning('[UNFOUND_TBD_LOG]')

                # Phase 5 - Upload to cloud ################################################################################
                
                # Check if cloud enable
                if config.data.ENABLE_CLOUD_UPLOAD == True:
                    # Check if this is the round to upload
                    if (crawlingInfo.visitCurrent % config.data.CLOUD_UPLOAD_VISIT_BATCH) == 0:
                        LOG.info('[UPLOADING_DATA]')
                        upload_data()

                # -> Wait before next fetch
                LOG.info('[SLEEP_NEXT]')
                time.sleep(config.wait.NEXT_VISIT)
            # End of activity iteration ------------
            # Uploading data
            if config.data.ENABLE_CLOUD_UPLOAD == True:
                LOG.info('[FINAL_UPLOADING_DATA]')
                upload_data()
                
            # Update crawling activity information
            crawlingInfo.isAllDone = True
            crawlingInfo.visitAll = read_visit_database(database, query)
            crawlingInfo.lastUpdate = get_timestamp()
            LOG.info('[FINAL_VISIT_COUNTER] -> ' + str(crawlingInfo.visitAll))

            # Write crawling activity information
            if config.crawling.ENABLE_WRITE_INFORMATION == True:
                writeToFile(crawlingInfoFile, json.dumps(crawlingInfoToDictionary()))

            # Stop virtual display if enable
            if config.crawling.ENABLE_VIRTUAL_DISPLAY == True:
                LOG.info('[STOP_VIRTUAL]')
                stop_xvfb(xvfb_display)

        else: # No item for processing
            LOG.info('[NO_ITEM] -> QUIT')

    except Exception as e:
        LOG.error('[EXCEPTION_MAIN]', exc_info=True)



if __name__ == '__main__':
    print("Please run crawling activity from 'run.py' file.")

