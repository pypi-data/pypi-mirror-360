import pyruvate
from app import application

pyruvate.serve(application, '0.0.0.0:9808', 2)
