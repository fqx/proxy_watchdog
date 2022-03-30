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
from logging.handlers import WatchedFileHandler
from requests.exceptions import Timeout, ProxyError

# Constants
LOG_FILE = '/var/log/proxy_watchdog.log'
URL = 'http://connectivitycheck.gstatic.com/generate_204'
PROXY = {
  "http": "http://127.0.0.1:8118",
  "https": "http://127.0.0.1:8118",
}
SERVICE = 'v2ray'
SLEEP_TIMER = 300
MAX_RETRY = 3


# log setup
def log_setup():
    log_handler = WatchedFileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)


def restart(message):
    """Restart service and logg message"""
    subprocess.run(['service', SERVICE, 'restart'])
    logging.warning('Restart because of {}'.format(message))
    time.sleep(60)


def main():
    """Main"""
    log_setup()
    logging.info('Wait {} seconds for proxy to boot up.'.format(SLEEP_TIMER))
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
            logging.info('Proxy is working fine. Latency is {}ms.'.format(round(req.elapsed.microseconds/1000)))
            retry = 0
            time.sleep(SLEEP_TIMER)


if __name__ == '__main__':
    main()