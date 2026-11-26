"""Shared helpers: storyboard loading + validation, run logging, caching, retries."""
import hashlib, json, os, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
RUNS = ROOT / "runs.jsonl"
CACHE_DIR = OUT / ".cache"


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _minimal_validate(sb, schema):
    """Fallback validator used only if the jsonschema package is missing."""
    errs = []
    for k in schema["required"]:
        if k not in sb:
            errs.append(f"missing top-level field: {k}")
    shot_schema = schema["properties"]["shots"]
    shots = sb.get("shots", [])
    if not (shot_schema["minItems"] <= len(shots) <= shot_schema["maxItems"]):
        errs.append(f"need 8-12 shots, got {len(shots)}")
    ids = set()
    for s in shots:
        for k in shot_schema["items"]["required"]:
            if k not in s:
                errs.append(f"{s.get('id','?')}: missing {k}")
        if s.get("id") in ids:
            errs.append(f"duplicate shot id {s.get('id')}")
        ids.add(s.get("id"))
    return errs


def load_storyboard():
    sb = json.loads((ROOT / "storyboard.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schema" / "storyboard.schema.json").read_text())
    try:
        import jsonschema
        v = jsonschema.Draft202012Validator(schema)
        errs = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(sb)]
    except ImportError:
        errs = _minimal_validate(sb, schema)
    total = sum(s["duration"] for s in sb.get("shots", [])) + sb.get("end_card", {}).get("duration", 0)
    if not 60 <= total <= 90:
        errs.append(f"total duration {total}s is outside 60-90s")
    if errs:
        print("storyboard.json is invalid:\n  " + "\n  ".join(errs))
        sys.exit(1)
    return sb


def log_call(stage, model, params, latency_s, cost_usd=0.0, status="ok", gpu_minutes=0.0, note=""):
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "stage": stage, "model": model,
           "params": params, "seed": params.get("seed"), "latency_s": round(latency_s, 3),
           "gpu_minutes": gpu_minutes, "cost_usd": cost_usd, "status": status, "note": note}
    with RUNS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def input_hash(*parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


class Cache:
    """Maps item id -> hash of the inputs that produced it. Skip work if hash and file match."""
    def __init__(self, stage):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.path = CACHE_DIR / f"{stage}.json"
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    def fresh(self, key, h, out_file):
        return self.data.get(key) == h and Path(out_file).exists()

    def put(self, key, h):
        self.data[key] = h
        self.path.write_text(json.dumps(self.data, indent=2))


def retry(fn, attempts=3, base_delay=4):
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # network errors, 429 quota, 5xx
            if i == attempts - 1:
                raise
            wait = base_delay * (2 ** i)
            print(f"  retry {i+1}/{attempts-1} after error: {e} (waiting {wait}s)")
            time.sleep(wait)


def http_json(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}")


def ffmpeg(*args):
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *map(str, args)]
    subprocess.run(cmd, check=True)


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())
