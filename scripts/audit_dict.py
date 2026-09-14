#!/usr/bin/env python3
"""Audit pt.wiktionary stamps (librus-linker#1).

Extract unique dict titles from stamped HTML, batch-query the Action API
(≤50 titles), then write:

  catalogs/dict-allowlist.json  — pages that exist (canonical title + lemmas)
  catalogs/dict-missing.json    — no page / no Português section
  catalogs/dict-api-cache.json  — raw query cache

Also retries case (pt.wiktionary is case-sensitive on the first letter) and
conservative PT inflections. Does not map a missing word to a neighbor lemma
(espiritualista ↛ espiritualismo).

  python3 scripts/audit_dict.py
  python3 scripts/audit_dict.py --books lde
"""

from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlparse
from urllib.request import Request, urlopen

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from restamp import CAT, find_shell_books, fold, nfc  # noqa: E402

API = "https://pt.wiktionary.org/w/api.php"
UA = (
    "librus-linker-audit/0.1 "
    "(https://github.com/sergioSHKLR/librus-linker; sergio@doutrina.org)"
)
BATCH = 50
PT_MARK = re.compile(r"\{\{-pt-\}\}|==\s*Portugu[eê]s\s*==", re.I)
DICT_HREF = re.compile(
    r'<a\b([^>]*data-link-provider=["\']d["\'][^>]*)>(.*?)</a>',
    re.I | re.S,
)


def case_variants(title: str) -> list[str]:
    t = nfc(title)
    if not t:
        return []
    out = [t]
    fl, rest = t[0], t[1:]
    out.append(fl.lower() + rest)
    out.append(fl.upper() + rest)
    out.append(t.casefold())
    seen: set[str] = set()
    uniq: list[str] = []
    for x in out:
        if x and x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def inflection_candidates(title: str) -> list[str]:
    """Morphological self-maps only. No opensearch neighbors."""
    t = nfc(title)
    out: list[str] = []
    if len(t) >= 5 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
        out.append(t[:-1])
    if t.endswith("ões") and len(t) > 4:
        out.append(t[:-3] + "ão")
    if t.endswith("ães") and len(t) > 4:
        out.append(t[:-3] + "ão")
    if t.endswith("ais") and len(t) > 4:
        out.append(t[:-3] + "al")
    if t.endswith("ns") and len(t) > 4:
        out.append(t[:-2] + "m")
    if t.endswith("eis") and len(t) > 4:
        out.append(t[:-3] + "il")  # fúteis → fútil
    if t.endswith("as") and len(t) > 4:
        out.append(t[:-2] + "os")
    elif t.endswith("a") and len(t) >= 5 and not t.endswith("á"):
        out.append(t[:-1] + "o")  # corpórea → corpóreo
    seen = {fold(t)}
    uniq: list[str] = []
    for x in out:
        k = fold(x)
        if k not in seen and len(x) >= 3:
            seen.add(k)
            uniq.append(x)
    return uniq


def api(params: dict[str, str], tries: int = 5) -> dict:
    q = dict(params)
    q.setdefault("format", "json")
    q.setdefault("formatversion", "2")
    url = API + "?" + urlencode(q, safe="|")
    req = Request(url, headers={"User-Agent": UA})
    last: Exception | None = None
    for i in range(tries):
        try:
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            last = e
            if e.code in {429, 500, 502, 503, 504}:
                time.sleep(1.5 * (i + 1))
                continue
            raise
        except URLError as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"wiktionary API failed: {last}")


def query_titles(titles: list[str], cache: dict) -> None:
    pending = [t for t in titles if t not in cache]
    for i in range(0, len(pending), BATCH):
        chunk = pending[i : i + BATCH]
        if not chunk:
            continue
        data = api(
            {
                "action": "query",
                "redirects": "1",
                "normalized": "1",
                "titles": "|".join(chunk),
            }
        )
        q = data.get("query") or {}
        pages = {p["title"]: p for p in q.get("pages") or []}
        redir = {r["from"]: r["to"] for r in q.get("redirects") or []}
        norm = {n["from"]: n["to"] for n in q.get("normalized") or []}
        for src in chunk:
            key = redir.get(norm.get(src, src), norm.get(src, src))
            p = pages.get(key) or pages.get(src) or {}
            cache[src] = {
                "input": src,
                "resolved": p.get("title") or key,
                "missing": bool(p.get("missing") or p.get("invalid") or not p),
                "pageid": p.get("pageid"),
                "normalized": norm.get(src),
                "redirect": redir.get(norm.get(src, src)),
            }
        time.sleep(0.15)


def fill_pt_sections(cache: dict) -> None:
    need: list[str] = []
    for rec in cache.values():
        if rec.get("missing"):
            rec.setdefault("has_pt", False)
            continue
        title = rec.get("resolved")
        if not title:
            rec["has_pt"] = False
            continue
        if rec.get("has_pt") is not None and rec.get("wikitext_checked"):
            continue
        need.append(title)
    seen: set[str] = set()
    titles = []
    for t in need:
        if t not in seen:
            seen.add(t)
            titles.append(t)
    pt_map: dict[str, bool] = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i : i + 20]
        data = api(
            {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "titles": "|".join(chunk),
            }
        )
        for p in (data.get("query") or {}).get("pages") or []:
            title = p.get("title") or ""
            if p.get("missing"):
                pt_map[title] = False
                continue
            revs = p.get("revisions") or []
            content = ""
            if revs:
                content = (
                    revs[0].get("slots", {}).get("main", {}).get("content")
                    or revs[0].get("content")
                    or ""
                )
            pt_map[title] = bool(PT_MARK.search(content))
        time.sleep(0.2)
    for rec in cache.values():
        if rec.get("missing"):
            rec["has_pt"] = False
            continue
        title = rec.get("resolved")
        if title in pt_map:
            rec["has_pt"] = pt_map[title]
            rec["wikitext_checked"] = True


def extract_html_dict(html: str) -> list[tuple[str, str]]:
    """(href_title, span_text) for each dict stamp."""
    out: list[tuple[str, str]] = []
    for m in DICT_HREF.finditer(html):
        attrs, inner = m.group(1), m.group(2)
        href_m = re.search(r'href=["\']([^"\']+)["\']', attrs)
        if not href_m:
            continue
        href = htmlmod.unescape(href_m.group(1))
        path = unquote(urlparse(href).path)
        title = path.rsplit("/wiki/", 1)[-1].replace("_", " ")
        span = re.sub(r"<[^>]+>", "", inner)
        span = htmlmod.unescape(span).strip()
        if title:
            out.append((nfc(title), nfc(span)))
    return out


def book_html(root: Path, book: str) -> str:
    body = root / book / "body.html"
    if body.exists():
        return body.read_text(encoding="utf-8")
    bookj = root / book / "book.json"
    if not bookj.exists():
        return ""
    data = json.loads(bookj.read_text(encoding="utf-8"))
    pages = data.get("pages") or []
    if pages and "html" in pages[0]:
        return pages[0]["html"] or ""
    return ""


def resolve_one(title: str, cache: dict) -> dict:
    """Pick the best existing page for a stamped title."""

    def hit(v: str, via: str) -> dict | None:
        rec = cache.get(v)
        if rec and not rec.get("missing") and rec.get("has_pt"):
            if via == "exact" and (rec.get("redirect") or rec.get("normalized")):
                via = "redirect"
            return {
                "ok": True,
                "via": via,
                "canonical": rec["resolved"],
                "tried": v,
            }
        return None

    # Prefer the lowercase lemma when both casings exist (common-noun titles).
    if title:
        low = title[0].lower() + title[1:]
        found = hit(low, "exact" if low == title else "case")
        if found:
            return found
        folded = title.casefold()
        if folded != low:
            found = hit(folded, "case")
            if found:
                return found
    for v in case_variants(title):
        found = hit(v, "exact" if v == title else "case")
        if found:
            return found
    for inf in inflection_candidates(title):
        for v in case_variants(inf):
            found = hit(v, "inflection")
            if found:
                return found
    rec = cache.get(title) or {}
    reason = "missing"
    if rec and not rec.get("missing") and rec.get("has_pt") is False:
        reason = "no-pt"
    return {"ok": False, "via": reason, "canonical": None, "tried": title}


def dump_json(path: Path, data) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", nargs="*", default=["lde", "ldm", "ese", "ceu", "gen"])
    ap.add_argument(
        "--html",
        action="append",
        default=[],
        help="Extra HTML files (e.g. a live body.html dump)",
    )
    args = ap.parse_args()

    shell = find_shell_books()
    cache_path = CAT / "dict-api-cache.json"
    cache: dict = {}
    if cache_path.exists():
        try:
            prev = json.loads(cache_path.read_text(encoding="utf-8"))
            cache = prev.get("pages") or {}
        except json.JSONDecodeError:
            cache = {}

    surfaces: dict[str, set[str]] = defaultdict(set)  # title -> books
    span_for: dict[str, set[str]] = defaultdict(set)  # title -> span texts

    for book in args.books:
        html = book_html(shell, book)
        if not html:
            print(f"skip {book}: no html", file=sys.stderr)
            continue
        for title, span in extract_html_dict(html):
            surfaces[title].add(book)
            if span:
                span_for[title].add(span)

    for i, path in enumerate(args.html):
        html = Path(path).read_text(encoding="utf-8")
        tag = Path(path).stem or f"html{i}"
        for title, span in extract_html_dict(html):
            surfaces[title].add(tag)
            if span:
                span_for[title].add(span)

    if not surfaces:
        print("no dict stamps found", file=sys.stderr)
        return 1

    lookup: list[str] = []
    seen: set[str] = set()
    for title in surfaces:
        for v in case_variants(title):
            if v not in seen:
                seen.add(v)
                lookup.append(v)
        for inf in inflection_candidates(title):
            for v in case_variants(inf):
                if v not in seen:
                    seen.add(v)
                    lookup.append(v)

    print(f"stamped titles {len(surfaces)}; API lookup {len(lookup)}")
    query_titles(lookup, cache)
    fill_pt_sections(cache)

    allow_by_canon: dict[str, dict] = {}
    missing_rows: list[dict] = []

    for title in sorted(surfaces, key=lambda s: fold(s)):
        hit = resolve_one(title, cache)
        books = sorted(surfaces[title])
        lemmas = sorted(
            {title, *span_for[title]},
            key=lambda s: (fold(s), s),
        )
        if hit["ok"]:
            canon = hit["canonical"]
            row = allow_by_canon.setdefault(
                canon,
                {
                    "title": canon,
                    "lemmas": [],
                    "via": hit["via"],
                    "books": [],
                },
            )
            for lem in lemmas + [canon, title]:
                if lem not in row["lemmas"]:
                    row["lemmas"].append(lem)
            for b in books:
                if b not in row["books"]:
                    row["books"].append(b)
            rank = {"exact": 0, "redirect": 1, "case": 2, "inflection": 3}
            if rank.get(hit["via"], 9) < rank.get(row.get("via"), 9):
                row["via"] = hit["via"]
        else:
            missing_rows.append(
                {
                    "title": title,
                    "reason": hit["via"],
                    "books": books,
                }
            )

    allow_rows = [allow_by_canon[k] for k in sorted(allow_by_canon, key=fold)]
    for row in allow_rows:
        row["lemmas"] = sorted(set(row["lemmas"]), key=lambda s: (fold(s), s))
        row["books"] = sorted(set(row["books"]))
    missing_rows.sort(key=lambda r: fold(r["title"]))

    CAT.mkdir(parents=True, exist_ok=True)
    dump_json(CAT / "dict-allowlist.json", allow_rows)
    dump_json(CAT / "dict-missing.json", missing_rows)
    dump_json(
        cache_path,
        {
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pages": cache,
        },
    )

    n_case = sum(1 for r in allow_rows if r.get("via") == "case")
    n_inf = sum(1 for r in allow_rows if r.get("via") == "inflection")
    n_nopt = sum(1 for r in missing_rows if r["reason"] == "no-pt")
    print(
        f"allow {len(allow_rows)} (case {n_case}, inflection {n_inf})  "
        f"missing {len(missing_rows)} (no-pt {n_nopt})"
    )
    print(f"wrote {CAT / 'dict-allowlist.json'}")
    print(f"wrote {CAT / 'dict-missing.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
