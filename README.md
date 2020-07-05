# py-vigil-reporter
[![PyPI](https://img.shields.io/pypi/v/py-vigil-reporter)](https://pypi.org/project/py-vigil-reporter/)
[![license](https://img.shields.io/pypi/l/py-vigil-reporter)](https://github.com/M0r13n/py-vigil-reporter/blob/master/LICENSE)
[![codecov](https://codecov.io/gh/M0r13n/py-vigil-reporter/branch/master/graph/badge.svg)](https://codecov.io/gh/M0r13n/py-vigil-reporter)
[![downloads](https://img.shields.io/pypi/dm/py-vigil-reporter)](https://pypi.org/project/py-vigil-reporter/)

#### Vigil Reporter for Python. Used in pair with [Vigil](https://github.com/valeriansaliou/vigil), the Microservices Status Page.


## Who uses it?

<table>
<tr>
<td align="center"><a href="https://smartphoniker.shop/"><img src="https://smartphoniker.shop/static/images/smartphoniker-logo.svg" height="64" /></a></td>
</tr>
<tr>
<td align="center">Smartphoniker</td>
</tr>
</table>



# How to install
Install with pip:

```sh
$ pip install py-vigil-reporter
```


# How to use
`vigil-reporter` can be instantiated as such:

```py
from vigil_reporter.reporter import VigilReporter

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
print("You can continue with your normal work here!")
```

This module uses the `threading.Timer` class from the `threading` module to run reporting in background. 
This makes the method non-blocking. 

**NOTE**: The threaded execution drifts about +/- 0.05 seconds. But this won't be an issue, as you should set an interval that is greater than 1.0 seconds.

For further details see this Stackoverflow [post](https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python).

# What is Vigil?
ℹ️ **Wondering what Vigil is?** Check out **[valeriansaliou/vigil](https://github.com/valeriansaliou/vigil)**.
