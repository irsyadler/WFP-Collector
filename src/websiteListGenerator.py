import json, argparse, time, os.path
from functions import *
from definitions import *
from run import init_config

# Initiate configuration
init_config()

# Source website list filepath
WEBSITE_LIST_PATH = os.path.join(config.directory.PROJECT, 'database', 'sourceWebsiteList.json')

# Destination website list filepath
DATABASE_OUTPUT_PATH = config.directory.DATABASE_FILE

# Max number of website
MAX_NUMBER_OF_WEBSITE = 250

# Max number of rounds
MAX_NUMBER_OF_INSTANCE = 10000


def generate_crawler_database(args):
    
    generateTime = time.time()

    # Load Website List file into JSON
    fileObj = open(WEBSITE_LIST_PATH, "r")
    jsonData = json.load(fileObj)
    fileObj.close()

    # Init database file
    database, query = get_database_query(DATABASE_OUTPUT_PATH)
    allvisitList = []

    # Start round
    currentRound = 0
    while currentRound < args.instance:

        # Increment round counter
        currentRound += 1
        
        for item in jsonData[0:args.top]:
            
            # Build visit data
            name = str(item['rank'])
            url = 'https://' + (item['subdomain'] + '.' + item['domain'] if len(item['subdomain']) > 0 else item['domain'])

            # Build proper data format & add to list
            visitData = {'status': visitStatus.PENDING,
                        'name': "{}_{}_{}".format(name, 'd' if args.mode == 'both' or args.mode == 'desk' else 'm', currentRound),
                        'url': url,
                        'mode': browserMode.DESKTOP if args.mode == 'both' or args.mode == 'desk' else browserMode.MOBILE,
                        "records": []
                        }
            allvisitList.append(visitData.copy())
            
            # If both-mode, change mode to mobile and add to list
            if args.mode == 'both':
                visitData['name'] = "{}_m_{}".format(name, currentRound)
                visitData['mode'] = browserMode.MOBILE
                allvisitList.append(visitData)
    
    # Add list to database 
    database.insert_multiple(allvisitList)
   
    # Result
    print("Total crawling items: {}".format(len(database)))
    print("Generation time: {} seconds".format(round(time.time() - generateTime, 2)))
    print("Top {} websites in {}-mode was generated for {} instance(s).".format(args.top, args.mode, args.instance))



if __name__ == '__main__':

    # Check arguments
    parser = argparse.ArgumentParser(description='Generate website list for crawling.')
    parser.add_argument('-t', '--top', default=100, type=int, help='Set the maximum number of website for crawling')
    parser.add_argument('-m', '--mode', default='both', choices=['both', 'desk', 'mobi'], help='Set the browsing mode: Both, Desktop, or Mobile')
    parser.add_argument('-r', '--instance', default=1, type=int, help='Set the maximum number of instance for each visit')
    parser.add_argument('-o', '--overwrite', action='store_true')
    args = parser.parse_args()

    generate = True
    
    # Check if database already exist
    if os.path.isfile(DATABASE_OUTPUT_PATH):
        # Check if overwrite is not enable
        if not args.overwrite:
            print("ERROR: Database file \"{}\" already exist. Please use -o argument to overwrite current file.".format(DATABASE_OUTPUT_PATH))
            generate = False
        else:
            os.unlink(DATABASE_OUTPUT_PATH)

    # Check if the number of website exceed the available list.
    if args.top > MAX_NUMBER_OF_WEBSITE:
        print("ERROR: The number of WEBSITE for crawling exceeded {}.".format(MAX_NUMBER_OF_WEBSITE))
        generate = False

    # Check if the number of round exceed the limit.
    if args.instance < 1 or args.instance > MAX_NUMBER_OF_INSTANCE:
        print("ERROR: The number of INSTANCE should be between 1 and {}.".format(MAX_NUMBER_OF_INSTANCE))
        generate = False

    if generate:
        generate_crawler_database(args)
