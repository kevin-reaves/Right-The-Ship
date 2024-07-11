import os
import sys
import django

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'right_the_ship.settings')
    django.setup()