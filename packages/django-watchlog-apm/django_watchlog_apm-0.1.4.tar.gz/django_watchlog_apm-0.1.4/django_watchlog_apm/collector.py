_grouped = {}


def record(metric):
    if metric.get("type") != "request":
        return

    key = f"{metric['service']}|{metric['path']}|{metric['method']}"
    group = _grouped.setdefault(
        key,
        {
            "type": "aggregated_request",
            "service": metric["service"],
            "path": metric["path"],
            "method": metric["method"],
            "request_count": 0,
            "error_count": 0,
            "total_duration": 0,
            "max_duration": 0,
            "total_memory": {
                "rss": 0,
                "heapUsed": 0,
                "heapTotal": 0
            }
        },
    )

    group["request_count"] += 1
    if metric.get("statusCode", 0) >= 500:
        group["error_count"] += 1

    duration = metric.get("duration", 0)
    group["total_duration"] += duration
    group["max_duration"] = max(group["max_duration"], duration)

    # memory aggregation if available
    memory = metric.get("memory")
    if memory:
        group["total_memory"]["rss"] += memory.get("rss", 0)
        group["total_memory"]["heapUsed"] += memory.get("heapUsed", 0)
        group["total_memory"]["heapTotal"] += memory.get("heapTotal", 0)


def flush():
    results = []

    for group in _grouped.values():
        count = group["request_count"] or 1

        result = {
            "type": group["type"],
            "service": group["service"],
            "path": group["path"],
            "method": group["method"],
            "request_count": group["request_count"],
            "error_count": group["error_count"],
            "avg_duration": round(group["total_duration"] / count, 2),
            "max_duration": round(group["max_duration"], 2),
        }

        # average memory if data available
        if any(group["total_memory"].values()):
            result["avg_memory"] = {
                "rss": round(group["total_memory"]["rss"] / count),
                "heapUsed": round(group["total_memory"]["heapUsed"] / count),
                "heapTotal": round(group["total_memory"]["heapTotal"] / count)
            }

        results.append(result)

    _grouped.clear()
    return results
