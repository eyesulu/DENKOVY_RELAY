# Relay Control

This project provides a web-based interface to control a relay using SNMP and the Denkovi module. It allows you to turn the relay on and off through a user-friendly website.

## Requirements

- Python 3.x
- Flask
- PySNMP
- pyasn1==0.4.8

Please make sure you have the required Python packages installed. Note that the script requires `pyasn1` version 0.4.8 for successful operation. You can install the required packages using pip:

```shell
pip install Flask PySNMP pyasn1==0.4.8
```

Usage
Update the app.py and snmp_module.py files with the necessary configuration settings for your Denkovi module, such as the IP address, port, and OID template.

Run the app.py script to start the Flask web server:
```shell
python app.py
