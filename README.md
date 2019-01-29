# django_cache_project
In this project I've created my own custom cache middleware which inherits from the default django cache middleware classes.<br/>
use the following commands to install dependancies and run the app on your local server

```
pip install -r requirements.txt

python manage.py runserver 
```
The settings.py contains the list of urls to be cached

```python
CACHE_URLS = [('^index/',60*60),('^sample/',20)]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = None          
CACHE_MIDDLEWARE_KEY_PREFIX = 'cache'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

The cache middleware is implemented in the cachemiddleware.py file with the following key changes to override the parent middleware 
class functions

### checking whether a url is the list of CACHE_URLS

```python
        request_url = request.get_full_path()
        url_match = False
        for value in settings.CACHE_URLS:
            regex = value[0]
            if re.match(regex,request_url):
                url_match = True
        if url_match == False: #Don't check cache
            request._cache_update_cache = False
            return None
```

### setting a cache timeout

```python
    request_url = request.get_full_path()
        
        for value in settings.CACHE_URLS:
            regex = value[0]
            if re.match(regex,request_url):
                self.cache_timeout = value[1]
                break;

        timeout = get_max_age(response)
        if timeout is None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
```
