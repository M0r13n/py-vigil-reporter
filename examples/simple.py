"""
py-vigil-reporter

Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""

from vigil_reporter.reporter import VigilReporter

if __name__ == "__main__":
    SAMPLE_CONFIG = {
        "url": "http://localhost:8080",
        "token": "REPLACE_THIS_WITH_A_SECRET_KEY",
        "probe_id": "stats",
        "node_id": "stats-node",
        "replica_id": "192.168.1.103",
        "interval": 5
    }
    reporter = VigilReporter.from_config(SAMPLE_CONFIG)
    reporter.start_reporting()
