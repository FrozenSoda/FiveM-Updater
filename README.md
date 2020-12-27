# FiveM-Updater
Update your FiveM server effortlessly.

## Prerequisites
### Operating System
This script is designed for Linux and has not been tested on, nor designed for, other operating systems.

### APT packages
**Debian/Ubuntu: Run <code>sudo apt update</code> then install with <code>sudo apt install \<package\></code>**
- python3
- python3-pip
- git

### Python packages
**Install with <code>pip3 install \<package\></code>**
- requests
- beautifulsoup4
- gitpython

## Downloading
1. Install all prerequisites according to the instructions above.
2. Switch to the user owning the FiveM server(s) by using <code>sudo su - \<user\></code>
3. Navigate to a parent directory of your FiveM server(s), preferably your home directory (<code>cd ~</code>)
4. Run <code>git clone https://github.com/steel9/FiveM-Updater.git</code>

## Usage
- To update your server, run <code>./fivem-updater.py --server-dir \<your-server-dir\></code>
- For more information about syntax and arguments, run <code>./fivem-updater.py -h</code>
- It is recommended that you call the updater from within your server start script.

### Example Start Script
<code>#!/bin/bash</code>\
<code>python3 /opt/fivem/FiveM-Updater/fivem-updater.py --server-dir "/opt/fivem/servers/$1"</code>\
<code>cd "/opt/fivem/servers/$1/FXServer/server-data"</code>\
<code>bash "/opt/fivem/servers/$1/FXServer/server/run.sh" +exec server.cfg</code>
