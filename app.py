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
                    default="./logs//")    #change path
parser.add_argument("--inifile", type=str, help='Path to config file.',
                    default="./denkovi.ini")    ##change path

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
        r_id = config.get("ADDRESS", "r_id_1")
        
    except Exception as e:
        logger.error("ERROR: Error reading ini file: %s", e)
        sys.exit(-1)
else:
    logger.error("no inifile %s exists" % inifile)
    exit(1)

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Check connection to Denkovi module
        relay_read_status(relay_id_template, r_id, board_ip, board_port, logger)
        return render_template('index.html', board_ip=board_ip, board_port=board_port)
    except Exception as e:
        # Pass the error message to the template
        error_message = f"Failed to retrieve the initial state."
        return render_template('index.html', error_message=error_message, board_ip=board_ip, board_port=board_port)

@app.route('/toggle', methods=['POST'])
def snmp_toggle():
    try:
        data = request.get_json()
        state = data['state']

        if state == 'on':
            relay_control(relay_id_template, r_id, 1, board_ip, board_port, logger)
            logger.error("The relay was turned ON")
        elif state == 'off':
            relay_control(relay_id_template, r_id, 0, board_ip, board_port, logger)
            logger.error("The relay was turned OFF")

        # Retrieve the updated status after the state change
        status = relay_read_status(relay_id_template, r_id, board_ip, board_port, logger)
        new_state = 'ON' if status[0][1] == 1 else 'OFF'

        # Log the current state
        logger.error("Current relay state: %s", new_state)

        return jsonify({'state': new_state})
    except Exception as e:
        # Handle the exception and return an error message
        error_message = str(e)
        return jsonify({"error": error_message}), 500
    
@app.route("/get_state", methods=["GET"])
def get_state():
    # Get the current state of the relay
    status = relay_read_status(relay_id_template, r_id, board_ip, board_port, logger)
    state = 'ON' if status[0][1] == 1 else 'OFF'
    return jsonify({"state": state})

if __name__ == '__main__':
    app.run()
  









