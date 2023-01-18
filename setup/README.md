# WFP-Collector: Setup
WFP-Collector requires set of system applications, browser applications, and python packages. You can choose the [Automate Setup](#Automate-WFP-Collector-Setup) for simplicity or manual setup [Manual Setup](#Manual-WFP-Collector-Setup) for full installation flexibility.


## Directory Structure
* [extension-preferences.json](extension-preferences.json) – Tor Browser extension preferences file
* [README.md](README.md) – This setup documentation.
* [setup](setup) – Bash script for setup automation.
* [setup.py](setup.py) – Python script for downloading and configuring Tor Browser and Geckodriver.


## Automate WFP-Collector Setup
The [setup](setup) script can be use to perform the WFP-Collector setup. All WFP-Collector core features are installed and configured automatically. The Rclone application also is installed. However, manual configurations still required to enable cloud upload (see [ Configure Cloud Upload](#Configure-Cloud-Upload)) and Telegram notification (see [ Configure Telegram Notification](#Configure-Telegram-Notification)) features.

* **IMPORTANT:** Please reboot the system immediately after successfully executing the [setup](setup) script to ensure proper user-permission integration.
* The [setup](setup) script will execute `apt-get update` and `apt-get upgrade` commands. If you wish to skip the `upgrade` command, run the [setup](setup) script with `--no-upgrade` argument.
* Step **[4]** in the [setup](setup) script is require for setup automation process. WFP-Collector does not require this step to functioning.
* Step **[5]** in the [setup](setup) script is require for tool testing purpose. WFP-Collector does not require this step to functioning.
* Ubuntu has variation of distribution such as Desktop, Server, and Docker. To ensure WFP-Collector work seamlessly on all distributions, the [setup](setup) script will explicitly install necessary system applications using `apt-get install` command despite it might be already included in the distribution.
* **NOTE:** Although WFP-Collector can functioning without the [config.json](../config.json) file, the [setup](setup) and [test](../test/test) scripts require this config file to download, configure, and test the required browser applications.


## Manual WFP-Collector Setup

#### 1. Install required system applications
1. Install Xvfb by using the `apt install xvfb` command.
2. Install Firefox by using the `apt install firefox` command. 
    * For Ubuntu Server 22.04 LTS, please install Firefox in .deb package version instead of the Snap version. Please refer to [How to Install Firefox as a .Deb on Ubuntu 22.04 (Not a Snap)](https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04).
    * Alternatively, Firefox (Snap) can be used, but several dependencies need to be install as execute on Step **[8]** in the [setup](setup) script.s
3. Install Dumpcap by using the `apt install wireshark` command.
    * By default, Dumpcap will not run without root-privileges. To ensure non-root users can run Dumpcap, please refer to [How do I run wireshark, with root-privileges?](https://askubuntu.com/questions/74059/how-do-i-run-wireshark-with-root-privileges). Please restart your system after the non-root privileges is configured.
    * By default, WFP-Collector will instruct Dumpcap to capture network traffic on the `eth0` network interface. If your system uses a different network interface, please set the `config.pcap.NET_INTERFACE` config.

#### 2. Install Python packages
In the repository's root directory (`WFP-Collector/`), execute the `pip install -r requirements.txt` command.

#### 3. Download Tor Browser and Geckodriver
1. Download Tor Browser from the [Tor Browser Download](https://www.torproject.org/download/). Extract the folder in [app/](app/) directory. The `tor-browser` folder must be accessible via `WFP-Collector/app/tor-browser` path.
2. Download Geckodriver from the [Geckodriver releases page](https://github.com/mozilla/geckodriver/releases/). Extract the file in the [app/](app/) directory. The `geckodriver` binary file must be accessible via `WFP-Collector/app/geckodriver` path.

#### 4. Add HAR Export Trigger extension
1. Open the Tor Browser and install the [HAR Export Trigger](https://addons.mozilla.org/en-US/firefox/addon/har-export-trigger/) extension. This extension is used to export the HTTP Archive.
2. Ensure the HAR Export Trigger extension is allowed in `Run in Private Windows`. Please refer to [Extensions in Private Browsing](https://support.mozilla.org/en-US/kb/extensions-private-browsing) for more information on enabling an extension in private windows.
3. To enable HTTP Archive data collection, please set `config.data.HAR` config to `True`.


## Additional Features Configuration

#### Configure Cloud Upload
1. Run `apt install rclone` command to install Rclone.
2. Please refer [Rclone Documentation](https://rclone.org/docs/) to do the initial setup for cloud storage (add remote config).
3. After a remote config is added to Rclone, please set the `config.data.CLOUD_UPLOAD_PATH` to a string value of your cloud storage path. As an example: `config.data.CLOUD_UPLOAD_PATH = "mycloudstorage:/WFP/Batch_A"` where `mycloudstorage:` is the Rclone's remote cloud storage name. 
4. To enable cloud upload, please set `config.data.ENABLE_CLOUD_UPLOAD` config to `True`.

#### Configure Telegram Notification
1. Create a Telegram Bot by referring to [Telegram Bot Docs](https://core.telegram.org/bots#how-do-i-create-a-bot).
2. You will receive a token for Telegram Bot API access. Use that token to set the `config.notification.TOKEN` config.
3. Telegram Bot requires a Chat ID to send the completion notification. To find Chat ID, you can refer to [How to Know Chat ID](https://www.wikihow.com/Know-Chat-ID-on-Telegram-on-Android) or [How to Get Group Chat ID](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id). Please use the Chat ID value to set the `config.notification.CHAT_ID` config. Make sure the Chat ID has a ‘-’ character in front of the numbers.
4. To enable the completion notification feature, please set `config.notification.ENABLE` config to `True`.



