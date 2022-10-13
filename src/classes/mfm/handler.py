# -*- coding: utf-8 -*-
#
#  mfm2mqtt.py (same as fritzinfluxdb.py from the great work of
#  https://github.com/bb-Ricardo/fritzinfluxdb 
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import asyncio
import urllib3
import requests
from xml.etree.ElementTree import fromstring
import hashlib
import json

# import 3rd party modules
#from fritzconnection import FritzConnection
#from fritzconnection.core.exceptions import FritzConnectionException, FritzServiceError, FritzActionError

from src.classes.mfm.config import MFMConfig
from src.log import get_logger
from src.classes.mfm.service_handler import FritzBoxTR069Service, FritzBoxLuaService
from src.classes.fritzbox.services_tr069 import fritzbox_services as tr069_services
from src.classes.fritzbox.services_lua import fritzbox_services as lua_services
from src.classes.common import MFMMeasurement
from src.common import grab

log = get_logger()

class MFMHandlerBase:
    """
        base class to provide common methods to both handler classes
    """

    config = None
    session = None
    init_successful = False
    services = None
    discovery_done = False

    def __init__(self, config):
        if isinstance(config, MFMConfig):
            self.config = config
        else:
            self.config = MFMConfig(config)

        self.init_successful = False
        self.services = list()
        self.current_result_list = list()

        self.version = None

    def add_services(self, class_name, service_definition):
        """
        Adds services from config to handler

        Parameters
        ----------
        class_name: FritzBoxTR069Service, FritzBoxLuaService
            the fritzbox service class
        service_definition: list
            list of service definitions
        """

        for fritzbox_service in service_definition:
            new_service = class_name(fritzbox_service)

            # adjust request interval if necessary
            if self.config.request_interval > new_service.interval:
                new_service.interval = self.config.request_interval

            self.services.append(new_service)

    def query_service_data(self, _):
        # dummy service to make IDE happy
        pass

    async def task_loop(self, queue):
        """
        common task loop which is called in fritzinfluxdb.py

        Parameters
        ----------
        queue: asyncio.Queue
            the result queue object to write measurements to so the influx handler can pick them up

        """
        while True:

            self.current_result_list = list()
            for service in self.services:
                self.query_service_data(service)

            for result in self.current_result_list:
                log.debug(result)
                await queue.put(result)

            await asyncio.sleep(1)

            # first discovery run is done
            self.discovery_done = True


class MFMHandler(MFMHandlerBase):

    name = "Mains frequency Measurement Dev. Board"

    def __init__(self, config):

        super().__init__(config)

        # parse services from fritzbox/services_tr069.py
        #self.add_services(FritzBoxTR069Service, tr069_services)

    def connect(self):

        if self.init_successful is True:
            return

        log.debug(f"Initiating new {self.name} session")

        try:
            self.session = FritzConnection(
                address=self.config.hostname,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                timeout=(self.config.connect_timeout, self.config.connect_timeout * 4),
                use_tls=self.config.tls_enabled
            )

            self.version = self.session.system_version

        except BaseException as e:
            log.error(f"Failed to connect to Device '{e}'")
            return

        # test connection
        try:
            device_info = self.session.call_action("DeviceInfo", "GetInfo")
        except FritzConnectionException as e:
            if "401" in str(e):
                log.error(f"Failed to connect to {self.name} '{self.config.hostname}' using credentials. "
                          "Check username and password!")
            else:
                log.error(f"Failed to connect to {self.name} '{self.config.hostname}': {e}")

            return
        except BaseException as e:
            log.error(f"Failed to connect to {self.name} '{self.config.hostname}': {e}")
            return

        if isinstance(device_info, dict):
            self.config.model = device_info.get("NewModelName")
            self.config.fw_version = device_info.get("NewSoftwareVersion")

        log.info(f"Successfully established {self.name} session")

        self.init_successful = True

    def close(self):
        self.session.session.close()
        if self.init_successful is True:
            log.info(f"Closed {self.name} connection")

    def query_service_data(self, service):

        if not isinstance(service, FritzBoxTR069Service):
            log.error("Query service must be of type 'FritzBoxTR069Service'")
            return

        if self.discovery_done is True and service.should_be_requested() is False:
            return

        # Request every action
        for action in service.actions:

            if service.available is False:
                break

            if self.discovery_done is True and action.available is False:
                log.debug(f"Skipping disabled service action: {service.name} - {action.name}")
                continue

            # add parameters
            try:
                call_result = self.session.call_action(service.name, action.name, **action.params)
            except FritzServiceError:
                log.info(f"Requested invalid service: {service.name}")
                if self.discovery_done is False:
                    log.info(f"Querying service '{service.name}' will be disabled")
                    service.available = False
                continue
            except FritzActionError:
                log.info(f"Requested invalid action '{action.name}' for service: {service.name}")
                if self.discovery_done is False:
                    log.info(f"Querying action '{action.name}' will be disabled")
                    action.available = False
                continue
            except FritzConnectionException as e:
                if "401" in str(e):
                    log.error(f"Failed to connect to {self.name} '{self.config.hostname}' using credentials. "
                              "Check username and password!")
                else:
                    log.error(f"Failed to connect to {self.name} '{self.config.hostname}': {e}")
                continue
            except Exception as e:
                log.error(f"Unable to request {self.name} data: {e}")
                continue

            if call_result is None:
                continue

            log.debug(f"Request {self.name} service '{service.name}' returned successfully: "
                      f"{action.name} ({action.params})")

            # set time stamp of this query
            service.set_last_query_now()

            for key, value in call_result.items():
                log.debug(f"{self.name} result: {key} = {value}")
                metric_name = service.value_instances.get(key)

                if metric_name is not None:
                    self.current_result_list.append(
                        FritzMeasurement(metric_name, value, box_tag=self.config.box_tag)
                    )

        if self.discovery_done is False:
            if True not in [x.available for x in service.actions]:
                log.info(f"All actions for service '{service.name}' are unavailable. Disabling service.")
                service.available = False

        return