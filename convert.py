#!/usr/bin/env python3
"""Convert hafrey1/LunaTV-config (LunaTV format) to a LibreTV SourceList v2.

Mapping (cross-validated against the one-off conversion in ljfbin2/tv-sources,
28/28 entries matched exactly):
  api_site.<key>.name   -> sources[].name
  api_site.<key>.api    -> sources[].url
  api_site.<key>.detail -> sources[].detail
  name contains 🔞       -> sources[].isAdult = true, else false

Filtering policy (default): drop entries whose upstream "_comment" marks the
source as unsearchable or result-polluting; keep the ones marked "备用"
(backup) and "不稳定" (unstable -- LibreTV's source-health ladder disables
persistently failing sources on its own). If upstream later fixes a source
and removes the comment, it returns automatically on the next run.
Pass --keep-all to disable filtering.

Fail-safe: any upstream/format problem raises, the script exits non-zero and
the previous sources.json is left untouched.
"""
import argparse, json, sys, urllib.request

UPSTREAM = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json"
DROP_HINTS = ("无法搜索", "暂不支持搜索", "无搜索结果", "污染", "403", "禁止搜索")


def convert(data, keep_all=False):
    sites = data.get("api_site")
    if not isinstance(sites, dict) or not sites:
        raise ValueError("upstream has no api_site object -- format may have changed")
    sources, dropped, seen = [], [], set()
    for _key, v in sites.items():
        name = (v.get("name") or "").strip()
        api = (v.get("api") or "").strip()
        detail = (v.get("detail") or "").strip()
        if not name or not api.startswith(("http://", "https://")):
            dropped.append((name or _key, "missing name or non-http api"))
            continue
        if api in seen:
            dropped.append((name, "duplicate url"))
            continue
        comment = (v.get("_comment") or "").strip()
        if not keep_all and any(h in comment for h in DROP_HINTS):
            dropped.append((name, f"_comment: {comment}"))
            continue
        seen.add(api)
        src = {"name": name, "url": api}
        if detail:
            src["detail"] = detail
        src["isAdult"] = "🔞" in name
        sources.append(src)
    if not sources:
        raise ValueError("conversion produced zero sources -- refusing to write an empty list")
    return {"name": "LunaTV-config 转换源（LibreTV）", "version": 2, "sources": sources}, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="read a local file instead of fetching upstream")
    ap.add_argument("--output", default="sources.json")
    ap.add_argument("--keep-all", action="store_true")
    a = ap.parse_args()
    if a.input:
        raw = open(a.input, encoding="utf-8").read()
    else:
        raw = urllib.request.urlopen(UPSTREAM, timeout=30).read().decode("utf-8")
    out, dropped = convert(json.loads(raw), keep_all=a.keep_all)
    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    adult = sum(1 for s in out["sources"] if s["isAdult"])
    print(f"kept {len(out['sources'])} sources ({adult} adult, {len(out['sources']) - adult} normal); dropped {len(dropped)}")
    for n, why in dropped:
        print(f"  dropped: {n} -- {why}")


if __name__ == "__main__":
    sys.exit(main())
