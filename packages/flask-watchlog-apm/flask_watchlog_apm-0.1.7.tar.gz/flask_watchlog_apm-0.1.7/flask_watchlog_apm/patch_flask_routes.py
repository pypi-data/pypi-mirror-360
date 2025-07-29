import functools
import time
import psutil
import os
from flask import request
from .collector import record


def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info()
    return {
        "rss": mem.rss,
        "heapUsed": mem.rss,  # approximation
        "heapTotal": mem.vms,  # approximation
    }


def patch_flask_app(app, service="default-service", ignore=[]):
    """
    تمام routeهای Flask را hook می‌کند تا متریک‌ها را خودکار ثبت کند.
    """
    original_add_url_rule = app.add_url_rule

    def wrapped_add_url_rule(rule, endpoint=None, view_func=None, **options):
        if any(
            isinstance(p, str) and p == rule or hasattr(p, "match") and p.match(rule)
            for p in ignore
        ):
            return original_add_url_rule(rule, endpoint, view_func, **options)

        if view_func:
            view_func = wrap_view_func(view_func, rule, service)

        return original_add_url_rule(rule, endpoint, view_func, **options)

    app.add_url_rule = wrapped_add_url_rule
    return app


def wrap_view_func(view_func, path, service):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        status_code = 200
        try:
            response = view_func(*args, **kwargs)
            if hasattr(response, "status_code"):
                status_code = response.status_code
            return response
        except Exception as e:
            status_code = 500
            raise e
        finally:
            duration = (time.perf_counter() - start) * 1000  # milliseconds
            memory = get_memory_usage()
            record(
                {
                    "type": "request",
                    "service": service,
                    "path": path,
                    "method": request.method,
                    "statusCode": status_code,
                    "duration": duration,
                    "memory": memory,
                }
            )

    return wrapper
