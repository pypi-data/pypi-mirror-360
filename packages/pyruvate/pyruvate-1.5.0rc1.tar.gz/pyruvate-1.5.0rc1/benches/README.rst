WSGI Benchmarks
===============

Benchmarking code is based on https://github.com/omedhabib/WSGI_Benchmarks.

Introduction
------------

The current setup is based on a quad core machine:

  * 2 cores are dedicated to docker / WSGI server
  * 2 cores are dedicated to web server stress tester

Steps to reproduce benchmarks
-----------------------------

Podman is required to run the benchmarking script.

Run `benchmark.sh` as a user that has docker permissions (it will automatically create the image), passing in directories to store results.

.. code-block::

    for directory in round*; do
        ./benchmark.sh $directory
    done

`results.py` will parse the results, producing a CSV file. Pass in the directories used in the previous step

.. code-block::

    ./results.py round* > results.csv

or use `postprocess.sh` (requires `matplotlib`) to produce some charts.

.. code-block::

   ./postprocess.sh

Results
-------

Versions used:

  * Bjoern 3.2.2 (one thread)
  * Cheroot 10.0.1 (one thread)
  * Gunicorn 23.0.0 (one thread)
  * Pyruvate 1.5.0 (2 threads)
  * uWSGI 2.0.30 (2 threads)
  * Waitress 3.0.2 (2 threads)

.. image:: requests.png

.. image:: latencies.png

.. image:: cpu.png

.. image:: memory.png

.. image:: errors.png
