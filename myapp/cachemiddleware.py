from django.conf import settings
from django.middleware.cache import *
import re


class CustomUpdateCacheMiddleware(UpdateCacheMiddleware):
    """
    Response-phase cache middleware that updates the cache if the response is
    cacheable.

    Must be used as part of the two-part update/fetch cache middleware.
    UpdateCacheMiddleware must be the first piece of middleware in MIDDLEWARE
    so that it'll get called last during the response phase.
    """
    def __init__(self, get_response=None):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.cache = caches[self.cache_alias]
        self.get_response = get_response
    

    def _should_update_cache(self, request, response):
        return hasattr(request, '_cache_update_cache') and request._cache_update_cache



    def process_response(self, request, response):
        """Set the cache, if needed."""
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.
            return response

        if response.streaming or response.status_code not in (200, 304):
            return response

        # Don't cache responses that set a user-specific (and maybe security
        # sensitive) cookie in response to a cookie-less request.
        if not request.COOKIES and response.cookies and has_vary_header(response, 'Cookie'):
            return response

        # Don't cache a response with 'Cache-Control: private'
        if 'private' in response.get('Cache-Control', ()):
            return response

        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
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
        patch_response_headers(response, timeout)
        if timeout and response.status_code == 200:
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix, cache=self.cache)
            if hasattr(response, 'render') and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response, timeout)
        return response



class CustomFetchFromCacheMiddleware(FetchFromCacheMiddleware):
    """
    Request-phase cache middleware that fetches a page from the cache.

    Must be used as part of the two-part update/fetch cache middleware.
    FetchFromCacheMiddleware must be the last piece of middleware in MIDDLEWARE
    so that it'll get called last during the request phase.
    """
    def __init__(self, get_response=None):
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.cache = caches[self.cache_alias]
        self.get_response = get_response

    def process_request(self, request):
        """
        Check whether the page is already cached and return the cached
        version if available.
        """
        if request.method not in ('GET', 'HEAD'):
            request._cache_update_cache = False
            return None  # Don't bother checking the cache.

        """
        check if current url is in the list of urls that need to be cached
        """
        request_url = request.get_full_path()
        url_match = False
        for value in settings.CACHE_URLS:
            regex = value[0]
            if re.match(regex,request_url):
                url_match = True
        if url_match == False: #Don't check cache 
            request._cache_update_cache = False
            return None


        # try and get the cached GET response
        cache_key = get_cache_key(request, self.key_prefix, 'GET', cache=self.cache)
        if cache_key is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.
        response = self.cache.get(cache_key)
        # if it wasn't found and we are looking for a HEAD, try looking just for that
        if response is None and request.method == 'HEAD':
            cache_key = get_cache_key(request, self.key_prefix, 'HEAD', cache=self.cache)
            response = self.cache.get(cache_key)

        if response is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.

        # hit, return cached response
        request._cache_update_cache = False
        return response



class CacheMiddleware(CustomUpdateCacheMiddleware, CustomFetchFromCacheMiddleware):
    """
    Cache middleware that provides basic behavior for many simple sites.

    Also used as the hook point for the cache decorator, which is generated
    using the decorator-from-middleware utility.
    """
    def __init__(self, get_response=None, cache_timeout=None, **kwargs):
        self.get_response = get_response
        # We need to differentiate between "provided, but using default value",
        # and "not provided". If the value is provided using a default, then
        # we fall back to system defaults. If it is not provided at all,
        # we need to use middleware defaults.

        try:
            key_prefix = kwargs['key_prefix']
            if key_prefix is None:
                key_prefix = ''
        except KeyError:
            key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.key_prefix = key_prefix

        try:
            cache_alias = kwargs['cache_alias']
            if cache_alias is None:
                cache_alias = DEFAULT_CACHE_ALIAS
        except KeyError:
            cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.cache_alias = cache_alias

        if cache_timeout is None:
            cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.cache_timeout = cache_timeout
        self.cache = caches[self.cache_alias]