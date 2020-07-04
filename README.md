# py-vigil-reporter

#### Vigil Reporter for Python. Used in pair with [Vigil](https://github.com/valeriansaliou/vigil), the Microservices Status Page.

# How to install
Install with pip:

```sh
$ pip install py-vigil-reporter
```


# How to use
`vigil-reporter` can be instantiated as such:

```py
SAMPLE_CONFIG = {
    "url": "http://localhost:8080",
    "token": "SOME_TOKEN",
    "probe_id": "web",
    "node_id": "web-node",
    "replica_id": "192.168.1.103",
    "interval": 10
}

reporter = VigilReporter.from_config(SAMPLE_CONFIG)
reporter.start_reporting()
```

This module uses the `threading.Timer` class from the `threading` module to run reporting in background. 
This makes the method non-blocking. 

**NOTE**: The threaded execution drifts about +/- 0.05 seconds. But this won't be an issue, as you should set an interval that is greater than 1.0 seconds.

For further details see this Stackoverflow [post](https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python).

# What is Vigil?
ℹ️ **Wondering what Vigil is?** Check out **[valeriansaliou/vigil](https://github.com/valeriansaliou/vigil)**.