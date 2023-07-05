#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:33:48 2023

@author: aisulu
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 09:18:54 2023

@author: aisulu
"""

import sys
import os
from flask import Flask, render_template, request, jsonify
from denkovy_code import relay_control, relay_read_status
import configparser
import logging
import argparse
from datetime import date


parser = argparse.ArgumentParser(description='Denkovi python script')
parser.add_argument("--logdir", type=str, help='Path to directory with the script logs.',
                    default="/Users/aisulu/Desktop/DENKOVY/DENKOVY_proj/logs//")    #change path
parser.add_argument("--inifile", type=str, help='Path to config file.',
                    default="/Users/aisulu/Desktop/DENKOVY/DENKOVY_proj/denkovi.ini")    ##change path

args = parser.parse_args()
logdir = args.logdir
inifile = args.inifile

# ---------LOGGING-----------------------------------------------------------------------------
logger = logging.getLogger('')
if not os.path.exists(logdir):
    os.makedirs(logdir)
    print("Logs directory created: %s" % logdir)
logname = 'product_delivery-%s.log' % (date.today())

# point logging to file
file_log_handler = logging.FileHandler(logdir + logname)
logger.addHandler(file_log_handler)

# point logging to console
stderr_log_handler = logging.StreamHandler()
logger.addHandler(stderr_log_handler)

# ----------import config file-----------------------------------------------------------------
config = configparser.ConfigParser()
if os.path.isfile(inifile):
    try:
        config.read(inifile)
        board_ip = config.get("ADDRESS", "ip")
        board_port = config.get("ADDRESS", "port")
        relay_id_template = config.get("ADDRESS", "relay_oid_template")

    except Exception as e:
        logger.error("ERROR: Error reading ini file: %s", e)
        sys.exit(-1)
else:
    logger.error("no inifile %s exists" % inifile)
    exit(1)
    
r_id = 1        #pin in use (Pin 1)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle', methods=['POST'])
def snmp_toggle():
    data = request.get_json()
    state = data['state']
    if state == 'on':
        relay_control(relay_id_template, r_id, 1, board_ip, board_port, logger)
    elif state == 'off':
        relay_control(relay_id_template, r_id, 0, board_ip, board_port, logger)   
    status = relay_read_status(relay_id_template, r_id, board_ip, board_port, logger)
    new_state = 'ON' if status[0][1] == 1 else 'OFF'
    return jsonify({'state': new_state})

@app.route("/get_state", methods=["GET"])
def get_state():
    # Get the current state of the relay
    status = relay_read_status(relay_id_template, r_id, board_ip, board_port, logger)
    state = 'ON' if status[0][1] == 1 else 'OFF'
    return jsonify({"state": state})

if __name__ == '__main__':
    app.run()
    









