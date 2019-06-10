#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""  

Simple web server watchdog, edit constants and stop start commands
preferably run with daemon
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

modified by FQX

""" 

# Import's
import requests
import subprocess
import time
import logging
from requests.exceptions import Timeout, ProxyError

# Constants
LOG_FILE = '/var/log/proxy_watchdog.log'
URL = 'http://www.gstatic.com/generate_204'
PROXY = {
  "http": "http://127.0.0.1:8118",
  "https": "http://127.0.0.1:8118",
}
SERVICE = 'v2ray'
SLEEP_TIMER = 300
MAX_RETRY = 3

# Opening log
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_FILE)


def restart(message):
    """Restart service and logg message"""
    subprocess.run(['service', SERVICE, 'restart'])
    logging.warning('Restart because of {}'.format(message))
    time.sleep(60)


def main():
    """Main"""
    time.sleep(SLEEP_TIMER)
    logging.info('Start watchdog.')
    retry = 0
    while True:
        try:
            req = requests.get(URL, timeout=5, proxies=PROXY)
        except (KeyboardInterrupt, SystemExit):
            logging.info('Stop watchdog.')
            break
        except ProxyError:
            restart('Proxy is down.')
            continue
        except Timeout:
            logging.info('Timeout.')
            retry += 1
            if retry > MAX_RETRY:
                retry = 0
                restart('Timeout.')
            time.sleep(60)
            continue
        if req.status_code != 204:
            restart('Wrong return.')
            continue
        else:
            logging.info('Proxy is working fine. Sleep 300 seconds.')
            retry = 0
            time.sleep(SLEEP_TIMER)


if __name__ == '__main__':
    main()