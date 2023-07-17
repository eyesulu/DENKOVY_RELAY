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


def relay_control(oid, hex_value, board_ip, board_port, logger):
    try:
        value = int(hex_value, 16)
        if value < 0 or value > 255:
            logger.error("Invalid hex value. Must be between 00 and FF.")
            return
    except ValueError:
        logger.error("Invalid hex value. Must be a valid hexadecimal.")
        return

    snmpset(logger=logger, oid=oid, type="i", value=value, community="private", ip=board_ip, port=board_port)


def relay_read_status(oid, board_ip, board_port, logger):
    status = snmpget(logger, "private", board_ip, board_port, oid)
    return status


def main():
    parser = argparse.ArgumentParser(description='Denkovi python script')
    parser.add_argument("--logdir", type=str, help='Path to directory with the script logs.',
                        default="./logs/")  # change path to './logs/'
    parser.add_argument("--inifile", type=str, help='Path to config file.',
                        default="./denkovi.ini")  # change path to './denkovy.ini'
    parser.add_argument("--state", choices=["on", "off"], help='State to set the relay.')
    parser.add_argument("--read", action="store_true", help='Read the current state of the relay.')

    args = parser.parse_args()
    logdir = args.logdir
    inifile = args.inifile
    state = args.state
    read_state = args.read

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
            oid = config.get("ADDRESS", "oid")
            power_off = config.get("ADDRESS", "power_off")
            power_on = config.get("ADDRESS", "power_on")

        except Exception as e:
            logger.error("ERROR: Error reading ini file: %s", e)
            sys.exit(-1)
    else:
        logger.error("no inifile %s exists" % inifile)
        exit(1)

    if read_state:
        status = relay_read_status(oid, board_ip, board_port, logger)
        logger.info("Current state: {}".format(status))
        byte_value = int(status[0][1])
        if byte_value == int(power_on, 16):
            print("The power is ON")
        elif byte_value == int(power_off, 16):
            print("The power is OFF")
        else:
            print (status[0][1])
    elif state:
        if state == "on":
            relay_control(oid, power_on, board_ip, board_port, logger)
            logger.info("Relay turned ON")
        elif state == "off":
            relay_control(oid, power_off, board_ip, board_port, logger)
            logger.info("Relay turned OFF")
    else:
        logger.error("No action specified. Please provide either --state or --read.")

# just call the `main` function above
if __name__ == '__main__':
    main()


    
    
