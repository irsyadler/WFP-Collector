# WFP-Collector: Crawler


## Directory Structure
* [configurations.py](configurations.py) – Common configurations declaration.
* [constants.py](constants.py) – Common constants definition.
* [crawler.py](crawler.py) – Manage crawling activity execution.
* [functions.py](functions.py) – Common functions declaration.
* [README.md](README.md) – This crawler documentation.
* [run.py](run.py) – Start dataset collection.
* [uploaderNotifier.py](uploaderNotifier.py) – Functions for cloud upload and Telegram notification.
* [validation.py](validation.py) – Functions for validation and filtering of collected data.


## Dataset Collection
WFP-Collector simplified various tasks in the data collection and cleaning process. After a [visit database is created](../database/), **dataset collection** can be started using the following command:

```
python3 crawler/run.py
```

WFP-Collector will start crawling activity by visiting each webpage listed on the created visit database. The following are the parameters of [run.py](run.py):


```
usage: run.py [-h] [-l LABEL] [-v VIRTUAL] [-rf] [-mr MAXREPEAT] [-vd VISITDATABASE] [-op OUTPUTPATH] [-up UPLOADPATH] [-t]

Execute crawling activity.

options:
  -h, --help            Show this help message and exit
  -l LABEL, --label LABEL
                        Crawling activity label
  -v VIRTUAL, --virtual VIRTUAL
                        Execute crawling activity in the virtual display (headless mode)
  -rf, --repeatFail     Repeat failed visit
  -mr MAXREPEAT, --maxRepeat MAXREPEAT
                        The maximum number of repetitions for the FAILED visit to be revisited
  -vd VISITDATABASE, --visitDatabase VISITDATABASE
                        File path to the visit database for crawling activity (JSON file)
  -op OUTPUTPATH, --outputPath OUTPUTPATH
                        Directory path to store collected browsing data
  -up UPLOADPATH, --uploadPath UPLOADPATH
                        Directory path to upload the collected data
  -t, --test            Execute crawling activity in a testing environment
```


## Collected Data
By default, the WFP-Collector stores all collected data files from the crawling activity inside the [output](../output/) folder. Please refer to the journal paper for detailed descriptions of the WFP-Collector's collected data files from the crawling activity.

Suppose the user wants to save storage space. In that case, they can set the WFP-Collector to **compress** the collected files by adding the following options to the `config` object in [config.js](../config.js) file:

```
"data.html": "SAVE_COMPRESS",
"data.har": "SAVE_COMPRESS",
"data.visitLog": "SAVE_COMPRESS",
"data.stemLog": "SAVE_COMPRESS",
"data.tbdLog": "SAVE_COMPRESS",
"pcap.data": "SAVE_COMPRESS",
```

There are other possible file handling options as defined under the `file` class in [constants.py](constants.py).

By default, WFP-Collector will save the visible webpage screenshot. If the user intends to capture a full webpage screenshot (including non-visible parts) add the following options to the `config` object in [config.js](../config.js) file: 

```
"data.saveScreenshot": "FULL"
```


## Filtering and Validation
The data filtering and validation procedures in [validation.py](validation.py) are mostly related to the WFP experiment. Any additional procedures can be quickly added to the [validation.py](validation.py) file if needed.

WFP-Collector allows users to set **minimum file size requirements and capture packet count**. If any data files from a webpage visit fail to meet this minimum requirement, the webpage visit will be labelled as `FAILED`. The following is an example of `1024 Bytes` for minimum data file size and `50 packets` for minimum captured packet count:

```
"validate.minSizeHTML": 1024,
"validate.minSizeImg": 1024,
"validate.minSizeHAR": 1024,
"validate.minSizePcap": 1024,
"validate.minSizeVisitLog": 1024,
"validate.minSizeStemLog": 1024,
"validate.minSizeTBDLog": 1024,
"validate.minCapturePackets": 50
```

NOTE: All the above value is in byte unit, except for `"minCapturePackets"` which accept integer value.


## Tips and Tricks
* All configurations in [configurations.py](configurations.py) can be overridden by adding an option to the `config` object in [config.js](../config.js) file. Certain possible value for the option is defined in [constants.py](constants.py).
* The `visitStatus` for each visit instance has 3 possible statuses: `PENDING`, `COMPLETED` and `FAILED`, as defined in [constants.py](constants.py).
* Once a webpage visit is completed, the WFP-Collector will upload the collected data to the cloud. Modify the `cloud.uploadBatch` option if you want to upload only after a certain number of completed webpage visits.

