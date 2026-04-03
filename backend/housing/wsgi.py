import os
from django.core.wsgi import get_wsgi_application

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")

application = get_wsgi_application()
