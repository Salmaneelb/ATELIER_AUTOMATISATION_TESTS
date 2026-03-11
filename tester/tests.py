import requests
from tester.client import get

def run_test(name, fn):
    try:
        r = fn()
        return {
            "name": name,
            "status": "PASS" if r["passed"] else "FAIL",
            "latency_ms": r.get("latency_ms"),
            "details": r.get("details", ""),
            "retried": r.get("retried", False),
        }
    except Exception as e:
        return {"name": name, "status": "ERROR", "latency_ms": None, "details": str(e), "retried": False}

# ── Tests CONTRAT ──────────────────────────────────────────────

def test_latest_200():
    r = get("/latest")
    return {"passed": r["status_code"] == 200, "latency_ms": r["latency_ms"],
            "details": f"status={r['status_code']}", "retried": r["retried"]}

def test_content_type_json():
    resp = requests.get("https://api.frankfurter.app/latest", timeout=5)
    ct = resp.headers.get("Content-Type", "")
    return {"passed": "application/json" in ct, "latency_ms": None, "details": f"Content-Type={ct}"}

def test_required_fields():
    r = get("/latest")
    data = r["json"] or {}
    missing = [f for f in ["base", "date", "rates"] if f not in data]
    return {"passed": not missing, "latency_ms": r["latency_ms"],
            "details": f"Manquants: {missing}" if missing else "OK", "retried": r["retried"]}

def test_field_types():
    r = get("/latest")
    data = r["json"] or {}
    errors = []
    if not isinstance(data.get("base"), str):   errors.append("base doit être str")
    if not isinstance(data.get("date"), str):   errors.append("date doit être str")
    if not isinstance(data.get("rates"), dict): errors.append("rates doit être dict")
    else:
        bad = [(k, v) for k, v in data["rates"].items() if not isinstance(v, (int, float))]
        if bad: errors.append(f"rates non-numériques: {bad[:2]}")
    return {"passed": not errors, "latency_ms": r["latency_ms"],
            "details": "; ".join(errors) or "OK", "retried": r["retried"]}

def test_base_usd():
    r = get("/latest", params={"base": "USD"})
    data = r["json"] or {}
    return {"passed": r["status_code"] == 200 and data.get("base") == "USD",
            "latency_ms": r["latency_ms"], "details": f"base={data.get('base')}", "retried": r["retried"]}

def test_filter_symbols():
    r = get("/latest", params={"symbols": "USD,GBP"})
    data = r["json"] or {}
    rates = data.get("rates", {})
    extra = [k for k in rates if k not in ("USD", "GBP")]
    return {"passed": r["status_code"] == 200 and not extra and len(rates) == 2,
            "latency_ms": r["latency_ms"], "details": f"rates={list(rates.keys())}", "retried": r["retried"]}

def test_currencies():
    r = get("/currencies")
    data = r["json"] or {}
    return {"passed": r["status_code"] == 200 and isinstance(data, dict) and len(data) > 0,
            "latency_ms": r["latency_ms"], "details": f"{len(data)} devises", "retried": r["retried"]}

def test_historical():
    r = get("/2020-01-02")
    data = r["json"] or {}
    return {"passed": r["status_code"] == 200 and data.get("date") == "2020-01-02",
            "latency_ms": r["latency_ms"], "details": f"date={data.get('date')}", "retried": r["retried"]}

# ── Tests ROBUSTESSE ───────────────────────────────────────────

def test_invalid_base():
    r = get("/latest", params={"base": "INVALIDXXX"})
    passed = r["status_code"] is not None and 400 <= r["status_code"] < 500
    return {"passed": passed, "latency_ms": r["latency_ms"],
            "details": f"status={r['status_code']} (attendu 4xx)", "retried": r["retried"]}

def test_invalid_date():
    r = get("/9999-99-99")
    passed = r["status_code"] is not None and 400 <= r["status_code"] < 500
    return {"passed": passed, "latency_ms": r["latency_ms"],
            "details": f"status={r['status_code']} (attendu 4xx)", "retried": r["retried"]}

def test_latency():
    r = get("/latest")
    lat = r["latency_ms"] or 9999
    return {"passed": lat < 3000, "latency_ms": lat,
            "details": f"{lat}ms (seuil=3000ms)", "retried": r["retried"]}

# ── Registre ───────────────────────────────────────────────────

ALL_TESTS = [
    ("GET /latest → HTTP 200",                test_latest_200),
    ("GET /latest → Content-Type JSON",        test_content_type_json),
    ("GET /latest → champs obligatoires",      test_required_fields),
    ("GET /latest → types des champs",         test_field_types),
    ("GET /latest?base=USD → base correcte",   test_base_usd),
    ("GET /latest?symbols=USD,GBP → filtrage", test_filter_symbols),
    ("GET /currencies → liste des devises",    test_currencies),
    ("GET /2020-01-02 → historique correct",   test_historical),
    ("GET /latest?base=INVALID → 4xx",         test_invalid_base),
    ("GET /9999-99-99 → date invalide → 4xx",  test_invalid_date),
    ("GET /latest → latence < 3000ms",         test_latency),
]
