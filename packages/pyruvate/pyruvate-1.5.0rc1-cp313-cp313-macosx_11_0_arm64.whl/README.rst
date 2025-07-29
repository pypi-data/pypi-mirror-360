Pyruvate WSGI server
====================

.. image:: https://gitlab.com/tschorr/pyruvate/badges/main/pipeline.svg
   :target: https://gitlab.com/tschorr/pyruvate

.. image:: https://codecov.io/gl/tschorr/pyruvate/branch/main/graph/badge.svg
   :target: https://codecov.io/gl/tschorr/pyruvate

.. image:: http://img.shields.io/pypi/v/pyruvate.svg
   :target: https://pypi.org/project/pyruvate

Pyruvate is a fast, multithreaded `WSGI <https://www.python.org/dev/peps/pep-3333>`_ server implemented in `Rust <https://www.rust-lang.org/>`_.
It is implementing a pre-fork worker model, making it a good choice for applications that are not completely thread safe or maintain per thread objects that are expensive to create (e.g. pooled database connections).

Features
--------

* Non-blocking read/write using `mio <https://github.com/tokio-rs/mio>`_
* Request parsing using `httparse <https://github.com/seanmonstar/httparse>`_
* `pyo3-ffi <https://github.com/pyo3/pyo3>`_ based Python interface
* Worker pool based on `threadpool <https://github.com/rust-threadpool/rust-threadpool>`_
* `PasteDeploy <https://pastedeploy.readthedocs.io/en/latest/>`_ entry point

Installation
------------

If you are on Linux and use a recent Python version,

.. code-block::

    $ pip install pyruvate

is probably all you need to do.

Binary Packages
+++++++++++++++

`manylinux_2_28 <https://peps.python.org/pep-0600/>`_ and `musllinux_1_2 <https://peps.python.org/pep-0656/>`_ wheels are available for the `x86_64` architecture and active Python 3 versions (currently 3.9-3.13).

Source Installation
+++++++++++++++++++

On macOS or if for any other reason you want to install the source tarball (e.g. using `pip install --no-binary`) you will need to `install Rust <https://doc.rust-lang.org/book/ch01-01-installation.html>`_ first.
Then you will need to switch to Rust Nightly::

    $ rustup install nightly
    $ rustup default nightly

Development Installation
++++++++++++++++++++++++

* Install `Rust <https://doc.rust-lang.org/book/ch01-01-installation.html>`__
* Install Rust Nightly Toolchain and make it the default::

    $ rustup install nightly
    $ rustup default nightly

* Install and activate a Python 3 (>= 3.9) `virtualenv <https://docs.python.org/3/tutorial/venv.html>`_
* Install `maturin <https://www.maturin.rs/>`_ using pip::

    $ pip install maturin

* Clone Pyruvate with git and cd into your copy::

    $ git clone https://gitlab.com/tschorr/pyruvate.git
    $ cd pyruvate

* Install Pyruvate as editable::

    $ maturin develop

Using Pyruvate in your WSGI application
---------------------------------------

From Python using a TCP port
++++++++++++++++++++++++++++

A hello world WSGI application using Pyruvate listening on 127.0.0.1:7878 and using 2 worker threads looks like this:

.. code-block:: python

    import pyruvate

    def application(environ, start_response):
        """Simplest possible application object"""
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers, None)
        return [b"Hello world!\n"]

    pyruvate.serve(application, "127.0.0.1:7878", 2)

From Python using a Unix socket
+++++++++++++++++++++++++++++++

A hello world WSGI application using Pyruvate listening on unix:/tmp/pyruvate.socket and using 2 worker threads looks like this:

.. code-block:: python

    import pyruvate

    def application(environ, start_response):
        """Simplest possible application object"""
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers, None)
        return [b"Hello world!\n"]

    pyruvate.serve(application, "/tmp/pyruvate.socket", 2)

Using PasteDeploy
+++++++++++++++++

Again listening on 127.0.0.1:7878 and using 2 worker threads::

    [server:main]
    use = egg:pyruvate#main
    socket = 127.0.0.1:7878
    workers = 2

Configuration Options
+++++++++++++++++++++

socket
    Required: The TCP socket Pyruvate should bind to.
    `Pyruvate` also supports `systemd socket activation <https://www.freedesktop.org/software/systemd/man/systemd.socket.html>`_
    If you specify `None` as the socket value, `Pyruvate` will try to acquire a socket bound by `systemd`.

workers
    Required: Number of worker threads to use.

async_logging
    Optional: Log asynchronously using a dedicated thread.
    Defaults to `True`.

chunked_transfer
    Optional: Whether to use chunked transfer encoding if no Content-Length header is present.
    Defaults to `False`.

keepalive_timeout
    Optional: Specify a timeout in integer seconds for keepalive connection.
    The persistent connection will be closed after the timeout expires.
    Defaults to 60 seconds.

max_number_headers
    Optional: Maximum number of request headers that will be parsed.
    If a request contains more headers than configured, request processing will stop with an error indicating an incomplete request.
    The default is 32 headers

max_reuse_count
    Optional: Specify how often to reuse an existing connection.
    Setting this parameter to 0 will effectively disable keep-alive connections.
    This is the default.

qmon_warn_threshold
    Optional: Warning threshold for the number of requests in the request queue.
    A warning will be logged if the number of queued requests reaches this value.
    The value must be a positive integer.
    The default is `None` which disables the queue monitor.

send_timeout
    Optional: Time to wait for a client connection to become available for
    writing after EAGAIN, in seconds. Connections that do not receive data
    within this time are closed.
    The value must be a positive integer.
    The default is 60 seconds.

Logging
+++++++

Pyruvate uses the standard `Python logging facility <https://docs.python.org/3/library/logging.html>`_.
The logger name is `pyruvate`.
See the Python documentation (`logging <https://docs.python.org/3/library/logging.html>`_, `logging.config <https://docs.python.org/3/library/logging.config.html>`_) for configuration options.

Example Configurations
----------------------

Django
++++++

After installing Pyruvate in your Django virtualenv, create or modify your `wsgi.py` file (one worker listening on 127.0.0.1:8000):

.. code-block:: python

    import os
    import pyruvate

    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_django_application.settings")

    application = get_wsgi_application()

    pyruvate.serve(application, "127.0.0.1:8000", 1)

You can now start Django + Pyruvate with::

    $ python wsgi.py

Override settings by using the `DJANGO_SETTINGS_MODULE` environment variable when appropriate.
Tested with `Django 4.2.x <https://www.djangoproject.com/>`_.

MapProxy
++++++++

First create a basic WSGI configuration following the `MapProxy deployment documentation <https://mapproxy.org/docs/latest/deployment.html#server-script>`_.
Then modify `config.py` so it is using Pyruvate (2 workers listening on 127.0.0.1:8005):

.. code-block:: python

    import os.path
    import pyruvate

    from mapproxy.wsgiapp import make_wsgi_app
    application = make_wsgi_app(r'/path/to/mapproxy/mapproxy.yaml')

    pyruvate.serve(application, "127.0.0.1:8005", 2)

Start from your virtualenv::

    $ python config.py

Tested with `Mapproxy 1.15.x, 1.13.x, 1.12.x <https://mapproxy.org/>`_.

Plone
+++++

Using `pip`
~~~~~~~~~~~

After installing Pyruvate in your Plone virtualenv, change the `server` section in your `zope.ini` file (located in `instance/etc` if you are using `mkwsgiinstance` to create the instance)::

    [server:main]
    use = egg:pyruvate#main
    socket = localhost:7878
    workers = 2

Using `zc.buildout`
~~~~~~~~~~~~~~~~~~~

Using `zc.buildout <https://pypi.org/project/zc.buildout/>`_ and `plone.recipe.zope2instance <https://pypi.org/project/plone.recipe.zope2instance>`_ you can define an instance part using Pyruvate's `PasteDeploy <https://pastedeploy.readthedocs.io/en/latest/>`_ entry point::

    [instance]
    recipe = plone.recipe.zope2instance
    http-address = 127.0.0.1:8080
    eggs =
        Plone
        pyruvate
    wsgi-ini-template = ${buildout:directory}/templates/pyruvate.ini.in

The `server` section of the template provided with the `wsgi-ini-template <https://pypi.org/project/plone.recipe.zope2instance/#advanced-options>`_ option should look like this (3 workers listening on `http-address` as specified in the buildout `[instance]` part)::

    [server:main]
    use = egg:pyruvate#main
    socket = %(http_address)s
    workers = 3

There is a minimal buildout example configuration for Plone 5.2 in the `examples directory <https://gitlab.com/tschorr/pyruvate/-/tree/main/examples/plone52>`_ of the package.

Tested with `Plone 6.0.x, 5.2.x <https://plone.org/>`_.

Pyramid
+++++++

Install Pyruvate in your Pyramid virtualenv using pip::

    $ pip install pyruvate

Modify the server section in your `.ini` file to use Pyruvate's `PasteDeploy <https://pastedeploy.readthedocs.io/en/latest/>`_ entry point (listening on 127.0.0.1:7878 and using 5 workers)::

    [server:main]
    use = egg:pyruvate#main
    socket = 127.0.0.1:7878
    workers = 5

Start your application as usual using `pserve`::

    $ pserve path/to/your/configfile.ini

Tested with `Pyramid 2.0, 1.10.x <https://trypyramid.com/>`_.

Radicale
++++++++

You can find an example configuration for `Radicale <https://radicale.org>`_ in the `examples directory <https://gitlab.com/tschorr/pyruvate/-/tree/main/examples/plone52>`_ of the package.
Tested with `Radicale 3.5.0 <https://radicale.org>`_.

Nginx settings
++++++++++++++

Like other WSGI servers Pyruvate should be used behind a reverse proxy, e.g. Nginx::

    ....
    location / {
        proxy_pass http://localhost:7878;
        ...
    }
    ...

Nginx doesn't use keepalive connections by default so you will need to `modify your configuration <https://nginx.org/en/docs/http/ngx_http_upstream_module.html#keepalive>`_ if you want persistent connections.
