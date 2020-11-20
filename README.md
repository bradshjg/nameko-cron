# Nameko Cron

Nameko `Cron` entrypoint fires based on a cron expression. It is not cluster-aware and
will fire on all service instances. The cron schedule is based on [croniter](http://github.com/kiorky/croniter).

## Usage

```python
from nameko_cron import cron


class Service:
    name ="service"

    @cron('*/5 * * * *')
    def ping(self):
        # executes every 5 minutes
        print("pong")
```

timezone-aware cron schedules are also available

```python
from nameko_cron import cron


class Service:
    name ="service"

    @cron('0 12 * * *', tz='America/Chicago')
    def ping(self):
        # executes every day at noon America/Chicago time
        print("pong")
```
