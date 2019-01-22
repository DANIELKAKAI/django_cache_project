# django_cache_project
use the following command to run the app on your local server

python manage.py runserver '''

In this project I've created my own custom cache middleware which inherits from the default django cache middleware classes.
The settings.py contains the list of urls to be cached

'''python
CACHE_URLS = [('^index/',60*60),('^sample/',20)]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:8000',
    }
}
'''

The cache middleware is implemented in the cachemiddleware.py file with the following key changes to override the parent middleware 
class functions

##checking whether a url is the list of CACHE_URLS

'''python
        request_url = request.get_full_path()
        url_match = 0
        for value in settings.CACHE_URLS:
            regex = value[0]
            if re.match(regex,request_url):
                match+=1
        if url_match > 0:
            request._cache_update_cache = False
            return None
'''

##setting a cache timeout

'''python
      for value in settings.CACHE_URLS:
            regex = value[0]
            request_url = request.get_full_path()
            if re.match(regex,request_url):
                self.timeout = value[1]

      timeout = self.timeout
'''
