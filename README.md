# WFP-Collector
WFP-Collector: Automated Dataset Collection of Tor Browser for Website Fingerprinting Evaluations.


## Description
When researching WFP on Tor, a sufficiently large and clean dataset is crucial for a quality and accurate experiment. WFP-Collector is an open-source tool that automatically enables researchers to build a suitable dataset for WFP on Tor experiments. This tool automates the tedious and repetitive tasks of crawling activity, network traffic capturing, and data cleaning, freeing up the researcher’s time for other, more productive tasks. The WFP-Collector also supports a flexible and configurable dataset collection process that can conform to various researchers’ requirements and conditions. 


## Version
This WFP-Collector code version is `0.5.2`.


## Repository Structure
* [app/](app/) – Directory for Tor Browser and Geckodriver.
* [crawler/](crawler/) – Directory for WFP-Collector crawling activity.
* [database/](database/) –  Directory for visit database and visit source list for crawling activity.
* [docker/](docker/) – Directory for Docker-related files.
* [output/](output/) – Directory for collected data from crawling activity.
* [setup/](setup/) – Directory for WFP-Collector installation tool.
* [test/](test/) – Directory for WFP-Collector testing tool.
* [config.json](config.json) – Directory for WFP-Collector testing tool.
* [requirements.txt](requirements.txt) – List of the required Python packages.
* [run](run) – Common execution script for WFP-Collector tool.


## Tested Environment
The WFP-Collector was tested on the following development environment:
* Ubuntu = 22.04.1 LTS
* Firefox = 106.0.2
* Python = 3.10.6
* Pip = 22.0.2
* Xvfb = 2:21.1.3-2ubuntu2.2
* Rclone = 1.53.3
* Tor Browser = 11.5.4
* Geckodriver = 0.32.0
* HAR Export Trigger = 0.6.1
* Dumpcap = 3.6.2

Warning: **Windows and macOS are not supported.**


## How To Use
#### 1. Download the WFP-Collector source code
Clone this repository by using the following command:
```
git clone https://github.com/irsyadler/WFP-Collector
```
Enter this repository directory by using the following command:

```
cd WFP-Collector
```

#### 2. Setup and configure required applications and packages
The **[setup section](setup/)** explain the complete installation procedure to use WFT-Collector tool. To make things easier, we provide setup automation script which can be executed by using the following command:
```
bash run setup
```
* **IMPORTANT:** Please reboot the system immediately after successfully executing this command before continuing to ensure proper user-permission integration.

#### 3. Test the WFP-Collector tool
To ensure WFP-Collector working as expected, the **[test section](test/)** explain the complete testing procedure of the WFT-Collector tool. To make things easier, we provide automate testing script which can be executed by using the following command:
```
bash run test
```

#### 4. Create a Visit Database
Before starting the dataset collection, a visit database need to be created. This database contains list of name and webpage url to be visited during the crawling activity. The **[database section](database/)** describe complete guide on the visit database creation process. A visit database can be created using the following command:
```
bash run database
```

#### 5. Collect a New Dataset
Based on the previous created visit database, WFP-Collector can begin the data collection process. The **[crawler section](datcrawlerabase/)** provide comprehensive guides on the crawling-related activity. The data collection can be started using the following command:
```
bash run crawler
```

## Configuration File
To add or modify configurations in WFP-Collector, user can user can use [config.json](config.json/) to overwrite existing config. This config file contains four main aspects as follow:
* `"config": {...}` – Modify existing configurations defined in [configurations.py](crawler/configurations.py).
* `"torrc": {...}` – Add or modify [Tor configurations](https://2019.www.torproject.org/docs/tor-manual.html.en).
* `"browserPreferences": {...}` – Add or modify Tor Browser [configuration](https://support.mozilla.org/bm/questions/1358615).
* `"setup": {...}` – Modify WFP-Collector [setup](setup) configuration. The [test](test) script also use this configuration for testing.

**NOTE:** The content of this configuration file is case-sensitive.


## Nice to know, Pitfalls and TODOs
* Tor Browser is based on Mozilla Firefox. Make sure you can run Mozilla Firefox on the same system. It may help discover issues such as missing libraries, displays etc. 
* Make sure you can run the Tor Browser in the same system and network to ensure your network does not block Tor. For more information on Tor obfuscation, please refer to [Tor Bridge](https://bridges.torproject.org/).
* The validating and filtering feature is based on the current website list’s contents and parameters. These webpages’ contents are commonly changed or updated from time to time. Hence, the validating and filtering criteria might be outdated. To modify the validating and filtering process, please refer to [validation.py](crawler/validation.py).
* Certain webpage visits will produce `selenium.common.exceptions.TimeoutException` exception when the webpage loading is over 300000ms. It is important to note that the crawling activity is inside a Tor network. Hence, the network performance is dissimilar to the regular Internet.
* Stem is required to obtain the Tor Guard’s list. However, the Stem sometimes requires over 90 seconds to establish the connection, which will raise `OSError: reached a 90 second timeout without success` exception.
* Certain webpage might redirect the visited domain to another domain due to localised content. Tor randomly select the Exit Relay to increase anonymity. Therefore, the visited domain might not match the Exit Relay's IP Address locality. Hence, redirection to the localised domain might occur.


## Licensing
**WFP-Collector** is available under the [AGPL-3.0-only](LICENSE) license.


## Contact
For any inquiries please contact: `contact [at] irsyadler [dot] com`.
