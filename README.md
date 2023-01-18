# WFP-Collector
WFP-Collector: Automated Dataset Collection of Tor Browser for Website Fingerprinting Evaluations.


## Description
When researching WFP on Tor, a sufficiently large and clean dataset is crucial for a quality and accurate experiment. WFP-Collector is an open-source tool that automatically enables researchers to build a suitable dataset for WFP on Tor experiments. This tool automates the tedious and repetitive tasks of crawling activity, network traffic capturing, and data cleaning, freeing up the researcher’s time for other, more productive tasks. The WFP-Collector also supports a flexible and configurable dataset collection process that can conform to various researchers’ requirements and conditions. 


## Documentation
WFP-Collector tool is written in Python programming language with a self-documentation approach. All necessary information regarding the variables, functions, class definitions and behaviour configurations are described in the codes files. Standalone documentation is currently appeared to be unnecessary. If more complex features, package modules, or APIs are introduced in the future, separate documentation will be considered.


## Version
This WFP-Collector code version is `0.2.1`.


## Directory Structure
* [app/](app/) – Directory for Tor Browser and geckodriver.
* [data/](data/) – Directory for output of dataset collection.
* [database/](database/) – Directory for visit database and visit source list for crawling activity.
* [src/](src/) – Main code for WFP-Collector.
    * [configurations.py](src/configurations.py) – Store all main configurations and options.
    * [crawler.py](src/crawler.py) – Manage and execute crawling activity.
    * [definitions.py](src/definitions.py) – Define common constant variable.
    * [functions.py](src/functions.py) – Common functions declaration
    * [run.py](src/run.py) – Start crawling activity.
    * [uploaderNotifier.py](src/uploaderNotifier.py) – Functions for cloud upload and completion notification.
    * [validator.py](src/validator.py) – Functions for validation and filtering.
    * [websiteListGenerator.py](src/websiteListGenerator.py) – Generate website list for website generation.


## Tested Environment
The WFP-Collector was tested on the following development environment:
* Ubuntu = 22.04.1 LTS
* Firefox = 106.0.2 (non-Snap)
* Python = 3.10.6
* Pip = 22.0.2
* Xvfb = 2:21.1.3-2ubuntu2.2
* Rclone = 1.53.3
* Tor Browser = 11.5.4
* Geckodriver = 0.32.0
* HAR Export Trigger = 0.6.1
* Dumpcap = 3.6.2

Warning: **Windows and macOS are not supported.**


## Installation
WFP-Collector provides various additional features compared to existing WFP's data collection architecture. However, certain users might not require to use all the additional features. Hence, the core part of the WFP-Collector requires the user to do installation steps 1 to 3. Steps 4 to 6 are for the extra features. We designed the WFP-Collector with easy cloud deployment in mind. After the first installation procedures are completed, the user can **skip most installation steps** by copying the installed and configured repository folder from one server to another.

#### 1. Install required applications:
1. Install Xvfb by using the `apt install xvfb` command.
2. Install Firefox by using the `apt install firefox` command. **IMPORTANT:** For Ubuntu 22.04 LTS, please install Firefox in .deb package version instead of the Snap version. Please refer to [How to Install Firefox as a .Deb on Ubuntu 22.04 (Not a Snap)](https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04).
3. Install Dumpcap by using the `apt install wireshark` command. **IMPORTANT:** By default, Dumpcap will not run without root-privileges. To ensure non-root users can run Dumpcap, please refer to [How do I run wireshark, with root-privileges?](https://askubuntu.com/questions/74059/how-do-i-run-wireshark-with-root-privileges). Please restart your system after the non-root privileges is configured. **IMPORTANT:** By default, Dumpcap will capture network traffic from the `eth0` network interface. If your system uses a different network interface, please set the `config.pcap.NET_INTEFACE` config.

#### 2. Install required Python packages:
`pip install -r requirements.txt`

#### 3. Download Tor Browser and geckodriver:
1. Download Tor Browser from the [Tor Browser Download](https://www.torproject.org/download/). Extract the folder in [app/](app/) directory. `tor-browser_en-US` folder is expected in the [app/](app/) directory. If a non-English language is used, please update the  `config.directory.TBB` config.
2. Download geckodriver from the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases/). Extract the file in the [app/](app/) directory. `geckodriver` file is expected in the [app/](app/) directory.

#### 4. Add HAR Export Trigger extension (optional):
1. Open the Tor Browser and install the [HAR Export Trigger](https://addons.mozilla.org/en-US/firefox/addon/har-export-trigger/) extension. This extension is used to export the HTTP Archive.
2. Ensure the HAR Export Trigger extension is allowed in `Run in Private Windows`. Please refer to [Extensions in Private Browsing](https://support.mozilla.org/en-US/kb/extensions-private-browsing) for more information on enabling an extension in private windows.
3. To enable HTTP Archive data extraction, please set `config.data.HAR` config to `True`.

#### 5. Add cloud storage account in Rclone (optional):
1. Run `apt install rclone` command to install Rclone.
2. Please refer [Rclone Documentation](https://rclone.org/docs/) to do the initial setup for cloud storage (add remote config).
3. After a remote config is added to Rclone, please set the `config.data.CLOUD_UPLOAD_PATH` to a string value of your cloud storage path. As an example: `config.data.CLOUD_UPLOAD_PATH = "mycloudstorage:/WFP/Batch-1"`. `mycloudstorage:` is the Rclone's remote cloud storage name. 
4. To enable cloud upload, please set `config.data.ENABLE_CLOUD_UPLOAD` config to `True`.

#### 6. Setup Telegram Bot (optional):
1. Create a Telegram Bot by referring to [Telegram Bot Docs](https://core.telegram.org/bots#how-do-i-create-a-bot).
2. You will receive a token for Telegram Bot API access. Use that token to set the `config.notification.TOKEN` config.
3. Telegram Bot requires a Chat ID to send the completion notification. To find Chat ID, you can refer to [How to Know Chat ID](https://www.wikihow.com/Know-Chat-ID-on-Telegram-on-Android) or [How to Get Group Chat ID](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id). Please use the Chat ID value to set the `config.notification.CHAT_ID` config. Make sure the Chat ID has a ‘-’ character in front of the numbers.
4. To enable the completion notification feature, please set `config.notification.ENABLE` config to `True`.


## Start Automate Dataset Generation
WFP-Collector simplified various tasks in the data collection and cleaning process. A user can automatically generate a cleaned dataset for WFP on Tor experiments with only **two commands**.

#### 1. Generate website list for visit:
```
python3 src/websiteListGenerator.py
```
A new JSON file contain list of website to be visited in the crawling activity process. The generated filename is defined in [run.py](src/run.py) under `config.main.DATABASE` config. To show  additional arguments on [websiteListGenerator.py](src/websiteListGenerator.py), please use the `-h` argument for help.

#### 2. Execute crawling activity:
```
python3 src/run.py
```
WFP-Collector will start crawling activity by visiting each website listed on the generated website list. To show additional arguments on [run.py](src/run.py), please use the `-h` argument for help.

WFP-Collector stores all generated data from the crawling activity inside the [data/](data/) folder. Please refer to the journal paper for detailed descriptions of WFP-Collector's generated data from the crawling activity.

Various data extraction, validating, and filtering procedures can be enabled or disabled in the [configurations.py](src/configurations.py) file. The data checking and filtering procedures in [validator.py](src/validator.py) are mostly related to the WFP experiment. Any additional procedures can be quickly added to the [validator.py](src/validator.py) file if needed.


## Tips and Tricks
* Several important configs are placed in [run.py](src/run.py). These configs will most probably change frequently during testing and development. These configs also will be referred by the [websiteListGenerator.py](src/websiteListGenerator.py) to store the generated website list.
* For quick configuration changes, you can update the config variable in the [run.py](src/run.py) file under `# -- Step 3 -> Override any other configuration (configurations.py) -- #` section. For an example, to update the `config.directory.TBB`, add the following line: `os.path.join(config.directory.APP, "tor-browser_de")`.
* The list of configurations and options for WFP-Collector can be found in the [configurations.py](src/configurations.py) and [definitions.py](src/definitions.py) files. These files contain detailed descriptions of each possible configuration and option.
* The `config.main.LABEL` config labels the dataset generation activity. By default, WFP-Collector stores the generated data inside a directory based on the `config.main.LABEL` config in the [data/](data/) directory. The cloud upload also utilised the same approaches to store the generated data.
* The `visitStatus` for each visit instance has 3 statuses, which is `PENDING`, `COMPLETED`, and `FAILED` as defined in [definitions.py](src/definitions.py).
* A visit instance with `FAILED` as it `visitStatus` can be rerun using the `-r` argument when executing [run.py](src/run.py) script.
* You can disable the headless browsing by set the `config.crawling.ENABLE_VIRTUAL_DISPLAY` config as `False`.
* You can automatically remove the log files for a successful visit by set the `config.data.REMOVE_CA_LOG`, `config.data.REMOVE_STEM_LOG`, and `config.data.REMOVE_TBD_LOG` configs as `removeLog.SUCCEED`.
* Once a website visit is completed, the WFP-Collector will upload the generated data to the cloud. If you want to upload only after a certain number of completed website visits, set the number on `config.data.CLOUD_UPLOAD_VISIT_BATCH` config.

#### Source Website List
* You can change the source of website list by modifying the [sourceWebsiteList.json](database/sourceWebsiteList.json) file. This file is in JSON format.
* The `rank` key refers to the website ranking on the Alexa Top Website. The rank number is also useful as an ID for each website.
* The `subdomain` key is used to set any website's subdomain. It is common for websites to have `www` as their subdomain. If no subdomain is required, please put an empty string.


## Nice to know, Pitfalls and TODOs
* Tor Browser is based on Mozilla Firefox. Make sure you can run Mozilla Firefox (non-Snap version) on the same system. It may help discover issues such as missing libraries, displays etc. 
* Make sure you can run the Tor Browser in the same system and network to ensure your network does not block Tor. For more information on Tor obfuscation, please refer to [Tor Bridge](https://bridges.torproject.org/).
* The validating and filtering feature is based on the current website list’s contents and parameters. These websites’ contents are commonly changed or updated from time to time. Hence, the validating and filtering criteria might be outdated. To modify the validating and filtering process, please refer to [validator.py](src/validator.py).
* Certain website visits will produce `selenium.common.exceptions.TimeoutException` exception when the website loading is over 300000ms. It is important to note that the crawling activity is inside a Tor network. Hence, the network performance is dissimilar to the regular Internet.
* Stem is required to extract the Tor Guard’s list. However, the Stem sometimes requires over 90 seconds to establish the connection, which will raise `OSError: reached a 90 second timeout without success` exception.
* Certain websites might redirect the visited domain to another domain due to localised content. Tor randomly select the Exit Relay to increase anonymity. Therefore, the visited domain might not match the Exit Relay's IP Address locality. Hence, redirection to the localised domain might occur.


## Licensing
**WFP-Collector** is available under the [AGPL-3.0-only](LICENSE) license.


## Contact
For any inquiries please contact: `contact [at] irsyadler [dot] com`.

