FROM ubuntu
RUN apt-get -y update
RUN apt-get -y install python3 python3-dev python3-pip python3-venv libev-dev gcc
RUN python3 -V
RUN mkdir py312
WORKDIR /py312
COPY pyruvate-1.5.0-cp312-cp312-manylinux_2_28_x86_64.whl /py312/pyruvate-1.5.0-cp312-cp312-manylinux_2_28_x86_64.whl
RUN python3 -m venv .
RUN bin/pip install gunicorn uWSGI bjoern cheroot waitress
RUN bin/pip install pyruvate-1.5.0-cp312-cp312-manylinux_2_28_x86_64.whl
RUN mkdir -p /home/www
COPY src /home/www/wsgi_benchmark
EXPOSE 9808
RUN chown -R www-data:www-data /home/www/wsgi_benchmark
