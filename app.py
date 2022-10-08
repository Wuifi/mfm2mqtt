#!/usr/bin/env python3

self_description = """
mfm2mqtt is a tiny daemon written to fetch data from the mains frequency measurement head and
sends it to an mqtt-broker instance.
"""

# import standard modules
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import configparser
import logging
import os
import signal
import time
from datetime import datetime

# import 3rd party modules
from src.app_functions import *
from src.mfm_functions import *
from src.mqtt_functions import *
from src.basic_functions import *

__version__ = "0.0.2"
__version_date__ = "2022-10-08"
__description__ = "mfm2mqtt"
__license__ = "MIT"

# default vars
running = True
default_config = os.path.join(os.path.dirname(__file__), 'config.ini')
default_log_level = logging.INFO



def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    # parse command line arguments
    args = parse_args()
    # set logging
    log_level = logging.DEBUG if args.verbose is True else default_log_level
    if args.daemon:
        # omit time stamp if run in daemon mode
        logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s: %(message)s')
    # read config from ini file
    config = read_config(args.config_file)
    # set up influxdb handler
    influxdb_client = None
    try:
        #influxdb_client = influxdb.InfluxDBClient(
        #    config.get('influxdb', 'host'),
        #    config.getint('influxdb', 'port', fallback=8086),
        #    config.get('influxdb', 'username'),
        #    config.get('influxdb', 'password'),
        #    config.get('influxdb', 'database'),
        #    config.getboolean('influxdb', 'ssl', fallback=False),
        #    config.getboolean('influxdb', 'verify_ssl', fallback=False)
        #)
        #measurement_name=config.get('influxdb', 'measurement_name')
           
        # test more config options and see if they are present
        _ =config.get('mfm', 'SERIAL_PORT')
        _ =config.getint('mfm', 'interval')
        _ =config.get('mfm', 'location')
        _ =config.getint('mfm', 'zip_code')
        #_ = config.get('influxdb', 'measurement_name')
    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    except ValueError as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    # check influx db status
    #check_db_status(influxdb_client, config.get('influxdb', 'database'))

    # create authenticated gridradar-api client handler
    api_response = None
    #result_dict={}
    request_interval = 60
    try:
        request_interval = config.getint('mfm', 'interval', fallback=60)
        api_response, connection_ok=getdata(config)
 
    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    except BaseException as e:
        logging.error("Failed to connect to device  '%s'" % str(e))
        exit(1)

    # test connection
    try:
        connection_ok==True
    except Exception as e:
        #if "401" in str(e):
        #    logging.error("Failed to connect to device '%s' Check Board Connectivity!" %
        #                  config.get('kostal', 'username'))
        #if "404" in str(e):
        #    logging.error("Failed to connect to device '%s' using credentials. Check url!" %
        #                  config.get('kostal', 'url'))
        #else:
        logging.error(str(e))
        exit(1)

    logging.info("Successfully connected to device")
    # read services from config file
    ###services_to_query = get_services(config, "service")
    logging.info("Starting main loop - wait  '%s' seconds until first request!",request_interval)
    duration=0
    time.sleep(request_interval) # wait, otherwise Exception 429, 'Limitation: maximum number of requests per second exceeded']
        
    while running:
        logging.debug("Starting device requests")
        start = int(datetime.utcnow().timestamp() * 1000)
        api_response, connection_ok=getdata(config)
        #if connection_ok==True:
        convertraw2str(api_response)
        dict_output, state_flag=mfmstring2dict_P1(api_response)
        MQTT_msg=convert_to_mqtt_msg(dict_output,config)
        #else: 
        publish2mqtt(MQTT_msg,config)

        duration= int(datetime.utcnow().timestamp() * 1000) - start
        logging.debug("Duration of requesting and sending data : %0.3fs" % (duration / 1000)) 
    
        # just sleep for interval seconds - last run duration
        for _ in range(0, int(((request_interval * 1000) - duration) / 100)):
            if running is False:
                break
            time.sleep(0.0965)
            
            
if __name__ == "__main__":
    main()
