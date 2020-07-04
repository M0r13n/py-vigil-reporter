import unittest

from requests.models import Response

import vigil_reporter.reporter as r
from vigil_reporter.reporter import VigilReporter

SAMPLE_CONFIG = {
    "url": "http://localhost:8080",
    "token": "SOME_TOKEN",
    "probe_id": "web",
    "node_id": "web-node",
    "replica_id": "192.168.1.103",
    "interval": 10
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

    def test_data(self):
        r.get_cpu_usage = lambda: 0.55
        r.get_memory_usage = lambda: 0.12

        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        data = reporter.build_request_data()
        assert isinstance(data, dict)
        print(data)
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
        self.assertRaises(ValueError, lambda: reporter.post_data({}))

    def test_unreachable(self):
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        reporter.url = "http://blibblablub.com"
        assert reporter.post_data({}) is None

    def test_report(self):
        _original_function = r.VigilReporter.post_data
        always_true_response = Response()
        always_true_response.status_code = 200
        r.VigilReporter.post_data = lambda x, y: always_true_response
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        assert reporter.report()
        r.VigilReporter.post_data = _original_function

    def test_report_post_400_err(self):
        _original_function = r.VigilReporter.post_data
        fail_response = Response()
        fail_response.status_code = 403
        r.VigilReporter.post_data = lambda x, y: fail_response
        reporter = VigilReporter.from_config(SAMPLE_CONFIG)
        self.assertRaises(ValueError, lambda: reporter.report())
        r.VigilReporter.post_data = _original_function


if __name__ == "__main__":
    unittest.main()
