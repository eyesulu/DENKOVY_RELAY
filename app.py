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
        oid = config.get("ADDRESS", "oid")
        power_off = config.get("ADDRESS", "power_off")
        power_on = config.get("ADDRESS", "power_on")
        
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
        status = relay_read_status(oid, board_ip, board_port, logger)
        current_state = 'ON' if status == power_on else 'OFF'
        return render_template('index.html', current_state=current_state, error_message=None)
    except Exception as e:
        error_message = "Failed to retrieve the initial state."
        logger.error(error_message)
        return render_template('index.html',board_ip=board_ip, board_port=board_port, current_state=None, error_message=error_message)

@app.route('/toggle', methods=['POST'])
def snmp_toggle():
    try:
        data = request.get_json()
        state = data['state']
        port = data.get('port', 1)  # Default to port 1 if 'port' key is not provided

        if state == 'on':
            relay_control(oid, power_on, board_ip, board_port, logger)
        elif state == 'off':
            relay_control(oid, power_off, board_ip, board_port, logger)

        # Read the status of the updated port
        status = relay_read_status(oid, board_ip, board_port, logger)
        current_state = 'ON' if status[0] == power_on else 'OFF'

        return jsonify({'currentState': current_state})

    except Exception as e:
        # Handle the exception and return an error message
        error_message = str(e)
        return jsonify({"error": error_message}), 500

@app.route("/get_state", methods=["GET"])
def get_state():
    try:
        status = relay_read_status(oid, board_ip, board_port, logger)
        byte_value = int(status[0][1])
        if byte_value == int(power_on, 16):
            current_state = "ON"
        elif byte_value == int(power_off, 16):
            current_state = "OFF"
        else:
            current_state = f"ERROR: unknown state ({byte_value})"
        return jsonify({"byteValue": byte_value, "currentState": current_state})
    except Exception as e:
        error_message = "Failed to retrieve the state."
        logger.error(error_message)
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run()









