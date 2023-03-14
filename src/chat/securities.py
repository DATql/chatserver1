import time
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

def rate_limit(requests=1, interval=60):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Tạo rate_limit_key từ IP của client và đường dẫn truy cập
            rate_limit_key = f"rate_limit:{request.META['REMOTE_ADDR']}:{request.path}"

            # Lấy thông tin từ cache
            cache_info = cache.get(rate_limit_key)

            # Nếu cache không có thông tin hoặc đã quá hạn, tạo cache mới
            if cache_info is None or time.time() > cache_info['timestamp'] + interval:
                cache.set(rate_limit_key, {'timestamp': time.time(), 'requests': 1}, timeout=interval)
            # Nếu cache vẫn còn hạn, kiểm tra số lần truy cập
            else:
                cache_info['requests'] += 1
                cache.set(rate_limit_key, cache_info, timeout=interval)
                if cache_info['requests'] > requests:
                    raise PermissionDenied

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
