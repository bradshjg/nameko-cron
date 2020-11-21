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

by default, if a worker takes longer than the next scheduled run the worker will wait until
the task is complete before immediately launching a new worker. This behavior can be controlled
via the ``concurrency`` keyword argument.

``ConcurrencyPolicy.WAIT`` is that default behavior.

``ConcurrencyPolicy.ALLOW`` will spawn a worker regardless of whether existing workers are still running.

``ConcurrencyPolicy.SKIP`` will skip a run if the previous worker lapsed the next scheduled run.
