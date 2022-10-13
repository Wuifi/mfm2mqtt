#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  mfm2mqtt.py (same as fritzinfluxdb.py from the great work of
#  https://github.com/bb-Ricardo/fritzinfluxdb 
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

self_description = """
mfm2mqtt is a tiny daemon written to fetch data from the mains frequency measurement head and
sends it to an mqtt-broker instance.
"""

# import standard modules
import os
import signal
import asyncio
import sys
#from http.client import HTTPConnection

#from argparse import ArgumentParser, RawDescriptionHelpFormatter
#import configparser
#import logging
#import os
#import signal
import time
from datetime import datetime

from src.cli_parser import parse_command_line
from src.log import setup_logging
from src.configparser import import_config
# import mfm-specific modules
from src.app_functions import *
from src.mfm_functions import *
from src.mqtt_functions import *
from src.basic_functions import *
from src.classes.mfm.handler import MFMHandler
from src.classes.influxdb.handler import InfluxHandler

__version__ = "0.0.3"
__version_date__ = "2022-10-13"
__description__ = "mfm2mqtt"
__license__ = "MIT"
__url__ = "https://github.com/Wuifi/mfm2mqtt"


# default vars
exit_code = 0
default_config = os.path.join(os.path.dirname(__file__), 'config.ini')


async def shutdown(shutdown_signal, loop, log):
    """Cleanup tasks tied to the service's shutdown."""
    log.info(f"Received exit signal {shutdown_signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for task in tasks:
        task.cancel()

    log.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def handle_task_result(task: asyncio.Task) -> None:
    global exit_code

    # noinspection PyBroadException
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Task cancellation should not be logged as an error.
    except Exception:
        import logging
        logging.exception('Exception raised by task = %r', task)

        # we kill ourself to shut down gracefully
        exit_code = 1
        os.kill(os.getpid(), signal.SIGTERM)








##############################################################

# default vars
running = True
default_config = os.path.join(os.path.dirname(__file__), 'config.ini')
#default_config = os.path.join('./config.ini')
default_log_level = logging.INFO


def main():
    
    # check for correct python version
    if sys.version_info[0] != 3 or sys.version_info[1] < 7:
        print("Error: Python version 3.7 or higher required!", file=sys.stderr)
        exit(1)

    # parse command line arguments
    args = parse_command_line(__version__, __description__, __version_date__, __url__, default_config)

    log = setup_logging("DEBUG" if args.verbose > 0 else "INFO", args.daemon)

    log.propagate = False

    log.info(f"Starting {__description__} v{__version__} ({__version_date__})")

    # read config from ini file
    config = import_config(args.config_file, default_config)


    # initialize handler
    influx_connection = InfluxHandler(config, user_agent=f"{__description__}/{__version__}")
    mqtt_connection = MqttHandler(config)
    mfm_connection = MFMHandler(config)
    mfm_v2_connection = MFMV2Handler(mfm_connection.config)

    handler_list = [
        influx_connection,
        mqtt_connection
        mfm_connection,
        mfm_v2_connection
#        fritzbox_lua_connection
    ]

    for handler in handler_list:
        if handler.config.parser_error is True:
            exit(1)

    log.info("Successfully parsed config")

    # try:
    #     # test more config options and see if they are present
    #     _ = config.get('mfm', 'SERIAL_PORT')
    #     _ = config.getint('mfm', 'interval')
    #     _ = config.get('mfm', 'location')
    #     _ = config.getint('mfm', 'zip_code')

    #     #_ = config.get('influxdb', 'measurement_name')
    # except configparser.Error as e:
    #     logging.error("Config Error: %s", str(e))
    #     exit(1)
    # except ValueError as e:
    #     logging.error("Config Error: %s", str(e))
    #     exit(1)
    # # check influx db status
    # #check_db_status(influxdb_client, config.get('influxdb', 'database'))


    # init connection on all handlers
    influx_connection.connect()
    mqtt_connection.connect()
    mfm_connection.connect()

    # handler for extended protocol is only useful with  FW >= 2.X
    if mfm_connection.config.fw_version is not None and mfm_connection.config.fw_version[0] == "2":
        mfm_v2_connection.connect()
    else:
        log.info("Disabling queries via extended protocol. version must be at least 2.XX")
        handler_list.remove(mfm_v2_connection)

    init_errors = False
    for handler in handler_list:
        if handler.init_successful is False:
            log.error(f"Initializing connection to {handler.name} failed")
            init_errors = True

    if init_errors is True:
        exit(1)

    log.info(f"Successfully connected to device '{mfm_connection.config.serial_port}' "
             f"({mfm_connection.config.box_tag}) Model: {mfm_connection.config.model} - "
             f"FW: {mfm_connection.config.fw_version}")

    loop = asyncio.get_event_loop()

    for fb_signal in [signal.SIGHUP, signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(
            fb_signal, lambda s=fb_signal: asyncio.create_task(shutdown(s, loop, log)))

    queue = asyncio.Queue()

    log.info("Starting main loop")

    try:
        for handler in handler_list:
            task = loop.create_task(handler.task_loop(queue))
            task.add_done_callback(handle_task_result)
        loop.run_forever()
    finally:
        loop.close()
        influx_connection.close()
        mqtt_connection.close()
        mfm_connection.close()
        log.info(f"Successfully shutdown {__description__}")

    exit(exit_code)


if __name__ == "__main__":
    main()


#     # create authenticated mfm client handler
#     rawdata = None
#     connection_ok = 0
#     MFMprotocol = 0
#     #result_dict={}
#     request_interval = 1
#     try:
#         request_interval = config.getint('mfm', 'interval', fallback=1)
#         mfm_port = config.get('mfm', 'SERIAL_PORT')
#         rawdata , connection_ok = MFMgetrawdata(mfm_port)
#         if connection_ok == 1:
#             logging.info("Serial communication to device OK")
#             rawdata , connection_ok = MFMgetrawdata(mfm_port)
#             string=str(rawdata, 'UTF-8')
#             MFMprotocol= MFMprotocol(list)
            
#             if MFMprotocol != 0:
#                 logging.info("MFMprotocol: V%s detected",str(MFMprotocol))
#             else: 
#                 logging.error("MFMprotocol: could not be detected with input :%s ",str(list))
#         else:
#             logging.error("Serial communication to device Failed")
            
#     except configparser.Error as e:
#         logging.error("Config Error: %s", str(e))
#         exit(1)
#     except BaseException as e:
#         logging.error("Failed to connect to device  '%s'" % str(e))
#         exit(1)



#     # starting main routine

#     logging.info("Starting main loop - wait  '%s' seconds until first request!",request_interval)
#     duration = 0
#     time.sleep(request_interval) # wait, otherwise Exception 429, 'Limitation: maximum number of requests per second exceeded']
        
#     while running:
#         logging.debug("Starting device requests")
#         start = int(datetime.utcnow().timestamp() * 1000)
#         try:
#             rawdata, connection_ok = MFMgetrawdata(mfm_port)
            
#             if (connection_ok == 1):   
#                 string = str(rawdata, 'UTF-8')
#                 string = string.replace('\r\n','')
#                 list = string.split(";")
#                 valid = MFMmonitor(list)
                
#                 if (valid == 1):
#                     if (MFMprotocol == 1):
#                         string, raw2str_ok = convertraw2str_P1(rawdata)  
#                         dict_meas, dict_mon, state_flag = MFMstring2dict_P1(string)  
                                                    
#                     elif (MFMprotocol == 4):
#                         dict_meas, dict_mon, state_flag = MFMlist2dict_P4(list)

#                     MQTT_msg=convert_to_mqtt_msg(dict_meas,config)
#                     publish2mqtt(MQTT_msg,config)
#                     MQTT_msg=convert_to_mqtt_msg(dict_mon,config)
#                     publish2mqtt(MQTT_msg,config)
                    

#             duration= int(datetime.utcnow().timestamp() * 1000) - start
#             logging.debug("Duration of requesting and sending data : %0.3fs" % (duration / 1000)) 
#         except BaseException as e:
#             logging.error("Failed to connect to device  '%s'" % str(e))
#             exit(1)    
#             # just sleep for interval seconds - last run duration
#         for _ in range(0, int(((request_interval * 1000) - duration) / 100)):
#             if running is False:
#                 break
#             time.sleep(0.0965)
            
            
# if __name__ == "__main__":
#     main()
