import pyruvate
import pytest
import requests
import socket
from multiprocessing import Process
from time import sleep
from urllib3.exceptions import NewConnectionError


def dummy_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'OK']


def latin1_url_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [bytes(environ['PATH_INFO'], encoding='latin-1')]


def long_header_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [bytes(environ['HTTP_FOO'], encoding='ascii')]


@pytest.fixture
def dummy(capsys):
    def srv():
        pyruvate.serve(dummy_app, '127.0.0.1:7878', 1)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


@pytest.fixture
def latin1(capsys):
    def srv():
        pyruvate.serve(latin1_url_app, '127.0.0.1:7878', 1)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


@pytest.fixture
def long_header(capsys):

    def srv():
        pyruvate.serve(long_header_app, '127.0.0.1:7878', 1)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


@pytest.fixture
def content_length_wrong(capsys):

    def content_length_wrong_app(environ, start_response):
        status = '200 OK'
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', '42')]
        start_response(status, response_headers)
        return [b'Hello world!\n']

    def srv():
        pyruvate.serve(content_length_wrong_app, '127.0.0.1:7878', 1)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


class TestHeaders(object):

    def _get_long_header(self):
        long_header = b'Foo42' * 65353
        tries = 0
        while True:
            try:
                got = requests.get(
                    'http://localhost:7878/', headers={'Foo': long_header})
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
        assert got.content == long_header  # noqa: E501
        assert got.headers['Content-type'] == 'text/plain'

    def _get_latin1_url(self):
        tries = 0
        while True:
            try:
                got = requests.get('http://localhost:7878/f%C3%A4%C3%A4')
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
        assert got.content == b'/f\xc3\xa4\xc3\xa4'

    def test_long_header(self, long_header):
        self._get_long_header()

    def test_latin1_url(self, latin1):
        self._get_latin1_url()

    def _expect_continue(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            tries = 0
            while True:
                try:
                    s.connect(('127.0.0.1', 7878))
                    break
                except ConnectionRefusedError:
                    if tries == 5:
                        raise
                    tries += 1
                    sleep(1)
            s.sendall(b'POST / HTTP/1.1\r\nContent-Length: 1603\r\nContent-Type: application/x-www-form-urlencoded\r\nExpect: 100-continue\r\n\r\n')  # noqa: E501
            data = b''
            while True:
                chunk = s.recv(1024)
                data += chunk
                if len(data) >= 16:
                    break
            assert data == b'HTTP/1.1 100 Continue\r\n\r\n'  # noqa: E501
            s.sendall(b'B' * 1603)
            data = b''
            while True:
                chunk = s.recv(1024)
                data += chunk
                if len(data) >= 16:
                    break
            assert data == b'HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nVia: pyruvate\r\nConnection: close\r\n\r\nOK'  # noqa: E501

    def test_expect_continue(self, dummy):
        self._expect_continue()

    def test_content_length_wrong(self, content_length_wrong):
        try:
            tries = 0
            while True:
                try:
                    requests.get('http://localhost:7878/')
                    break
                except (
                        ConnectionRefusedError,
                        NewConnectionError,
                        requests.exceptions.ConnectionError):
                    if tries == 5:
                        raise
                    tries += 1
                    sleep(1)
        except requests.exceptions.ChunkedEncodingError as e:
            incomplete_read = e.args[0].args[1]
            assert incomplete_read.expected == 29
            assert incomplete_read.partial == 13
