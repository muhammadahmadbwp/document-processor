import os

env = os.getenv('DJANGO_ENV') or 'dev'
if env == 'prod':
    from .prod import *
elif env == 'uat':
    from .uat import *
else:
    from .dev import *