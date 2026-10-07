"""Deterministic daily collector; Python standard library only, no model calls."""
import argparse
import concurrent.futures
import datetime as dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

SITE = "https://frontier-radar.gaoxinpeng1999.chatgpt.site"
BEIJING = ZoneInfo("Asia/Shanghai")

def due(source, now):
    if not source.get("enabled"):
        return False
    checked = source.get("last_checked")
    if not checked:
        return True
    try:
        last = dt.datetime.fromisoformat(checked.replace("Z", "+00:00")).astimezone(BEIJING)
    except (ValueError, TypeError):
        return True
    if source.get("status") == "running" and (now-last).total_seconds() < 600:
        return False
    days = max(1, int(source.get("interval_hours", 24)) // 24)
    return (now.astimezone(BEIJING).date() - last.date()).days >= days

def call(payload=None):
    request = urllib.request.Request(SITE + "/api/radar", data=None if payload is None else json.dumps(payload).encode(), headers={"Content-Type":"application/json", "User-Agent":"FrontierRadarScheduler/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in (429, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"Radar API HTTP {error.code}") from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("Radar API connection failed") from None
        time.sleep(2 ** attempt)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Manually check all enabled sources, respecting existing per-source leases")
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    sources = call()["sources"]
    targets = [s for s in sources if (bool(s["enabled"]) if args.force else due(s, now))]
    print(json.dumps({"mode":"dry_run" if args.dry_run else "collect", "enabled":sum(bool(s["enabled"]) for s in sources), "due":len(targets)}, ensure_ascii=False), flush=True)
    if args.dry_run:
        return
    batches = [[s["id"] for s in targets[i:i+3]] for i in range(0,len(targets),3)]
    failed = []
    request_failures = 0
    def refresh(ids):
        return call({"action":"refresh", "sourceIds":ids})["results"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(refresh, batch): batch for batch in batches}
        for future in concurrent.futures.as_completed(futures):
            try:
                for result in future.result():
                    print(json.dumps(result, ensure_ascii=False), flush=True)
                    if result["status"] == "error":
                        failed.append(result.get("name", result["id"]))
            except Exception as error:
                request_failures += 1
                print(json.dumps({"status":"error", "message":str(error), "source_ids":futures[future]}, ensure_ascii=False), flush=True)
                failed.extend(futures[future])
    print(json.dumps({"checked":len(targets), "source_errors":len(failed), "request_failures":request_failures}, ensure_ascii=False), flush=True)
    if request_failures:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
