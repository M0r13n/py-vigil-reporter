"""
py-vigil-reporter

Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""

import threading
import typing

import psutil
import requests
from requests.sessions import InvalidSchema


def get_cpu_usage() -> float:
    return round(psutil.cpu_percent(interval=None, percpu=False) / 100.0, 2)


def get_memory_usage() -> float:
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

        for slot in self.__slots__:
            if getattr(self, slot) is None:
                raise ValueError("%s must not be None!" % slot)

    @classmethod
    def from_config(cls, config: typing.Dict):
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
        url = "%s/reporter/%s/%s/" % (self.url, self.probe_id, self.node_id)
        return url

    def post_data(self, data: typing.Dict) -> requests.Response:
        try:
            response = requests.post(
                url=self.endpoint_url,
                auth=('Authorization', self.token),
                json=data,
            )
            return response
        except InvalidSchema as e:
            raise ValueError(
                "Invalid URL schema! Make sure that you provide a valid url, that starts with http://") from e

    def build_request_data(self) -> typing.Dict:
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
        return response.status_code == 200

    def report_in_thread(self) -> None:
        self.report()
        interval = self.interval
        threading.Timer(interval, self.report_in_thread).start()

    def start_reporting(self) -> None:
        self.report_in_thread()
