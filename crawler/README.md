# WFP-Collector: Crawler


## Directory Structure
* [configurations.py](configurations.py) – Common configurations declaration.
* [constants.py](constants.py) – Common constants definition.
* [crawler.py](crawler.py) – Manage and execute crawling activity.
* [functions.py](functions.py) – Common functions declaration.
* [README.md](README.md) – This crawler documentation.
* [run.py](run.py) – Start dataset collection.
* [uploaderNotifier.py](uploaderNotifier.py) – Functions for cloud upload and Telegram notification.
* [validation.py](validation.py) – Functions for validation and filtering of collected data.

## Dataset Collection
WFP-Collector simplified various tasks in the data collection and cleaning process. After a [visit database created](../database/), **dataset collection** can be started using the following command:
```
python3 crawler/run.py
```
WFP-Collector will start crawling activity by visiting each website listed on the generated website list. The following are the parameters of [run.py](run.py)
```
usage: run.py [-h] [-l LABEL] [-v VIRTUAL] [-rf] [-mr MAXREPEAT] [-vd VISITDATABASE] [-op OUTPUTPATH] [-up UPLOADPATH] [-t]

Execute crawling activity.

options:
  -h, --help            Show this help message and exit
  -l LABEL, --label LABEL
                        Crawling activity label
  -v VIRTUAL, --virtual VIRTUAL
                        Execute crawling activity in virtual display (headless mode)
  -rf, --repeatFail     Repeat failed visit
  -mr MAXREPEAT, --maxRepeat MAXREPEAT
                        The maximum number of repetition for the failed-visit to be revisit
  -vd VISITDATABASE, --visitDatabase VISITDATABASE
                        File path to the visit database for crawling activity (JSON file)
  -op OUTPUTPATH, --outputPath OUTPUTPATH
                        Directory path to store collected browsing data
  -up UPLOADPATH, --uploadPath UPLOADPATH
                        Directory path to upload the collected data
  -t, --test            Execute crawling in testing procedure
```


WFP-Collector stores all generated data from the crawling activity inside the [output](../output/) folder. Please refer to the journal paper for detailed descriptions of WFP-Collector's generated data from the crawling activity.

Various data is collected, validating, and filtering procedures can be enabled or disabled in the [configurations.py](src/configurations.py) file. The data checking and filtering procedures in [validator.py](src/validator.py) are mostly related to the WFP experiment. Any additional procedures can be quickly added to the [validator.py](src/validator.py) file if needed.



## Tips and Tricks
* For quick configuration changes, you can update the config variable in the [run.py](src/run.py) file under `# -- Step 3 -> Override any other configuration (configurations.py) -- #` section. For an example, to update the `config.directory.TBB`, add the following line: `os.path.join(config.directory.APP, "tor-browser_de")`.
* The list of configurations and options for WFP-Collector can be found in the [configurations.py](src/configurations.py) and [definitions.py](src/definitions.py) files. These files contain detailed descriptions of each possible configuration and option.
* The `config.main.LABEL` config labels the dataset generation activity. By default, WFP-Collector stores the generated data inside a directory based on the `config.main.LABEL` config in the [data/](data/) directory. The cloud upload also utilised the same approaches to store the generated data.
* The `visitStatus` for each visit instance has 3 statuses, which is `PENDING`, `COMPLETED`, and `FAILED` as defined in [definitions.py](src/definitions.py).
* A visit instance with `FAILED` as it `visitStatus` can be rerun using the `-r` argument when executing [run.py](src/run.py) script.
* You can disable the headless browsing by set the `config.crawling.ENABLE_VIRTUAL_DISPLAY` config as `False`.
* You can automatically remove the log files for a successful visit by set the `config.data.REMOVE_CA_LOG`, `config.data.REMOVE_STEM_LOG`, and `config.data.REMOVE_TBD_LOG` configs as `removeLog.SUCCEED`.
* Once a website visit is completed, the WFP-Collector will upload the generated data to the cloud. If you want to upload only after a certain number of completed website visits, set the number on `config.data.CLOUD_UPLOAD_VISIT_BATCH` config.



