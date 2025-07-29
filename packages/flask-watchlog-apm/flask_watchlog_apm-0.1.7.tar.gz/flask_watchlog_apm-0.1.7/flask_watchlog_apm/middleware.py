import time
from flask import request
from .collector import record


def apm_middleware(app, service="default-service"):
    @app.before_request
    def start_timer():
        request._watchlog_start = time.time()

    @app.after_request
    def track_response(response):
        try:
            duration = (
                time.time() - getattr(request, "_watchlog_start", time.time())
            ) * 1000
            record(
                {
                    "type": "request",
                    "service": service,
                    "path": path,
                    "method": request.method,
                    "statusCode": status_code,
                    "duration": duration,
                    "memory": get_memory_usage(),
                }
            )
        except Exception as e:
            pass
            # print(f"[Watchlog APM] Error in tracking: {e}")
        return response

    return app
