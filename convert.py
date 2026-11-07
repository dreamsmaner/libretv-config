#!/usr/bin/env python3
"""Convert hafrey1/LunaTV-config (LunaTV format) to LibreTV SourceList v2.

Three upstream variants are converted in one run:

  LunaTV-config.json (full, with adult)      -> libretv-config.json
  jingjian.json      (slim, with adult)      -> libretv-config-jingjian.json
  jin18.json         (slim, no adult)        -> libretv-config-jin18.json

Mapping (cross-validated against the one-off conversion in ljfbin2/tv-sources,
28/28 entries matched exactly):
  api_site.<key>.name   -> sources[].name
  api_site.<key>.api    -> sources[].url
  api_site.<key>.detail -> sources[].detail
  name contains 🔞       -> sources[].isAdult = true, else false

Filtering policy (default): drop entries whose upstream "_comment" marks the
source as unsearchable or result-polluting; keep the ones marked "备用"
(backup) and "不稳定" (unstable -- LibreTV's source-health ladder disables
persistently failing sources on its own). The two slim upstream files carry
no "_comment" marks (upstream already curated them), so the filter changes
nothing there. If upstream later fixes a source and removes the comment, it
returns automatically on the next run. Pass --keep-all to disable filtering.

Fail-safe: all three conversions finish in memory before any file is
written. Any upstream/format problem raises, the script exits non-zero and
every previously published file is left untouched.
"""
import argparse, json, sys, urllib.request

BASE = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/"
JOBS = [
    ("LunaTV-config.json", "libretv-config.json", "LunaTV-config 完整版（LibreTV）"),
    ("jingjian.json", "libretv-config-jingjian.json", "LunaTV-config 精简版+18禁（LibreTV）"),
    ("jin18.json", "libretv-config-jin18.json", "LunaTV-config 精简版（LibreTV）"),
]
DROP_HINTS = ("无法搜索", "暂不支持搜索", "无搜索结果", "污染", "403", "禁止搜索")


def convert(data, list_name, keep_all=False):
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
    return {"name": list_name, "version": 2, "sources": sources}, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-all", action="store_true")
    a = ap.parse_args()
    results = []
    for upstream_name, output_name, list_name in JOBS:
        raw = urllib.request.urlopen(BASE + upstream_name, timeout=30).read().decode("utf-8")
        out, dropped = convert(json.loads(raw), list_name, keep_all=a.keep_all)
        results.append((output_name, out, dropped))
    for output_name, out, dropped in results:
        with open(output_name, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write("\n")
        adult = sum(1 for s in out["sources"] if s["isAdult"])
        print(f"{output_name}: kept {len(out['sources'])} sources "
              f"({adult} adult, {len(out['sources']) - adult} normal); dropped {len(dropped)}")
        for n, why in dropped:
            print(f"  dropped: {n} -- {why}")


if __name__ == "__main__":
    sys.exit(main())
