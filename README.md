# Denkovi Relay Control
## Introduction
This project allows you to control a Denkovi relay module via a command-line interface and provides a web interface to monitor and control the relay using a web browser.

## Prerequisites
- Python 3.X
- Flask library (version 1.1.2)
- PySNMP library (version 4.4.12)
- pyasn1 library (version 0.4.8)

Please make sure you have the required Python packages installed. Note that the script requires pyasn1 version 0.4.8 for successful operation.

## Command-Line Interface (CLI)

To control the relay via the command-line interface, use the denkovy_code.py script.

Command-Line Arguments
- --logdir (optional): Path to the directory where log files will be stored. Default is ./logs/.
- --inifile (optional): Path to the configuration file. Default is ./denkovy.ini.
- --state (optional): Show the current state of the relay.
- --control (optional): Control the relay (0 for OFF, 1 for ON).

Examples:

Show the current state of the relay:
```shell
python denkovy_code.py --state
```

Control the relay and switch it ON:
```shell
python denkovy_code.py --control 1
```

Control the relay and switch it OFF:
```shell
python denkovy_code.py --control 0
```

## Web Interface
To use the web interface, run the app.py script.

1. Make sure the Denkovi relay module is connected.

2. Update the denkovy.ini file with the appropriate configuration settings.

3. Run the following command to start the web server:
```shell
python app.py
```

The web interface provides buttons to turn the relay ON and OFF. The current state of the relay is displayed on the page.

## Version
Current version: 1.0.0
