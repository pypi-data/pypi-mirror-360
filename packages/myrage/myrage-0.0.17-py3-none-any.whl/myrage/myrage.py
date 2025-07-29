"""Single responsibility module to define the Myrage class"""

import psutil
import time
import socket

from stem.process import launch_tor_with_config
from stem.control import Controller
from stem import Signal

from requests import Session
from requests.adapters import Retry, HTTPAdapter
from urllib3.connection import HTTPConnection

from myrage import (
    logger,
    CONTROL_PORT,
    SOCKS_PORT,
    GEO_IP_FILE,
    GEO_IP_V6_FILE,
    EXIT_NODES,
    STRICT_NODES,
    TOR_CMD_PATH,
    PROXIES,
    HEADERS,
)


class Myrage(Session):
    """Class that will start a Tor process with passed parameters
    IP address will be rolled when max requests will be reached

    Attributes: 
        request_counter (int): get and post requests counter
        max_requests (int): number of requests allowed per IP
        headers (dict): request headers
        proxies (dict): socket proxies
        ip_info (str): exit node ip
    """
    request_counter = 0
    max_requests = 100

    def __init__(
        self,
        control_port: int = CONTROL_PORT,
        socks_port: int = SOCKS_PORT,
        geo_ip_file: str = GEO_IP_FILE,
        geo_ip_v6_file: str = GEO_IP_V6_FILE,
        exit_nodes: str = EXIT_NODES,
        strict_nodes: int = STRICT_NODES,
        tor_cmd_path: str = TOR_CMD_PATH,
    ):

        self._control_port = CONTROL_PORT
        self._socks_port = SOCKS_PORT
        self._geo_ip_file = GEO_IP_FILE
        self._geo_ip_v6_file = GEO_IP_V6_FILE
        self._exit_nodes = EXIT_NODES
        self._strict_nodes = STRICT_NODES
        self._tor_cmd_path = TOR_CMD_PATH

        super().__init__()
        self.headers = HEADERS
        self.mount(
            "http://",
            adapter=HTTPAdapter(max_retries=Retry(total=10, backoff_factor=2)),
        )

    def get(self, *args, **kwargs):
        """Override get method to renew IP when max requests limit is reached
            *args: args from get request
            **kwargs: kwargs from get request

        Returns:
            get request response
        """
        self.request_counter += 1
        if self.request_counter == self.max_requests:
            self.renew_ip()
            self.request_counter = 0
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Override post method to renew IP when max requests limit is reached
            *args: args from post request
            **kwargs: kwargs from post request
        
        Returns:
            post request response
        """
        self.request_counter += 1
        if self.request_counter == self.max_requests:
            self.renew_ip()
            self.request_counter = 0
        return super().post(*args, **kwargs)

    def __configure_tor_session(
        self,
    ):
        """Configure Tor with passed or default parameters"""

        self._check_existing_tor_processes()
        self._tor_process = launch_tor_with_config(
            config={
                "ControlPort": str(self._control_port),
                "SocksPort": str(self._socks_port),
                "GeoIPFile": self._geo_ip_file,
                "GeoIPv6File": self._geo_ip_v6_file,
                "ExitNodes": self._exit_nodes,
                "StrictNodes": str(self._strict_nodes),
            },
            tor_cmd=self._tor_cmd_path,
            init_msg_handler=lambda line: logger.log.info(line),
        )
        self._controller = Controller.from_port(port=self._control_port)
        self._controller.authenticate()

        self.proxies = PROXIES


        r = self.get(r"http://ip-api.com/json")
        self.ip_info = r.json()
        logger.log.info(f"proxy info: {self.ip_info}")

    def get_locale_ip_info(self):
        """Store locale ip information"""
        r = Session().get("http://ip-api.com/json")
        return r.json()

    def get_ip_info(self):
        """Store information about the IP that will be used in the session"""
        r = self.get("http://ip-api.com/json")
        return r.json()

    def _check_existing_tor_processes(self):
        """Check and kill existing tor processes before starting one"""

        for proc in psutil.process_iter():
            try:
                if proc.name() == "tor":
                    # proc.kill()
                    logger.log.warning(
                        "Trying to terminate an already existing Tor process:"
                        f" process id: {proc.pid} - "
                        f"process name: {proc.name} - "
                        f"user: {proc.username()}"
                    )
                    proc.terminate()
                    break
            except psutil.NoSuchProcess as unknown_process_error:
                logger.log.warning(unknown_process_error)

    def renew_ip(self):
        """Renew IP """
        
        logger.log.info("Renewing tor IP")
        self._controller.signal(Signal.NEWNYM)
        time.sleep(1)
        r = self.get(r"http://ip-api.com/json")
        self.ip_info = r.json()
        logger.log.info(f"proxy info: {self.ip_info}")

    def __call__(self):

        """Launch tor configuration

        Returns:
            Configured instance
        """

        self.__configure_tor_session()

        return self


    def stop(self, kill: bool = False):
        """Stop Tor process

        Args:
            kill: kill the process if true otherwise terminate it
        """

        for proc in psutil.process_iter():
            if proc.name() == "tor":
                proc.terminate() if kill is False else proc.kill()

    def __del__(self):
        """Delete myrage controller and tor instances"""

        logger.log.info("Deleting myrage controller and tor instances")
        self._controller.close()
        self._tor_process.kill()
