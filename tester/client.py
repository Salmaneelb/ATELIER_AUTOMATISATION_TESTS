import time, requests

BASE_URL = "https://api.frankfurter.app"
TIMEOUT = 5
MAX_RETRIES = 1

def get(endpoint: str, params: dict = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    result = {"status_code": None, "json": None, "latency_ms": None, "error": None, "retried": False}

    for attempt in range(MAX_RETRIES + 1):
        try:
            t0 = time.perf_counter()
            response = requests.get(url, params=params, timeout=TIMEOUT)
            result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            result["status_code"] = response.status_code

            if response.status_code == 429 and attempt < MAX_RETRIES:
                time.sleep(int(response.headers.get("Retry-After", 2)))
                result["retried"] = True
                continue
            if response.status_code >= 500 and attempt < MAX_RETRIES:
                time.sleep(1)
                result["retried"] = True
                continue

            try:
                result["json"] = response.json()
            except Exception:
                result["json"] = None
            return result

        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
            if attempt < MAX_RETRIES:
                result["retried"] = True
                time.sleep(1)
                continue
            return result
        except Exception as e:
            result["error"] = str(e)
            return result

    return result
