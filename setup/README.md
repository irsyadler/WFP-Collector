# WFP-Collector: Setup
WFP-Collector requires a set of system applications, browser applications, and python packages. You can choose the [Automate Setup](#Automate-WFP-Collector-Setup) for simplicity or manual setup [Manual Setup](#Manual-WFP-Collector-Setup) for full installation flexibility.


## Directory Structure
* [extension-preferences.json](extension-preferences.json) – Tor Browser extension preferences file
* [README.md](README.md) – This setup documentation.
* [setup](setup) – Bash script for setup automation.
* [setup.py](setup.py) – Python script for downloading and configuring Tor Browser and Geckodriver.


## Automate WFP-Collector Setup
The [setup script](setup) can be used to perform the WFP-Collector setup. All WFP-Collector core features are installed and configured automatically. The Rclone application (for cloud upload) is also installed. However, manual configurations are still required to enable cloud upload (see [ Configure Cloud Upload](#Configure-Cloud-Upload)) and Telegram notification (see [ Configure Telegram Notification](#Configure-Telegram-Notification)) features.

The WFP-Collector's [setup script](setup) can be executed using the following command:

```
bash setup/setup
```


* **IMPORTANT:** Please reboot the system immediately after successfully executing  the [setup script](setup) to ensure proper user-permission integration.
* The [setup script](setup) will execute `apt-get update` and `apt-get upgrade` commands. If you wish to skip the `upgrade` command, run the [setup script](setup) with the `--no-upgrade` flag.
* Step **[4]** in the [setup script](setup) is required for the setup automation process. WFP-Collector does not require this step to function.
* Step **[5]** in the [setup script](setup) is required for tool testing purposes. WFP-Collector does not require this step to function.
* Ubuntu (and other Linux-based OS) has a variety of distributions, such as Desktop, Server, and Docker. Hence, the [setup script](setup) will explicitly install necessary system applications despite it might be already included in the distribution. It is ensure WFP-Collector work seamlessly on all distributions.
* **NOTE:** Although WFP-Collector can function without the [config.json](../config.json) file, the [setup script](setup) requires this config file to download and configure the required browser applications.


## Manual WFP-Collector Setup

#### 1. Install required system applications
1. Install Xvfb by using the `sudo apt install xvfb` command.
2. Install Mozilla Firefox by using the `sudo apt install firefox` command. 
    * For Ubuntu Server 22.04 LTS, please install Mozilla Firefox in .deb package version instead of the Snap version. Please refer to [How to Install Firefox as a .Deb on Ubuntu 22.04 (Not a Snap)](https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04).
    * Alternatively, Mozilla Firefox (Snap) can be used. However, several dependencies must be installed as executed in Step **[8]** in the [setup script](setup).
3. Install Dumpcap by using the `apt install wireshark` command.
    * By default, Dumpcap will not run without root-privileges. To ensure non-root users can run Dumpcap, please refer to [How do I run wireshark, with root-privileges?](https://askubuntu.com/questions/74059/how-do-i-run-wireshark-with-root-privileges). Please restart your system after the non-root privilege is configured.
    * By default, WFP-Collector instruct Dumpcap to capture network traffic on the `eth0` network interface. If your system uses a different network interface, please change the option value for `pcap.networkInterface` in the [config.js](../config.js) file.
    * To list the available network interface, execute `ip link show` or `dumpcap -D` commands. However, only certain interface listed using these commands is connected to the Internet. Please refer [here](https://unix.stackexchange.com/questions/14961/how-to-find-out-which-interface-am-i-using-for-connecting-to-the-internet) for more information on finding the correct network interface connected to the Internet.

#### 2. Install Python packages
In the repository's root directory (`WFP-Collector/`), execute the `pip install -r requirements.txt` command.

#### 3. Download Tor Browser and Geckodriver
1. Download Tor Browser from the [Tor Browser Download](https://www.torproject.org/download/). Extract the downloaded archive into the [app/](../app/) directory. The archive contains a `tor-browser` folder which must be accessible via `WFP-Collector/app/tor-browser` path.
2. Download Geckodriver from the [Geckodriver releases page](https://github.com/mozilla/geckodriver/releases/). Extract the downloaded archive into the [app/](../app/) directory. The archive contains a `geckodriver` binary file which must be accessible via `WFP-Collector/app/geckodriver` path.

NOTE: The Tor Browser path can be changed using `path.browser` option, and the Geckodriver path can be set using `path.gecko` option. These two options can be added into `config` object in [config.js](../config.js) file.

#### 4. Add HAR Export Trigger extension
1. Open the Tor Browser and install the [HAR Export Trigger](https://addons.mozilla.org/en-US/firefox/addon/har-export-trigger/) extension. This extension is used to export the HTTP Archive.
2. Ensure the HAR Export Trigger extension is allowed in `Run in Private Windows`. Please refer to [Extensions in Private Browsing](https://support.mozilla.org/en-US/kb/extensions-private-browsing) for more information on enabling an extension in private windows.


## Additional Features Configuration
#### Configure Cloud Upload
1. Run `apt install rclone` command to install Rclone.
2. Please refer to [Rclone Documentation](https://rclone.org/docs/) to do the initial setup for cloud storage (add remote config).
3. Add the following options to the `config` object in the [config.js](../config.js) file:

```
"cloud.enable": true,
"cloud.uploadPath":"mycloudstorage:/WFP/Batch_A"
```

Note: The `mycloudstorage:` is the Rclone's remote cloud storage name, and the `/WFP/Batch_A` is the cloud storage's path for file upload.

#### Configure Telegram Notification
1. Create a Telegram Bot by referring to [Telegram Bot Docs](https://core.telegram.org/bots#how-do-i-create-a-bot).
2. You will receive a token for Telegram Bot API access. Use that token to set the value for `notification.token` option.
3. Telegram Bot requires a Chat ID to send a notification message. To find Chat ID, refer to [How to Know Chat ID](https://www.wikihow.com/Know-Chat-ID-on-Telegram-on-Android) or [How to Get Group Chat ID](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id). Please use the Chat ID value to set the value for `notification.chatID` option. Ensure the Chat ID has a `-` character in front of the numbers.
3. Using the retrieved token and Chat ID, add the following options to the `config` object in the [config.js](../config.js) file:

```
"notification.enable": true
"notification.token": "0000000000:Xxx...",
"notification.chatID": "-000000000"
```


## Command to check application/package version
* Ubuntu/Linux: `lsb_release -a`
* Mozilla Firefox: `firefox --version`
* Geckodriver: `geckodriver --version` (from [app/](../app/) directory)
* Python 3: `python3 --version`
* Pip: `pip --version`
* Python package: `pip show <package-name>`
* Rclone: `rclone --version`
* Dumpcap: `dumpcap --version`
* Xvfb: `apt show xvfb`
* Dumpcap: `firefox --version`

