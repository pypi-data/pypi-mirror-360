import socket
from cheroot import wsgi
from app import application

server = wsgi.Server(
    ('0.0.0.0', 9808),
    application
)

if __name__ == '__main__':
    try:
        server.start()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
