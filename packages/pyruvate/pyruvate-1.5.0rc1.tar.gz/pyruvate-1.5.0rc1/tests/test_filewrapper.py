import pyruvate
import pytest
import os
import socket
from multiprocessing import Process
from tempfile import mkstemp
from time import sleep


def filewrapper_app(environ, start_response):
    fh, fname = mkstemp()
    os.write(fh, b'Hello world!\n')
    os.close(fh)
    fw = environ.get('wsgi.file_wrapper')
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', 5)]
    start_response(status, response_headers)
    return fw(open(fname))


def honour_blocksize_app(environ, start_response):
    fh, fname = mkstemp()
    os.write(fh, b'Hello world!\n')
    os.close(fh)
    fw = environ.get('wsgi.file_wrapper')
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'), ('Content-Length', 13)]
    start_response(status, response_headers)
    return fw(open(fname), 4)


@pytest.fixture
def one_worker_content_length(capsys):
    def srv():
        pyruvate.serve(
            filewrapper_app, '127.0.0.1:7878', 1, max_reuse_count=10)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


@pytest.fixture
def one_worker_blocksize(capsys):
    def srv():
        pyruvate.serve(
            honour_blocksize_app,
            '127.0.0.1:7878',
            1,
            max_reuse_count=10)
    p = Process(target=srv)
    yield p.start()
    p.terminate()


class TestFileWrapper(object):

    def _honour_content_length_header_sendfile(self, fixture):
        # we cannot rely on higher level modules/libraries
        # because they will not read beyond Content-Length
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
            s.sendall(b'GET / HTTP/1.1\r\n\r\n')
            data = b''
            while True:
                chunk = s.recv(1024)
                data += chunk
                if len(data) >= 108:
                    break
            assert data == b'HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nContent-Length: 5\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello'  # noqa: E501

    def _honour_blocksize_sendfile(self, fixture):
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
            s.sendall(b'GET / HTTP/1.1\r\n\r\n')
            data = b''
            while True:
                chunk = s.recv(1024)
                data += chunk
                if len(data) >= 117:
                    break
            assert data == b'HTTP/1.1 200 OK\r\nContent-type: text/plain\r\nContent-Length: 13\r\nVia: pyruvate\r\nConnection: keep-alive\r\n\r\nHello world!\n'  # noqa: E501

    def test_honour_content_length_header_sendfile(
            self, one_worker_content_length):
        self._honour_content_length_header_sendfile(
                one_worker_content_length)

    def test_honour_blocksize_sendfile(
            self, one_worker_blocksize):
        self._honour_blocksize_sendfile(one_worker_blocksize)
