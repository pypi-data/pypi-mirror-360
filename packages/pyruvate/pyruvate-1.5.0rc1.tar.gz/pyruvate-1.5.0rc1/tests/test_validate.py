import pyruvate
import pytest
import requests
from multiprocessing import Process
from wsgiref.validate import validator
from time import sleep
from urllib3.exceptions import NewConnectionError


HELLO_WORLD = b"<html><body><h1>Hello world!</h1></body></html>\n"


def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return [HELLO_WORLD]


@pytest.fixture
def one_worker(capsys):
    vldt = validator(simple_app)

    def srv():
        pyruvate.serve(vldt, '127.0.0.1:7878', 1)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


class TestPyruvate(object):

    def _pyruvate_serve(self, fixture):
        while True:
            tries = 0
            try:
                got = requests.get('http://localhost:7878/')
                break
            except (
                    ConnectionRefusedError,
                    NewConnectionError,
                    requests.exceptions.ConnectionError):
                if tries == 5:
                    raise
                tries += 1
                sleep(1)
        assert got.ok
        assert got.status_code == 200
        assert got.content == b'<html><body><h1>Hello world!</h1></body></html>\n'  # noqa: E501
        assert got.headers['Content-type'] == 'text/html'

    def test_serve(self, one_worker):
        self._pyruvate_serve(one_worker)
