import logging

import eventlet
import freezegun
import pytest
from unittest.mock import Mock

from nameko.testing.services import get_extension
from nameko.testing.utils import wait_for_call

from nameko_cron import ConcurrencyPolicy, Cron, cron


@pytest.fixture
def tracker():
    return Mock()


@pytest.mark.parametrize("timeout,concurrency,task_time,expected_calls", [
    # the cron schedule is set to spawn a worker every second
    (5, ConcurrencyPolicy.WAIT, 0, 5),    # a short-lived worker run at 0, 1, 2, 3, 4, 5
    (5, ConcurrencyPolicy.WAIT, 2, 3),    # a long-lived worker should fire at 0, 2, 4
    (5, ConcurrencyPolicy.ALLOW, 10, 5),   # if concurrency is permitted, new workers spawn alongside existing ones
    (5, ConcurrencyPolicy.SKIP, 1.5, 3),  # skipping should run at 0, 2, and 4
    (5, ConcurrencyPolicy.WAIT, 1.5, 4),  # run at 0, 1.5, 3, 4.5 (always behind)
])
def test_cron_runs(timeout, concurrency, task_time, expected_calls, container_factory, tracker):
    """Test running the cron main loop."""
    class Service(object):
        name = "service"

        @cron('* * * * * *', concurrency=concurrency)
        def tick(self):
            tracker()
            eventlet.sleep(task_time)

    container = container_factory(Service, {})

    # Check that Cron instance is initialized correctly
    instance = get_extension(container, Cron)
    assert instance.schedule == '* * * * * *'
    assert instance.tz is None
    assert instance.concurrency == concurrency

    with freezegun.freeze_time('2020-11-20 23:59:59.5', tick=True):
        container.start()
        eventlet.sleep(timeout)
        container.stop()

        assert tracker.call_count == expected_calls


@pytest.mark.parametrize("timezone,expected_first_interval_hours", [
    ("America/Chicago", 22),
    ("America/New_York", 21),
])
def test_timezone_aware_cron(timezone, expected_first_interval_hours):
    with freezegun.freeze_time('2020-11-20 08:00:00'):  # 2AM America/Chicago time (i.e. this is UTC)
        cron_extension = Cron('0 0 * * *', tz=timezone)
        next_interval = cron_extension._get_next_interval()
        assert next(next_interval) == expected_first_interval_hours*60*60
        assert next(next_interval) == expected_first_interval_hours*60*60 + 24*60*60


def test_kill_stops_cron(container_factory, tracker):

    class Service(object):
        name = "service"

        @cron('* * * * * *')
        def tick(self):
            tracker()

    container = container_factory(Service, {})
    container.start()

    with wait_for_call(2.0, tracker):
        container.kill()

    eventlet.sleep(2.0)
    assert tracker.call_count == 1


def test_stop_while_sleeping(container_factory, tracker):
    """Check that waiting for the cron to fire does not block the container
    from being shut down gracefully.
    """
    class Service(object):
        name = "service"

        @cron('* * * * * *')
        def tick(self):
            tracker()  # pragma: no cover

    container = container_factory(Service, {})
    container.start()

    # raise a Timeout if the container fails to stop within 1 second
    with eventlet.Timeout(1):
        container.stop()

    assert tracker.call_count == 0, 'Cron should not have fired.'


def test_timer_error(container_factory, caplog, tracker):
    """Check that an error in the decorated method does not cause the service
    containers loop to raise an exception.
    """

    class Service(object):
        name = "service"

        @cron('* * * * * *')
        def tick(self):
            tracker()

    tracker.side_effect = ValueError('Boom!')
    container = container_factory(Service, {})

    with caplog.at_level(logging.CRITICAL):
        container.start()
        eventlet.sleep(1.0)
        # Check that the function was actually called and that the error was
        # handled gracefully.
        assert tracker.call_count == 1
        container.stop()

    # Check that no errors are thrown in the runners thread.
    # We can't check for raised errors here as the actual
    # exception is eaten by the worker pools handler.
    assert len(caplog.records) == 0, (
        'Expected no errors to have been '
        'raised in the worker thread.'
    )
