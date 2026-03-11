
import datetime, statistics
from tester.tests import ALL_TESTS, run_test

def run_all() -> dict:
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    results = [run_test(name, fn) for name, fn in ALL_TESTS]

    latencies = [r["latency_ms"] for r in results if r["latency_ms"] is not None]
    passed  = sum(1 for r in results if r["status"] == "PASS")
    failed  = sum(1 for r in results if r["status"] == "FAIL")
    errors  = sum(1 for r in results if r["status"] == "ERROR")
    total   = len(results)

    avg = round(statistics.mean(latencies), 2) if latencies else None
    p95 = round(statistics.quantiles(latencies, n=20)[18], 2) if len(latencies) >= 2 else (latencies[0] if latencies else None)

    return {
        "api": "Frankfurter",
        "base_url": "https://api.frankfurter.app",
        "timestamp": timestamp,
        "summary": {
            "total": total, "passed": passed, "failed": failed, "errors": errors,
            "error_rate": round((failed + errors) / total, 4) if total else None,
            "availability": round(passed / total, 4) if total else None,
            "latency_ms_avg": avg,
            "latency_ms_p95": p95,
        },
        "tests": results,
    }
```

---

## 7️⃣ `requirements.txt` — Remplace le contenu
```
flask>=3.0.0
requests>=2.31.0
