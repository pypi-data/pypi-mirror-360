import pyruvate
from radicale import application


pyruvate.serve(application, '127.0.0.1:5232', 3)
