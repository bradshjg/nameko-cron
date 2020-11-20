import datetime
import time
from logging import getLogger

from croniter import croniter
from eventlet import Timeout
from eventlet.event import Event
import pytz

from nameko.extensions import Entrypoint


_log = getLogger(__name__)


class Cron(Entrypoint):
    def __init__(self, schedule, tz=None, **kwargs):
        """
        Cron entrypoint. Fires according to a (possibly timezone-aware)
        cron schedule. If no timezone info is passed, the default is UTC.

        Example::

            class Service(object):
                name = "service"

            @cron(schedule='0 12 * * *', tz='America/Chicago')
            def ping(self):
                # method executes every day at noon America/Chicago time
                print("pong")

        """
        self.schedule = schedule
        self.tz = tz
        self.should_stop = Event()
        self.worker_complete = Event()
        self.gt = None
        super().__init__(**kwargs)

    def start(self):
        _log.debug('starting %s', self)
        self.gt = self.container.spawn_managed_thread(self._run)

    def stop(self):
        _log.debug('stopping %s', self)
        self.should_stop.send(True)
        self.gt.wait()

    def kill(self):
        _log.debug('killing %s', self)
        self.gt.kill()

    def _get_next_interval(self):
        now_utc = datetime.datetime.now(tz=pytz.UTC)
        if self.tz:
            tz = pytz.timezone(self.tz)
            base = now_utc.astimezone(tz)
        else:
            base = now_utc
        cron_schedule = croniter(self.schedule, base)
        while True:
            yield max(cron_schedule.get_next() - time.time(), 0)

    def _run(self):
        """ Runs the schedule loop. """
        interval = self._get_next_interval()
        sleep_time = next(interval)
        while True:
            # sleep for `sleep_time`, unless `should_stop` fires, in which
            # case we leave the while loop and stop entirely
            with Timeout(sleep_time, exception=False):
                self.should_stop.wait()
                break

            self.handle_timer_tick()

            self.worker_complete.wait()
            self.worker_complete.reset()

            sleep_time = next(interval)

    def handle_timer_tick(self):
        args = ()
        kwargs = {}

        # Note that we don't catch ContainerBeingKilled here. If that's raised,
        # there is nothing for us to do anyway. The exception bubbles, and is
        # caught by :meth:`Container._handle_thread_exited`, though the
        # triggered `kill` is a no-op, since the container is already
        # `_being_killed`.
        self.container.spawn_worker(
            self, args, kwargs, handle_result=self.handle_result)

    def handle_result(self, worker_ctx, result, exc_info):
        self.worker_complete.send()
        return result, exc_info


cron = Cron.decorator
