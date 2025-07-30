# opsduty-python

> Command-line utility for interfacing with OpsDuty.

The `opsduty-python` library is built with two core features in mind:

- Command-line interface to interact with OpsDuty
- Programatic way to report heartbeat checkins in Python

## Help

See the [documentation](https://docs.opsduty.io/cli/) for more details.

## CLI

The `opsduty-python` package contains a CLI that can be used to interact with
OpsDuty.

The preferred way to install the CLI is to use `pipx install opsduty-python`.

```bash
$ opsduty
Usage: opsduty [OPTIONS] COMMAND [ARGS]...

Options:
  --log-format [json|logfmt|console]
                                  [default: console]
  --log-level [error|warning|info|debug]
                                  [default: info]
  --base-url TEXT                 Base URL for API requests to OpsDuty.
  --timeout INTEGER               API request timeout to OpsDuty.  [required]
  --access-token TEXT             Set the bearer token used to communicate
                                  with OpsDuty.  [env var:
                                  OPSDUTY_ACCESS_TOKEN]
  --version                       Show the version and exit.
  -h, --help                      Show this message and exit.

Commands:
  heartbeats  Commands for managing and monitoring heartbeats.
  schedules   Commands for accesing schedules.

  Command-line utility for interfacing with OpsDuty.
```

## Heartbeats

Send periodic heartbeats to OpsDuty using `opsduty-python`. The heartbeat needs
to be configured in OpsDuty before check-ins can be observed. Head over to
[https://opsduty.io](https://opsduty.io) to configure your heartbeats.

### Installation

Install using `pip install -U opsduty-python`.

### Alternative 1: Decorator

```python
from opsduty_python.heartbeats.heartbeats import (
    heartbeat_checkin,
)

@heartbeat_checkin(heartbeat="HBXXXX", environment="prod", enabled=True)
def periodic_job():
    pass
```

### Alternative 2: Send heartbeat manually.

```python
from opsduty_python.heartbeats.heartbeats import (
    send_heartbeat_checkin,
)

def periodic_job():
    try:
        pass
    except Exception:
        print("Job failed.")
    else:
        send_heartbeat_checkin(heartbeat="HBXXXX", environment="prod")
```
