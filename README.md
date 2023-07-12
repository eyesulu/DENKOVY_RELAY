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

##Usage
1. Update the denkovi.ini files with the necessary configuration settings for your Denkovi module, such as the IP address, port, OID template etc.

2. Run the app.py script to start the Flask web server:
```shell
python app.py
```

3. Access the web interface by navigating to http://localhost:5000 in your web browser.

4. Use the "Turn ON" and "Turn OFF" buttons to control the relay. The current state of the relay will be displayed on the page.

##Additional Information
The current version of the project is 1.0.0.

The script was written by Ghalam.


