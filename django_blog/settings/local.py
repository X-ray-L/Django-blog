from .common import *
SECRET_KEY = 'h^k1^5r!_+it^80)s+19ar)kky8j#-*(942yq&*p*g%h-by^ko'
DEBUG = True
ALLOWED_HOSTS = ['*']

HAYSTACK_CONNECTIONS['default']['URL'] = 'http://elasticsearch_local:9200/'