from django.utils.functional import LazyObject
from django.core.cache import cache

class LazyQuerySet:
    """Lazy loading para querysets pesados"""
    
    def __init__(self, queryset_func, cache_key, timeout=300):
        self.queryset_func = queryset_func
        self.cache_key = cache_key
        self.timeout = timeout
        self._result = None
    
    def __iter__(self):
        if self._result is None:
            self._result = cache.get(self.cache_key)
            if self._result is None:
                self._result = list(self.queryset_func())
                cache.set(self.cache_key, self._result, self.timeout)
        return iter(self._result)
    
    def count(self):
        return len(list(self))

def lazy_queryset(cache_key, timeout=300):
    """Decorator para lazy loading de querysets"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return LazyQuerySet(
                lambda: func(*args, **kwargs),
                cache_key,
                timeout
            )
        return wrapper
    return decorator