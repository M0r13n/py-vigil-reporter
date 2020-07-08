"""
py-vigil-reporter

Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""

import time
import unittest

from requests.models import Response

import vigil_reporter.reporter as r
from vigil_reporter.reporter import RequestFailedError, VigilReporter, get_current_system_load

SAMPLE_CONFIG = {
    "url": "http://localhost:8080",
    "token": "SOME_TOKEN",
    "probe_id": "web",
    "node_id": "web-node",
    "replica_id": "192.168.1.103",
    "interval": 1
}


class VigilTestSuite(unittest.TestCase):
    """ Testcases for Vigil Reporter """

    def test_cpu(self):
        cpu = r.get_cpu_usage()
        # assert is float
        assert isinstance(cpu, float)
        # make sure it's between 0 and 1 (for vigil it could be > 1, but should be)
        assert 0.0 <= cpu <= 1.0

    def test_mem(self):
        mem = r.get_memory_usage()
        # assert is float
        assert isinstance(mem, float)
        # make sure it's between 0 and 1 (for vigil it could be > 1, but should be)
        assert 0.0 <= mem <= 1.0

    def test_from_config(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        assert isinstance(reporter, VigilReporter)
        assert reporter.url == SAMPLE_CONFIG["url"]
        assert reporter.token == SAMPLE_CONFIG["token"]
        assert reporter.probe_id == SAMPLE_CONFIG["probe_id"]
        assert reporter.node_id == SAMPLE_CONFIG["node_id"]
        assert reporter.replica_id == SAMPLE_CONFIG["replica_id"]
        assert reporter.interval == SAMPLE_CONFIG["interval"]

    def test_init_raise_error_if_none(self):
        # make sure all values are set when instantiating VigilReporter
        args = ("ABC",) * 5
        self.assertRaises(ValueError, lambda: VigilReporter(*args, None))

    def test_url(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        endpoint_url = reporter.endpoint_url
        assert endpoint_url == "http://localhost:8080/reporter/web/web-node/"

    def test_current_load(self):
        current_load = get_current_system_load()
        assert 0.0 <= current_load["cpu"] <= 1.0
        assert 0.0 <= current_load["mem"] <= 1.0

    def test_data(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        data = reporter.build_report_payload(0.55, 0.12)
        assert isinstance(data, dict)
        expected = {
            "replica": SAMPLE_CONFIG["replica_id"],
            "interval": SAMPLE_CONFIG["interval"],
            "load": {
                "cpu": 0.55,
                "ram": 0.12
            }
        }
        assert data == expected

    def test_invalid_url(self):
        url = "localhost:8080"
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        reporter.url = url
        self.assertRaises(ValueError, lambda: reporter._post_data({}))

    def test_unreachable(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        reporter.url = "http://blibblablubbbb.com"
        assert reporter._post_data({}) is None

    def test_report(self):
        _original_function = r.VigilReporter._post_data
        always_true_response = Response()
        always_true_response.status_code = 200
        r.VigilReporter._post_data = lambda x, y: always_true_response
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        assert reporter.send_single_report()
        r.VigilReporter._post_data = _original_function

    def test_report_post_400_err(self):
        _original_function = r.VigilReporter._post_data
        fail_response = Response()
        fail_response.status_code = 403
        r.VigilReporter._post_data = lambda x, y: fail_response
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        self.assertRaises(RequestFailedError, lambda: reporter.send_single_report())
        r.VigilReporter._post_data = _original_function

    def test_send_report_with_connection_err(self):
        _original_function = r.VigilReporter._post_data
        r.VigilReporter._post_data = lambda x, y: None
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        assert not reporter.send_single_report()
        r.VigilReporter._post_data = _original_function

    def test_response_handler(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        mock_response = Response()
        mock_response.status_code = 200
        assert reporter._handle_vigil_response(mock_response)

        mock_response.status_code = 201
        assert not reporter._handle_vigil_response(mock_response)

        mock_response.status_code = 301
        assert not reporter._handle_vigil_response(mock_response)

        mock_response.status_code = 400
        self.assertRaises(RequestFailedError, lambda: reporter._handle_vigil_response(mock_response))

        mock_response.status_code = 401
        self.assertRaises(RequestFailedError, lambda: reporter._handle_vigil_response(mock_response))

        mock_response.status_code = 404
        self.assertRaises(RequestFailedError, lambda: reporter._handle_vigil_response(mock_response))

    def test_stop_method(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        assert not reporter._stop

        reporter.stop()
        assert reporter._stop

    def test_thread(self):
        _original_function = r.VigilReporter._post_data
        always_true_response = Response()
        always_true_response.status_code = 200
        success_flag = [False, ]

        def return_true_and_set_flag(*args, success_flag=success_flag, **kwargs):
            success_flag[0] = True
            return always_true_response

        r.VigilReporter._post_data = return_true_and_set_flag

        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        reporter.interval = 0.1
        reporter.start_reporting()
        time.sleep(0.5)
        reporter.stop()
        assert reporter._stop
        assert all(success_flag)
        r.VigilReporter._post_data = _original_function

    def test_handle_unexpected_errors(self):
        _original_function = r.VigilReporter._post_data

        def error(*args, **kwargs):
            raise ValueError("Blaa")

        r.VigilReporter._post_data = error
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        reporter.stop()
        assert not reporter.report_in_thread()
        r.VigilReporter._post_data = _original_function


if __name__ == "__main__":
    unittest.main()
