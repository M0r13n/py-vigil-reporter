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
    return round(psutil.cpu_percent(interval=None, percpu=False) / 100.0, 2)


def get_memory_usage() -> float:
    return round(psutil.virtual_memory().percent / 100.0, 2)


def get_current_system_load() -> typing.Dict[str, float]:
    return dict(
        cpu=get_cpu_usage(),
        mem=get_memory_usage()
    )


class RequestFailedError(Exception):
    pass


class VigilReporter(object):
    __slots__ = (
        'url',
        'token',
        'probe_id',
        'node_id',
        'replica_id',
        'interval',
        '_stop'
    )

    def __init__(
            self,
            url: str,
            token: str,
            probe_id: str,
            node_id: str,
            replica_id: str,
            interval: float,
    ) -> None:
        self.url: str = url
        self.token: str = token
        self.probe_id: str = probe_id
        self.node_id: str = node_id
        self.replica_id: str = replica_id
        self.interval: float = interval
        self._stop: bool = False

        # prevent important values from beeing None
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

    def stop(self):
        """Stop reporting after next probe"""
        self._stop = True

    def _handle_vigil_response(self, response: requests.Response) -> bool:
        # Errors that are not recoverable, most likely due to a wrong config
        if 400 <= response.status_code < 500:
            raise RequestFailedError("Vigil responded with %i - Please check your config." % response.status_code)
        if response.status_code == 200:
            return True
        logger.error("Request FAILED: Vigil responded with %i" % response.status_code)
        return False

    def _make_request(self, data: typing.Dict) -> requests.Response:
        return requests.post(
            url=self.endpoint_url,
            auth=('Authorization', self.token),
            json=data,
        )

    def _post_data(self, data: typing.Dict) -> typing.Optional[requests.Response]:
        """
        Post the probe data and returns the requests.Response object on success.
        Connection errors are ignored because they are considered self recoverable.
        """
        try:
            response = self._make_request(data)
            return response
        except InvalidSchema as e:
            raise ValueError("Invalid URL schema! Make sure that you provide a valid url, that starts with http://") from e
        except requests.exceptions.ConnectionError:
            # Could not connect to Vigil. Possible reasons are: Network down, DNS down, Vigil down, Vigil busy, etc.
            # This error is considered recoverable. So VigilReporter should just try it again.
            logger.warning("%s is currently unreachable!" % self.endpoint_url)
            return None

    def build_report_payload(self, cpu: float, mem: float) -> typing.Dict:
        data = {
            "replica": self.replica_id,
            "interval": self.interval,
            "load": {
                "cpu": cpu,
                "ram": mem
            }
        }
        return data

    def send_single_report(self) -> bool:
        """
        Returns True if Vigil accepted the payload (returned a 2XX status code).
        Returns False if vigil could not be reached (temporary  error)
        An excpetion is raised if Vigil did not accept the payload
        """
        load_data = get_current_system_load()
        payload = self.build_report_payload(**load_data)
        response = self._post_data(payload)
        if response is not None:
            return self._handle_vigil_response(response)
        return False

    def report_in_thread(self) -> bool:
        """
        Sends a single report probe to Vigil and afterwards creates a new Timer for this function that will be executed in *interval* seconds.
        See: https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python

        Call .stop() in order to stop execution.
        """
        try:
            self.send_single_report()
        except RequestFailedError as e:
            raise e
        except Exception as unexpected_error:
            logger.error(unexpected_error)
            return False
        if not self._stop:
            threading.Timer(self.interval, self.report_in_thread).start()
        return True

    def start_reporting(self) -> None:
        """
        Start periodic reporting in background.
        """
        self.report_in_thread()
