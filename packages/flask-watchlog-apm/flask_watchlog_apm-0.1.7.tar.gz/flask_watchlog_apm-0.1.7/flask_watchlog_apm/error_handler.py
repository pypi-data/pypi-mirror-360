from flask import request
from .collector import record
from werkzeug.exceptions import NotFound


def apm_error_handler(app, service="default-service"):
    @app.errorhandler(Exception)
    def handle_error(e):
        # از لاگ کردن 404 صرف‌نظر می‌کنیم
        if isinstance(e, NotFound):
            return e

        record(
            {
                "type": "error",
                "service": service,
                "path": request.path,
                "method": request.method,
                "statusCode": 500,
                "message": str(e),
                "stack": repr(e),
            }
        )
        raise e
