import waitress
from app import application

waitress.serve(application, listen='0.0.0.0:9808', threads=2)
