# WFP-Collector: Test
To ensure that WFP-Collector can collect a new dataset as expected, we provide a [test script](test) to test the WFP-Collector functionality. This test also will be helpful in **debugging installation or configuration errors**. The test is also performed in verbose mode so the user can easily understand and replicate the commands used in the [test script](test).

**NOTE:** To ensure testing-related requirements are installed, please run the [setup script](../setup/setup) before executing the [test script](test).


## Directory Structure
* [README.md](README.md) – This test documentation.
* [test](test) – Bash script for WFP-Collector testing (start testing using this script).
* [test.py](test.py) – Python script for WFP-Collector testing.
* [testCloudUpload.txt](testCloudUpload.txt) – Test file for testing the cloud upload feature.
* [testVisitDatabaseSource.csv](testVisitDatabaseSource.csv) – Source file to test visit database creation.


## Testing Activity
The WFP-Collector's [test script](test) can be executed using the following command:

```
bash test/test
```

The [test script](test) will perform the following check:
* [1] Ensure the required system applications are available
* [2] Checking `"config"` in the configuration file ([config.js](../config.js)).
* [3] Ensure the Tor Browser and Geckodriver are available and configured appropriately.
* [4] Ensure the required python packages are available with the correct version.
* [5] Ensure Dumpcap is working with the correct interface and permission.
* [6] (If cloud upload is enabled) Ensure the cloud upload feature using Rclone is functional
* [7] (If Telegram notification is enabled) Ensure the Telegram notification feature is functional
* [8] Test the visit database creation using a custom CSV source file
* [9] Test the main crawler activity

**NOTE:** The test will succeed if all tests are passed and the visited webpage is completed successfully. Sometimes, the visited webpage might fail due to network performance. Hence, please run the test twice or thrice if the test failed due to the visited webpage failing.


## Test Result
#### Successful test
A successful test will be ended with the following message:
```
WFP-Collector Testing: SUCCEED
```
A test output folder will be created to save all the collected test data in the following directory: `WFP-Collector/test/TEST_<timestamp>`. The `<timestamp>` is a number generated based on the time the [test script](test) is executed.

#### Failed test
A failed test will be ended with the following message:
```
WFP-Collector Testing: FAILED
```
The lines before this message will hint at the failure's reason.
