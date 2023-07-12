#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:33:41 2023

@author: aisulu
"""

from pysnmp.hlapi import *
import logging
import argparse
import os
from datetime import date
import configparser
import sys


def snmpget(logger, community, ip, port, oid):
    error_indication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )

    if error_indication:
        logger.error(error_indication)
        raise ValueError
    elif errorStatus:
        logger.error('%s at %s' % (errorStatus.prettyPrint(),
                                   errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        raise ValueError
    else:
        for name, val in varBinds:
            logger.debug("{} = {}".format(name, val))
        return varBinds


def snmpset(logger, community, ip, port, oid, type, value):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid), OctetString(value) if type == 's' else Integer(value)))
    )

    if errorIndication:
        print(errorIndication)
        raise ValueError
    elif errorStatus:
        logger.error('%s at %s' % (errorStatus.prettyPrint(),
                                   errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        raise ValueError
    else:
        for name, val in varBinds:
            logger.info("{} = {}".format(oid, val))
            return oid, val


def relay_control(relay_id_template, r_id, value, board_ip, board_port, logger):
    relay_id = relay_id_template.replace("X", str(r_id))
    relay_id_tuple = tuple(map(int,relay_id.split(".")[1:][:-1]))
    snmpset(logger=logger, oid=relay_id_tuple, type="i", value=value, community="private", ip=board_ip, port=board_port)


def relay_reset(relay_id_template, board_ip, board_port, logger):
    value = 0
    for i in range(1, 9):
        relay_id = relay_id_template.replace("X", str(i))
        relay_id_tuple = tuple(map(int,relay_id.split(".")[1:][:-1]))
        snmpset(logger=logger, oid=relay_id_tuple, type="i", value=value, community="private", ip=board_ip, port=board_port)


def relay_read_status(relay_id_template, r_id, board_ip, board_port, logger):
    relay_id = relay_id_template.replace("X", str(r_id))
    relay_id_tuple = tuple(map(int,relay_id.split(".")[1:][:-1]))
    logger.debug(relay_id_tuple)
    logger.debug(board_ip)
    status = snmpget(logger, "private", board_ip, board_port, relay_id_tuple)
    return status


def main():
    parser = argparse.ArgumentParser(description='Denkovi python script')
    parser.add_argument("--logdir", type=str, help='Path to directory with the script logs.',
                        default="./logs/")  # change path to './logs/'
    parser.add_argument("--inifile", type=str, help='Path to config file.',
                        default="./denkovi.ini")  # change path to './denkovy.ini'
    parser.add_argument("--state", action='store_true', help='Show current state of the relay.')
    parser.add_argument("--control", type=int, help='Control the relay (0 for OFF, 1 for ON).')

    args = parser.parse_args()
    logdir = args.logdir
    inifile = args.inifile
    show_state = args.state
    control_state = args.control

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

    config = configparser.ConfigParser()
    if os.path.isfile(inifile):
        try:
            config.read(inifile)
            board_ip = config.get("ADDRESS", "ip")
            board_port = config.get("ADDRESS", "port")
            relay_id_template = config.get("ADDRESS", "relay_oid_template")
            r_id = config.get("ADDRESS", "r_id_1")  # Define r_id

        except Exception as e:
            logger.error("ERROR: Error reading ini file: %s", e)
            sys.exit(-1)
    else:
        logger.error("no inifile %s exists" % inifile)
        exit(1)

    r_id = int(r_id)  # Convert r_id to integer

    try:
        status = relay_read_status(relay_id_template, r_id, board_ip, board_port, logger)
        if status[0][1] == 1:
            current_state = 'ON'
        else:
            current_state = 'OFF'
        logger.info('Current state: %s' % current_state)

    except Exception as e:
        logger.error("Failed to connect to Denkovi module. Check the network connection and ensure the Denkovi module is accessible.")
        sys.exit(-1)

    if show_state:
        print('Current state:', current_state)

    if control_state is not None:
        if control_state == 1:
            logger.info("Switching relay ON")
            relay_control(relay_id_template, r_id, 1, board_ip, board_port, logger)
        elif control_state == 0:
            logger.info("Switching relay OFF")
            relay_control(relay_id_template, r_id, 0, board_ip, board_port, logger)
        else:
            logger.error("Invalid control state provided. Reverting to OFF.")
            relay_control(relay_id_template, r_id, 0, board_ip, board_port, logger)

# just call the `main` function above
if __name__ == '__main__':
    main()


    
    
