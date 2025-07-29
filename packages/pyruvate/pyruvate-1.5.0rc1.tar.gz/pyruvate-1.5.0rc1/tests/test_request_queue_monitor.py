import aiohttp
import asyncio
import logging
import logging.handlers
import pyruvate
import pytest
import queue
import multiprocessing
import multiprocessing.connection
from time import sleep


def dummy_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    sleep(.3)
    start_response(status, response_headers)
    return [b'OK']


queued_log = multiprocessing.Queue()


@pytest.fixture
def rq_monitor_fixture(caplog):
    def srv(logs):
        h = logging.handlers.QueueHandler(logs)
        root = logging.getLogger()
        root.addHandler(h)
        root.setLevel(logging.WARN)
        pyruvate.serve(
            dummy_app, '127.0.0.1:7878', 1, qmon_warn_threshold=2)
    p = multiprocessing.Process(target=srv, args=(queued_log, ))
    yield p.start()
    p.join(2)
    p.terminate()


class TestRequestQueueMonitor(object):

    async def _get_response(self, session, url):
        async with session.get('http://localhost:7878/') as resp:
            assert resp.ok
            assert resp.status == 200
            assert resp.headers['Content-type'] == 'text/plain'
            got = await resp.text()
            assert got == 'OK'

    @pytest.mark.asyncio
    async def test_queue_monitor(self, rq_monitor_fixture):
        """ Produce concurrent requests
        """
        url = 'http://localhost:7878/'
        async with aiohttp.ClientSession() as session:
            resps = []
            for rd in range(5):
                resps.append(
                    asyncio.ensure_future(self._get_response(session, url)))
            await asyncio.gather(*resps)
        record_count = 0
        while True:
            try:
                record = queued_log.get_nowait()
                record_count += 1
                assert record.levelno == logging.WARN
                assert 'requests in queue' in record.message
                assert record.name == 'pyruvate'
            except queue.Empty:
                break
        assert record_count > 0
