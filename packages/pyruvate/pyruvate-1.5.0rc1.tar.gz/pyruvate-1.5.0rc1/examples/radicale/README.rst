Pyruvate Example Configuration for Radicale CalDAV and CardDAV Server
=====================================================================

`Radicale <https://radicale.org>`_ is a free and open-source CalDAV and CardDAV server.
To use it with Pyruvate, first install it in a Python virtualenv, e.g. using the `requirements.txt` file in this directory::

    $ pip install -r requirements.txt

Start Radicale using the `wsgi.py` module.
Radicale expects the location of the configuration file in the `RADICALE_CONFIG` environment variable::

    $ RADICALE_CONFIG=/path/to/this/directory/config python wsgi.py

Don't forget to edit the `config` file before using it.
