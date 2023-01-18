# WFP-Collector: Test
To ensure WFP-Collector can collect dataset as expected, we provide a [test](test) script to test the WFP-Collector functionality. This test also will be useful to **debug  installation or configuration errors**.
------ Test step 5 until 9 will show the command example and verbose command output

## Directory Structure
* [README.md](README.md) – This test documentation.
* [test](test) – Bash script for WFP-Collector testing (start testing using this script).
* [test.py](test.py) – Python script for WFP-Collector testing.
* [testCloudUpload.txt](testCloudUpload.txt) – Test file for testing the cloud upload feature.
* [testVisitDatabaseSource.csv](testVisitDatabaseSource.csv) – Source file to test visit database creation.


## Test activity
The [test](test) script will execute the following check:
* [1] Ensure the required system applications are available
* [2] Checking `"config"` in the configuration file ([config.js](../config.js)).
* [3] Ensure the Tor Browser and Geckodriver are available and configure appropriately.
* [4] Ensure the required python packages are available with correct version.
* [5] Ensure Dumpcap is working with correct interface and permission.
* [6] (If cloud upload enabled) Ensure the cloud upload feature using Rclone is functional
* [7] (If Telegram notification enabled) Ensure the Telegram Bot notification feature is functional
* [8] Test the visit database creation using custom csv source file
* [9] Test the main crawler activity


**NOTE:** The test will succeed if all test are passed and the visited webpage is completed successfully. Sometime, the visited webpage might failed to to network performances. Hence, try running the test twice or thrice if the test failed due to visited webpage failed.


## Test Result
#### Successful test
A successful test will ended with the following message:
```
WFP-Collector Testing: SUCCEED
```
An test output folder will be create to save all the collected test data in the following directory: `WFP-Collector/test/TEST_<timestamp>`. The `<timestamp>` is a number generated based on the time of test being execute.

#### Failed test
A failed test will ended with the following message:
```
WFP-Collector Testing: FAILED
```
The lines before this message will give the hint about the failure's reason.
