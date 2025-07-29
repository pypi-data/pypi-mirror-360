# APM for Flask – Watchlog Integration

🎯 Lightweight and production-safe Application Performance Monitoring (APM) middleware for Flask apps, made for [Watchlog](https://watchlog.io).

Tracks route execution time, status codes, memory usage, and errors — and sends them periodically to your Watchlog agent in aggregated form.

---

## 🚀 Features

- 🔧 Automatic tracking of all Flask routes
- 📊 Aggregation of metrics by path and method
- ⚠️ Optional error tracking
- 🌐 Sends metrics to Watchlog agent over HTTP
- 🧠 Captures memory usage (`rss`, `vms`)
- 💡 Safe-by-default (never crashes your app)
- 🏷️ Auto-detects route like `/users/<int:id>`

---

## 📦 Installation

```bash
pip install flask_watchlog_apm
```

---

## ⚙️ Usage

Here’s a complete example:

```python
from flask import Flask
from flask_watchlog_apm import patch_flask_app, apm_error_handler, start

app = Flask(__name__)

# Auto-instrument all routes
patch_flask_app(app, service="my-flask-service")

# Enable automatic error tracking
apm_error_handler(app, service="my-flask-service")

# Start background sender
start()




@app.route("/user/<int:user_id>")
def get_user(user_id):
    return f"User {user_id}"

@app.route("/fail")
def fail():
    raise Exception("error")

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 🛠️ Service Name

You can define your service name like this:

```python
patch_flask_app(app, service="my-service")
apm_error_handler(app, service="my-service")
```

Or set it in environment variables:

```bash
export WATCHLOG_APM_SERVICE=users-api
```

Fallbacks to `APP_NAME` or defaults to `flask-app`.

---

## 📤 What gets sent

Example payload every 10 seconds:

```json
{
  "collected_at": "2025-05-18T12:00:00Z",
  "platformName": "flask",
  "metrics": [
    {
      "type": "aggregated_request",
      "service": "users-api",
      "path": "/user/<int:user_id>",
      "method": "GET",
      "request_count": 3,
      "error_count": 1,
      "avg_duration": 9.2,
      "max_duration": 13.4,
      "avg_memory": {
        "rss": 13434880,
        "heapUsed": 13930496,
        "heapTotal": 13930496
      }
    }
  ]
}
```

---

## 📁 Recommended `.gitignore`

```gitignore
/storage/logs/apm-buffer.json
/storage/framework/cache/watchlog-apm.lock
```

---

## ✅ Notes

- Uses `request.url_rule.rule` to extract route pattern like `/user/<int:id>`
- All routes are auto-wrapped using `patch_flask_app`
- Error tracking is optional but recommended
- Metrics are batched in a local file and flushed every 10 seconds

---

## 📝 License

MIT © Mohammadreza  
Built for [Watchlog.io](https://watchlog.io)
