"""
py-vigil-reporter

Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""

import logging
import threading
import typing

import psutil
import requests
from requests.sessions import InvalidSchema

logger = logging.getLogger(__name__)


def get_cpu_usage() -> float:
    """
    Get total CPU usage
    """
    return round(psutil.cpu_percent(interval=None, percpu=False) / 100.0, 2)


def get_memory_usage() -> float:
    """
    Get total memory usage
    """
    return round(psutil.virtual_memory().percent / 100.0, 2)


class VigilReporter(object):
    __slots__ = (
        'url',
        'token',
        'probe_id',
        'node_id',
        'replica_id',
        'interval'
    )

    def __init__(
            self,
            url: str,
            token: str,
            probe_id: str,
            node_id: str,
            replica_id: str,
            interval: float
    ) -> None:
        self.url = url
        self.token = token
        self.probe_id = probe_id
        self.node_id = node_id
        self.replica_id = replica_id
        self.interval = interval

        # assert that all values are set
        for slot in self.__slots__:
            if getattr(self, slot) is None:
                raise ValueError("%s must not be None!" % slot)

    @classmethod
    def from_config(cls, config: typing.Dict):
        """
        Create a new VigilReporter instance from a dict object.
        """
        return cls(
            config['url'],
            config['token'],
            config['probe_id'],
            config['node_id'],
            config['replica_id'],
            config['interval'],
        )

    @property
    def endpoint_url(self) -> str:
        """
        Returns the fully build endpoint url for vigil.
        """
        url = "%s/reporter/%s/%s/" % (self.url, self.probe_id, self.node_id)
        return url

    def post_data(self, data: typing.Dict) -> typing.Optional[requests.Response]:
        """
        Post the probe data and returns the requests.Response object on success.

        Connection errors are ignored because they are considered self recoverable.
        """
        try:
            response = requests.post(
                url=self.endpoint_url,
                auth=('Authorization', self.token),
                json=data,
            )
            return response
        except InvalidSchema as e:
            raise ValueError("Invalid URL schema! Make sure that you provide a valid url, that starts with http://") from e
        except requests.exceptions.ConnectionError:
            # this might happen for various reasons and SHOULD NOT kill the service permanently.
            logger.warning("%s is currently unreachable!" % self.endpoint_url)
            return None

    def build_request_data(self) -> typing.Dict:
        """
        Construct the probe object as a dict that will be send to Vigil.
        """
        cpu = get_cpu_usage()
        mem = get_memory_usage()
        data = {
            "replica": self.replica_id,
            "interval": self.interval,
            "load": {
                "cpu": cpu,
                "ram": mem
            }
        }
        return data

    def report(self) -> bool:
        data = self.build_request_data()
        response = self.post_data(data)
        try:
            if response.status_code == 200:
                return True
            else:
                raise ValueError("Server responded with: %s : %s\nGiving up permanently." % (response.status_code, response.text))
        except AttributeError:
            # response was most likely None
            return False

    def report_in_thread(self) -> None:
        """
        Send a report Probe.
        Afterwards create a new Timer that will be executed in interval seconds.
        See: https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python
        """
        self.report()
        interval = self.interval
        threading.Timer(interval, self.report_in_thread).start()

    def start_reporting(self) -> None:
        """
        Start periodic reporting in background.

        If an excpetion is raised on first call, the main thread will be terminated.
        """
        self.report_in_thread()
