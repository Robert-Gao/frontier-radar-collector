# Frontier Radar collector

Deterministic collection for the published Frontier Radar website. Python standard library only; no model calls, AI quota, API keys or copied news content in this repository.

- Scheduled at 00:00 UTC / 08:00 Asia/Shanghai each day; GitHub may delay scheduled runs.
- Reads existing sources from the website, respects paused sources and their daily / two-day / weekly frequency, and invokes the same server collection operation used by the website's manual refresh button.
- The website performs collection, robots checks, deduplication, baseline handling and persistent storage. This runner does not bypass source restrictions or change future-only settings.
- Website source errors appear in the website's status view and in run logs. A transport failure to the website fails the job; a failed external news source is reported independently.
- Run manually in Actions using `force` to check all enabled sources once.
- Chinese translation and editorial analysis remain a separate 08:30 cloud AI task that processes only missing or changed material. Collection does not trigger that task.
- Each run commits only a timestamp, run ID and outcome to `last-run.json`; this provides an audit marker and repository activity so the public scheduled workflow does not go inactive after 60 days. The temporary GitHub Actions token is scoped to this runner repository.

Website: https://frontier-radar.gaoxinpeng1999.chatgpt.site/
