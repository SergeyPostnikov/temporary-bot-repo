# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, '/home/a/alekspbv/alekspbv.beget.tech/temporary-bot-repo/FoodPlan')  # python dir
sys.path.insert(1, '/home/a/alekspbv/.local/bin/python3.8/site-packages')  # django dir
os.environ['DJANGO_SETTINGS_MODULE'] = 'FoodPlan.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
