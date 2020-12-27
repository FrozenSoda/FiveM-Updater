# FiveM-Updater
Update your FiveM server effortlessly.

## Prerequisites
### Operating System
This script is designed for Linux and has not been tested on, nor designed for, other operating systems.

### APT packages
**Debian/Ubuntu: Run <code>sudo apt update</code> once then install with <code>sudo apt install \<package\></code>**
- python3
- python3-pip
- git

### Python packages
**Install with <code>pip3 install \<package\></code> while signed in to the user that is running your FiveM server**
- requests
- beautifulsoup4
- gitpython

## Downloading
1. Install the APT prerequisites according to the instructions above, while signed in to a user with root privileges.
2. Switch to the user owning the FiveM server(s) by using <code>sudo su - \<user\></code>
3. Install the Python prerequisites according to the instructions above.
4. Navigate to a parent directory of your FiveM server(s), preferably your home directory (<code>cd ~</code>)
5. Run <code>git clone https://github.com/steel9/FiveM-Updater.git</code>

## Usage
- To update your server, run <code>./fivem-updater.py --server-dir \<your-server-dir\></code>
- As the script might break if the FiveM website/packages change, you can be notified via Pushover if it fails. To be notified, specify the arguments <code>--pushover-user-key \<your-user-key\></code> and <code>--pushover-app-token \<your-app-token\></code>
- Update this updater script by running <code>git pull</code> after <code>cd</code>:ing to the script directory. This is useful if the script for some reason stops working. Keep in mind that the script syntax/arguments _might_ change after an update, so make sure you verify that everything is working afterwards.
- It is recommended that you call the updater from within your server start script.
- For more information about syntax and arguments, run <code>./fivem-updater.py -h</code>

### Example Start Script
<code>#!/bin/bash</code>\
<code>python3 /opt/fivem/FiveM-Updater/fivem-updater.py --server-dir "/opt/fivem/servers/$1"</code>\
<code>cd "/opt/fivem/servers/$1/FXServer/server-data"</code>\
<code>bash "/opt/fivem/servers/$1/FXServer/server/run.sh" +exec server.cfg</code>
