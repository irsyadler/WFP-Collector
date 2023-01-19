# WFP-Collector: Database
Crawling activity requires a visit database to start data collection. A visit database is a JSON file built using [TinyDB](https://tinydb.readthedocs.io/en/latest/). This database contain a list of visit items for the crawling activity. Each visit item contains the following properties:
* `status` – The status of this visit item. Possible value: PENDING, COMPLETED, FAILED.
* `name` – The visit name which will be used as the collected filename's prefix.
* `mode` – The browsing mode: DESKTOP, MOBILE, TABLET.
* `url` – The webpage URL (must include 'https://' or 'http://') to be browsed by the Tor Browser.
* `records` – The records of failed visit with error reason.


## Directory Structure
* [ats_global_500.csv](ats_global_500.csv) – CSV source file (from Alexa's Top 500 Sites).
* [create.py](create.py) – Script to create a visit database file.
* [README.md](README.md) – This database documentation.


## Visit Database Creation
A visit database can be created using the following command:

```
python3 database/create.py
```

The following are the parameters of [create.py](create.py):

```
usage: create.py [-h] [-t TOP] [-m {desktop,mobile,tablet} [{desktop,mobile,tablet} ...]] [-i INSTANCE] [-o] [-sp SOURCEPATH] [-vd VISITDATABASE]

Create a visit database for crawling activity.

options:
  -h, --help            Show this help message and exit
  -t TOP, --top TOP     Set the number of URLs (from the top) to be included in the visit database
  -m {desktop,mobile,tablet} [{desktop,mobile,tablet} ...], --mode {desktop,mobile,tablet} [{desktop,mobile,tablet} ...]
                        Set the browsing mode: desktop, mobile, or tablet
  -i INSTANCE, --instance INSTANCE
                        Set the number of instances for each URL
  -o, --overwrite       Overwrite existing visit database
  -sp SOURCEPATH, --sourcePath SOURCEPATH
                        Path to a CSV source file for visit database creation
  -vd VISITDATABASE, --visitDatabase VISITDATABASE
                        Path to save the created visit database (JSON file)
```


## CSV source file
To create a visit database, a CSV source file is required. This CSV file contain list of visit name and webpage URL. You can change the list of URL by modifying [ats_global_500.csv](ats_global_500.csv) or providing an external CSV source file.

NOTE: The CSV source file should not contain a header/title on the top.

#### Visit name
* A string represents the visit name.
* This string must contain [characters that are valid to be used as a filename](https://www.mtu.edu/umc/services/websites/writing/characters-avoid/).
* This visit name will use as the filename's prefix for collected data in the [output](../output) directory.
* If the visit name is a number (similar to [ats_global_500.csv](ats_global_500.csv)), [create.py](create.py) will append a leading `0`. This leading `0` ensures that the file sorting (based on string value) sorts the prefix number appropriately. For example, if the [ats_global_500.csv](ats_global_500.csv) is used to create a visit database for the top 100 webpage URLs, the collected filename for the first webpage URL will have `001` as its prefix.

#### Webpage URL
* The webpage URL can be a domain such as `google.com` or a full URL such as `https://www.google.com`.
* The [create.py](create.py) will prepend the `https://` on the URL if it does not exist.
