from collections import defaultdict

_grouped = defaultdict(
    lambda: {
        "type": "aggregated_request",
        "service": None,
        "path": None,
        "method": None,
        "request_count": 0,
        "error_count": 0,
        "total_duration": 0.0,
        "max_duration": 0.0,
        "total_memory": {"rss": 0, "heapUsed": 0, "heapTotal": 0},
    }
)


def record(metric):
    if metric.get("type") != "request":
        return

    duration = float(metric.get("duration", 0))
    memory = metric.get("memory", {})

    key = f"{metric.get('service')}|{metric.get('path')}|{metric.get('method')}"
    group = _grouped[key]
    group["service"] = metric.get("service")
    group["path"] = metric.get("path")
    group["method"] = metric.get("method")
    group["request_count"] += 1

    if metric.get("statusCode", 0) >= 500:
        group["error_count"] += 1

    group["total_duration"] += duration
    group["max_duration"] = max(group["max_duration"], duration)

    # ثبت memory
    if memory:
        group["total_memory"]["rss"] += memory.get("rss", 0)
        group["total_memory"]["heapUsed"] += memory.get("heapUsed", 0)
        group["total_memory"]["heapTotal"] += memory.get("heapTotal", 0)


def flush():
    results = []
    for group in _grouped.values():
        count = group["request_count"] or 1  # محافظت در برابر تقسیم بر صفر

        results.append(
            {
                "type": group["type"],
                "service": group["service"],
                "path": group["path"],
                "method": group["method"],
                "request_count": count,
                "error_count": group["error_count"],
                "avg_duration": round(group["total_duration"] / count, 2),
                "max_duration": round(group["max_duration"], 2),
                "avg_memory": {
                    "rss": round(group["total_memory"]["rss"] / count),
                    "heapUsed": round(group["total_memory"]["heapUsed"] / count),
                    "heapTotal": round(group["total_memory"]["heapTotal"] / count),
                },
            }
        )

    _grouped.clear()
    return results
