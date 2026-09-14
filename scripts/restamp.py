#!/usr/bin/env python3
"""Restamp spiritism HTML: Luz → map → wiki → capped dict; Bible cites only."""

from __future__ import annotations

import html as htmlmod
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "catalogs"


def find_shell_books() -> Path:
    env = os.environ.get("LIBRUS_SHELL_BOOKS")
    if env:
        return Path(env)
    candidates = [
        ROOT.parent / "librus-shell" / "public" / "books",
        Path("/home/sergioshklr/librus-shell/public/books"),
        Path("/home/user/dev/librus-shell/public/books"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise SystemExit(
        "cannot find librus-shell/public/books (set LIBRUS_SHELL_BOOKS)"
    )


SHELL = find_shell_books()

WORD = re.compile(r"[\wÀ-ÿ]")
STOP = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "um", "uma",
    "para", "por", "com", "que", "se", "não", "nao", "na", "no", "nas", "nos",
    "ao", "aos", "à", "às", "é", "ser", "são", "sao", "foi", "como", "mais",
    "mas", "ou", "seu", "sua", "seus", "suas", "este", "esta", "isso", "ele",
    "ela", "eles", "elas", "lhe", "lhes", "pelo", "pela", "pelos", "pelas",
    "entre", "sobre", "até", "ate", "quando", "muito", "já", "ja", "também",
    "tambem", "há", "ha", "tem", "ter", "pode", "essa", "esse", "isto",
    "aquele", "aquela", "onde", "porque", "pois", "assim", "ainda", "só",
    "so", "mesmo", "todos", "todas", "outro", "outra", "depois", "antes",
    "sem", "sob", "num", "numa", "nos", "vos", "eu", "tu", "nós", "vós",
    "me", "te", "lhe", "lhes", "minha", "meu", "nossa", "nosso", "pela",
    "era", "sendo", "ter", "sido", "muito", "pouco", "bem",  # Bem is Luz exact
    "disse", "então", "entao", "obra", "parte", "forma", "modo", "vez",
    "vezes", "todo", "toda", "cada", "qualquer", "alguns", "algumas",
    "este", "estes", "estas", "isso", "aquilo", "aqui", "ali", "lá", "la",
    "há", "havia", "são", "estão", "esta", "está", "foi", "foram", "será",
    "seria", "pode", "podem", "deve", "devem", "há",
}

# Keep these as Luz even though short
LUZ_SHORT = {"fé", "mal", "bem"}

BIBLE_BOOKS = {
    "mateus": ("MAT", "Mateus,_o_Evangelista", "Mateus"),
    "marcos": ("MRK", "Marcos,_o_Evangelista", "Marcos"),
    "lucas": ("LUK", "Lucas,_o_Evangelista", "Lucas"),
    "joão": ("JHN", "João,_o_Evangelista", "João"),
    "joao": ("JHN", "João,_o_Evangelista", "João"),
    "joão evangelista": ("JHN", "João,_o_Evangelista", "João"),
    "gênesis": ("GEN", "Gênesis", "Gênesis"),
    "genesis": ("GEN", "Gênesis", "Gênesis"),
    "êxodo": ("EXO", "Êxodo", "Êxodo"),
    "exodo": ("EXO", "Êxodo", "Êxodo"),
    "exôdo": ("EXO", "Êxodo", "Êxodo"),
    "levítico": ("LEV", "Levítico", "Levítico"),
    "números": ("NUM", "Números", "Números"),
    "deuteronômio": ("DEU", "Deuteronômio", "Deuteronômio"),
    "josué": ("JOS", "Josué", "Josué"),
    "juízes": ("JDG", "Livro_dos_Juízes", "Juízes"),
    "rute": ("RUT", "Livro_de_Rute", "Rute"),
    "samuel": ("1SA", "Livro_de_Samuel", "Samuel"),
    "reis": ("1KI", "Livros_dos_Reis", "Reis"),
    "jó": ("JOB", "Livro_de_Jó", "Jó"),
    "jo": ("JOB", "Livro_de_Jó", "Jó"),
    "salmos": ("PSA", "Livro_de_Salmos", "Salmos"),
    "provérbios": ("PRO", "Livro_de_Provérbios", "Provérbios"),
    "eclesiastes": ("ECC", "Eclesiastes", "Eclesiastes"),
    "isaías": ("ISA", "Isaías", "Isaías"),
    "isaias": ("ISA", "Isaías", "Isaías"),
    "jeremias": ("JER", "Jeremias_(profeta)", "Jeremias"),
    "ezequiel": ("EZE", "Ezequiel", "Ezequiel"),
    "daniel": ("DAN", "Daniel_(profeta)", "Daniel"),
    "oseias": ("HOS", "Oseias", "Oseias"),
    "joel": ("JOL", "Joel_(profeta)", "Joel"),
    "amós": ("AMO", "Amós", "Amós"),
    "jonas": ("JON", "Jonas_(profeta)", "Jonas"),
    "miqueias": ("MIC", "Miqueias", "Miqueias"),
    "habacuque": ("HAB", "Habacuque", "Habacuque"),
    "ageu": ("HAG", "Ageu", "Ageu"),
    "zacarias": ("ZEC", "Zacarias_(profeta)", "Zacarias"),
    "malaquias": ("MAL", "Malaquias", "Malaquias"),
    "atos": ("ACT", "Atos_dos_Apóstolos", "Atos"),
    "romanos": ("ROM", "Epístola_aos_Romanos", "Romanos"),
    "coríntios": ("1CO", "Primeira_Epístola_aos_Coríntios", "Coríntios"),
    "gálatas": ("GAL", "Epístola_aos_Gálatas", "Gálatas"),
    "efésios": ("EPH", "Epístola_aos_Efésios", "Efésios"),
    "filipenses": ("PHP", "Epístola_aos_Filipenses", "Filipenses"),
    "colossenses": ("COL", "Epístola_aos_Colossenses", "Colossenses"),
    "tessalonicenses": ("1TH", "Primeira_Epístola_aos_Tessalonicenses", "Tessalonicenses"),
    "timóteo": ("1TI", "Primeira_Epístola_a_Timóteo", "Timóteo"),
    "tito": ("TIT", "Epístola_a_Tito", "Tito"),
    "hebreus": ("HEB", "Epístola_aos_Hebreus", "Hebreus"),
    "tiago": ("JAS", "Epístola_de_Tiago", "Tiago"),
    "pedro": ("1PE", "Primeira_Epístola_de_Pedro", "Pedro"),
    "apocalipse": ("REV", "Apocalipse", "Apocalipse"),
    "decálogo": ("EXO", "Decálogo", "Decálogo"),
}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFC", s)
    return s.casefold().strip()


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def derive_keys(title: str) -> list[str]:
    t = nfc(title).strip()
    out = [t]
    for pref in ("O ", "A ", "Os ", "As "):
        if t.startswith(pref) or t.startswith(pref.lower()):
            out.append(t[len(pref) :])
    if not t.endswith(("s", "S")) and len(t) >= 3:
        out.append(t + "s")
    if t.endswith("m") and len(t) >= 4:
        out.append(t[:-1] + "ns")  # médium → médiuns
    return out


def load_index() -> list[tuple[str, int, str, str, str]]:
    """(fold_key, length, provider, canon, href) longest-first."""
    rows: list[tuple[str, int, str, str, str]] = []

    def add(key: str, prov: str, canon: str, href: str) -> None:
        k = fold(key)
        if len(k) < 3 and k not in LUZ_SHORT:
            return
        rows.append((k, len(k), prov, canon, href))

    luz = json.loads((CAT / "luz-articles.json").read_text(encoding="utf-8"))
    for a in luz:
        item = a["item"]
        href = (
            "https://www.luzespirita.org.br/index.php?lisPage=enciclopedia&item="
            + quote(item, safe="")
        )
        keys = [a["title"], item] + list(a.get("aliases") or [])
        if item == "Espírita":
            keys += ["Espírito", "Espíritos"]
        for k in keys:
            for d in derive_keys(k):
                add(d, "l", item, href)

    places = json.loads((CAT / "places.json").read_text(encoding="utf-8"))
    for p in places:
        q = p["query"]
        href = "https://www.openstreetmap.org/search?query=" + quote(q, safe="")
        for k in [p["title"], q] + list(p.get("lemmas") or []):
            add(k, "m", q, href)

    wiki = json.loads((CAT / "wiki-allowlist.json").read_text(encoding="utf-8"))
    for w in wiki:
        title = w["title"]
        href = "https://pt.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe="_:")
        for k in [title] + list(w.get("lemmas") or []):
            add(k, "w", title, href)

    # later keys of same fold keep first (luz beats map beats wiki if we add luz first
    # and skip dupes). Longest still wins at match time.
    best: dict[str, tuple[str, int, str, str, str]] = {}
    rank = {"l": 0, "m": 1, "w": 2, "d": 3}
    for rec in rows:
        k = rec[0]
        prev = best.get(k)
        if prev is None or rank[rec[2]] < rank[prev[2]]:
            best[k] = rec
    out = list(best.values())
    out.sort(key=lambda r: (-r[1], rank[r[2]]))
    return out


def extract_dict_lemmas(html: str) -> set[str]:
    lemmas: set[str] = set()
    for m in re.finditer(
        r'<a\b[^>]*data-link-provider=["\']d["\'][^>]*>(.*?)</a>',
        html,
        re.I | re.S,
    ):
        t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        t = fold(t)
        if t and t not in STOP and len(t) >= 4:
            lemmas.add(t)
    return lemmas


def load_dict_catalog() -> tuple[dict[str, str], set[str]]:
    """fold(lemma) → canonical Wiktionary title; missing folds never stamp."""
    mapping: dict[str, str] = {}
    missing: set[str] = set()
    miss_p = CAT / "dict-missing.json"
    allow_p = CAT / "dict-allowlist.json"
    if miss_p.exists():
        for row in json.loads(miss_p.read_text(encoding="utf-8")):
            missing.add(fold(row["title"]))
            for lem in row.get("lemmas") or []:
                missing.add(fold(lem))
    if allow_p.exists():
        for row in json.loads(allow_p.read_text(encoding="utf-8")):
            title = row["title"]
            for lem in [title] + list(row.get("lemmas") or []):
                k = fold(lem)
                if k not in missing:
                    mapping[k] = title
    return mapping, missing


def dict_href(canon: str) -> str:
    return "https://pt.wiktionary.org/wiki/" + quote(
        canon.replace(" ", "_"), safe="_:"
    )


def unwrap_providers(html: str) -> str:
    def keep_link(tag: str) -> bool:
        href = re.search(r'href=["\']([^"\']+)["\']', tag)
        if not href:
            return False
        h = htmlmod.unescape(href.group(1))
        if h.startswith("#"):
            return True
        if "kardecpedia.com" in h.lower():
            return True
        if "luzespirita" in h or "wiktionary" in h or "wikipedia.org" in h:
            return False
        # Keep bible.com outside .bible-block (GEN cites). Blocks are rewritten
        # from the last paragraph; unwrapping those hrefs would drop them.
        if "bible.com" in h:
            return True
        if "openstreetmap" in h:
            return False
        if re.search(r'data-link-provider=', tag):
            return False
        return True

    def repl(m: re.Match) -> str:
        tag, inner = m.group(1), m.group(2)
        if keep_link(tag):
            return m.group(0)
        return inner

    return re.sub(r"<a\b([^>]*)>(.*?)</a>", repl, html, flags=re.I | re.S)


def a_tag(href: str, prov: str, text: str, extra: str = "") -> str:
    extra = extra or ""
    return (
        f'<a href="{htmlmod.escape(href, quote=True)}" '
        f'data-link-provider="{prov}" data-doutrina-link="1"{extra}>'
        f"{text}</a>"
    )


def first_verse(vers: str) -> str:
    m = re.search(r"\d+", vers)
    return m.group(0) if m else "1"


def normalize_cite_blob(text: str) -> str:
    text = htmlmod.unescape(text)
    text = re.sub(r"🎬\([^)]*\)", "", text)
    text = re.sub(r"\{:[^}]+\}", "", text)
    text = re.sub(r"\b(Mateus)Mt\b", r"\1", text, flags=re.I)
    text = re.sub(r"\b(Marcos)Mc\b", r"\1", text, flags=re.I)
    text = re.sub(r"\b(Lucas)Lc\b", r"\1", text, flags=re.I)
    text = re.sub(r"\b(João)Jo\b", r"\1", text, flags=re.I)
    text = re.sub(
        r"cap\.\s*0*(\d+)(?:Mt|Mc|Lc|Jo)?(?:0*\1)?",
        r"cap. \1",
        text,
        flags=re.I,
    )
    # Prior restamp ate “A” from ARC into the verse (e.g. “14, A, A, ARC”).
    text = re.sub(r"(?:,\s*)?(?:A\s*,\s*)+ARC\b", " ARC", text, flags=re.I)
    text = re.sub(r",?\s*A\.?\s*R\.?\s*C\.?\b", " ARC", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" ,;")
    return text


CITE_ONE = re.compile(
    r"(?P<book>[A-Za-zÁÉÍÓÚÂÊÔÃÕáéíóúâêôãõçÇ][A-Za-zÁÉÍÓÚÂÊÔÃÕáéíóúâêôãõçÇ\- ]*?)"
    r",?\s*cap\.\s*(?P<ch>\d+)\s*[.,]?\s*vers\.\s*"
    r"(?P<vs>\d+(?:\s*[-–]\s*\d+)?(?:\s*(?:a|e|,)\s*\d+(?:\s*[-–]\s*\d+)?)*)",
    re.I,
)


def render_one_cite(book: str, ch: str, vs: str) -> str | None:
    bk = fold(book).strip(" .")
    if bk in {"livro", "x", "idem", "ibidem"}:
        return None
    if bk not in BIBLE_BOOKS:
        return None
    code, wiki, label = BIBLE_BOOKS[bk]
    ch_n = str(int(ch))
    vs_disp = re.sub(r"\s+", " ", vs).strip(" .,;")
    vs_disp = vs_disp.replace(" a ", "-").replace(" e ", ", ")
    vs_disp = re.sub(r"(?:,\s*)?\bA\b", "", vs_disp).strip(" ,;")
    v1 = first_verse(vs_disp)
    book_href = "https://pt.wikipedia.org/wiki/" + wiki
    ch_href = f"https://pt.wikipedia.org/wiki/{wiki.split(',')[0]}_{ch_n}"
    # Mateus,_o_Evangelista → Mateus_5
    ch_page = {
        "MAT": "Mateus",
        "MRK": "Marcos",
        "LUK": "Lucas",
        "JHN": "João",
        "GEN": "Gênesis",
        "EXO": "Êxodo",
        "ISA": "Isaías",
        "JOB": "Jó",
        "EZE": "Ezequiel",
        "JOL": "Joel",
        "ACT": "Atos_dos_Apóstolos",
        "ROM": "Romanos",
        "JER": "Jeremias",
        "REV": "Apocalipse",
        "DEU": "Deuteronômio",
    }.get(code, wiki.split(",")[0])
    ch_href = f"https://pt.wikipedia.org/wiki/{ch_page}_{ch_n}"
    bib_href = f"https://www.bible.com/pt/bible/212/{code}.{ch_n}.{v1}.ARC"
    arc_href = (
        "https://www.bible.com/pt/versions/212-arc-almeida-revista-e-corrigida"
    )
    extra = ' data-bible-cite="1"'
    return (
        a_tag(book_href, "w", label, extra)
        + ", "
        + a_tag(ch_href, "w", f"cap. {ch_n}", extra)
        + ", "
        + a_tag(bib_href, "bible", f"vers. {vs_disp}", extra)
        + ", "
        + a_tag(arc_href, "bible", "ARC", extra)
    )


def rewrite_bible_block(block: str) -> str:
    body_m = re.search(
        r'(<div class="bible-block"><div class="bible-body">)(.*)(</div></div>)\s*$',
        block,
        re.S,
    )
    if not body_m:
        return block
    prefix, inner, suffix = body_m.group(1), body_m.group(2), body_m.group(3)
    ps = list(re.finditer(r"<p(?:\s[^>]*)?>(.*?)</p>", inner, re.S))
    if not ps:
        return block
    last = ps[-1]
    raw = re.sub(r"<[^>]+>", " ", last.group(1))
    blob = normalize_cite_blob(raw)
    if not re.search(r"cap\.\s*\d+", blob, re.I):
        return block
    parts = []
    for m in CITE_ONE.finditer(blob):
        rendered = render_one_cite(m.group("book"), m.group("ch"), m.group("vs"))
        if rendered:
            parts.append(rendered)
    if not parts:
        return block
    new_p = '<p class="bible-cite">' + "; ".join(parts) + "</p>"
    inner2 = inner[: last.start()] + new_p + inner[last.end() :]
    return prefix + inner2 + suffix


def restamp_bible_blocks(html: str) -> str:
    return re.sub(
        r'<div class="bible-block"><div class="bible-body">.*?</div></div>',
        lambda m: rewrite_bible_block(m.group(0)),
        html,
        flags=re.S,
    )


AUTHOR_LAST_P = re.compile(
    r"^(?:\s*<strong>.*?</strong>\s*(?:<br\s*/?>)?\s*)+$",
    re.S,
)


def unwrap_spirit_authors(html: str) -> str:
    """Drop **bold** on spirit signature lines (last p is only <strong> names)."""

    def one(m: re.Match) -> str:
        prefix, inner, suffix = m.group(1), m.group(2), m.group(3)
        ps = list(re.finditer(r"<p(?:\s[^>]*)?>(.*?)</p>", inner, re.S))
        if not ps:
            return m.group(0)
        last = ps[-1]
        inner_p = last.group(1).strip()
        if inner_p.startswith("✨"):
            return m.group(0)
        if not (
            AUTHOR_LAST_P.fullmatch(last.group(1)) or "<strong>" in last.group(1)
        ):
            return m.group(0)
        new_p = "<p>" + re.sub(r"</?strong>", "", last.group(1)) + "</p>"
        inner2 = inner[: last.start()] + new_p + inner[last.end() :]
        return prefix + inner2 + suffix

    return re.sub(
        r'(<div class="spirit-block"><div class="spirit-body">)(.*?)(</div></div>)',
        one,
        html,
        flags=re.S,
    )


def bound_start(text: str, i: int) -> bool:
    """True only at the start of a word — never on space, dash, or emoji."""
    if i >= len(text) or not WORD.match(text[i]):
        return False
    if i == 0:
        return True
    return not WORD.match(text[i - 1])


def bound_end(text: str, j: int) -> bool:
    if j >= len(text):
        return True
    return not WORD.match(text[j])


def stamp_text(
    text: str,
    index: list[tuple[str, int, str, str, str]],
    dict_map: dict[str, str],
    dict_missing: set[str],
    used: set[tuple[str, str]],
    dict_in_p: list[int],
) -> str:
    if not text or not any(c.isalpha() for c in text):
        return text
    folded = fold(text)
    # fold() lowercases but length may differ from NFC text if we only casefold
    # NFC casefold is length-stable for PT.
    src = nfc(text)
    folded_src = src.casefold()
    if len(folded_src) != len(src):
        folded_src = src  # safety: match on original with IGNORECASE via fold keys
        # Use per-char walk on src with fold of slices
    out: list[str] = []
    i = 0
    n = len(src)
    while i < n:
        if not bound_start(src, i):
            out.append(src[i])
            i += 1
            continue
        hit = None
        for key, klen, prov, canon, href in index:
            if i + klen > n:
                continue
            sl = src[i : i + klen]
            if fold(sl) != key:
                continue
            if not bound_end(src, i + klen):
                continue
            hit = (klen, prov, canon, href, sl)
            break
        if hit is None:
            # dict leftover: single token
            j = i + 1
            while j < n and WORD.match(src[j]):
                j += 1
            tok = src[i:j]
            ft = fold(tok)
            canon = dict_map.get(ft)
            already = ("d", fold(canon)) in used if canon else False
            if (
                j > i
                and WORD.match(src[i])
                and tok == tok.strip()
                and canon
                and ft not in dict_missing
                and ft not in STOP
                and not already
                and dict_in_p[0] < 2
            ):
                href = dict_href(canon)
                out.append(a_tag(href, "d", tok))
                used.add(("d", fold(canon)))
                dict_in_p[0] += 1
                i = j
                continue
            out.append(src[i])
            i += 1
            continue
        klen, prov, canon, href, sl = hit
        sig = (prov, fold(canon))
        if sig in used:
            out.append(sl)
            i += klen
            continue
        if prov == "d" and dict_in_p[0] >= 2:
            out.append(sl)
            i += klen
            continue
        extra = ' data-bible-cite="1"' if False else ""
        out.append(a_tag(href, prov, sl, extra))
        used.add(sig)
        if prov == "d":
            dict_in_p[0] += 1
        i += klen
    return "".join(out)


SKIP_TAGS = {
    "a",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "script",
    "style",
    "code",
    "pre",
    "summary",
}


def stamp_html(
    html: str,
    index,
    dict_map: dict[str, str],
    dict_missing: set[str],
) -> str:
    parts = re.split(r"(<[^>]+>)", html)
    stack: list[str] = []
    used: set[tuple[str, str]] = set()
    dict_in_p = [0]
    out: list[str] = []
    in_bible_cite = False
    bible_depth = 0

    def skipped() -> bool:
        return in_bible_cite or bible_depth > 0 or any(t in SKIP_TAGS for t in stack)

    for part in parts:
        if part.startswith("</"):
            name = re.match(r"</([a-zA-Z0-9]+)", part)
            tag = name.group(1).lower() if name else ""
            if stack and stack[-1] == tag:
                stack.pop()
            if tag == "strong":
                in_bible_cite = False
            if tag == "div" and bible_depth:
                bible_depth -= 1
            out.append(part)
            continue
        if part.startswith("<"):
            name = re.match(r"<([a-zA-Z0-9]+)", part)
            tag = name.group(1).lower() if name else ""
            self_close = part.endswith("/>")
            if tag in {"h3", "h4", "h5"}:
                used = set()
            if tag == "p":
                dict_in_p[0] = 0
            if tag == "strong" and "bible-cite" in part:
                in_bible_cite = True
            if tag == "div":
                if bible_depth:
                    bible_depth += 1
                elif "bible-block" in part:
                    bible_depth = 1
            if tag and not self_close:
                stack.append(tag)
            out.append(part)
            continue
        if skipped():
            out.append(part)
        else:
            out.append(
                stamp_text(part, index, dict_map, dict_missing, used, dict_in_p)
            )
    return "".join(out)


def drop_excess_dict(html: str, max_frac: float = 0.33) -> str:
    """Keep dict ≤ max_frac of all provider links (dict ≤ non_dict * max_frac/(1-max_frac))."""
    provs = re.findall(r'data-link-provider="([^"]+)"', html)
    n_dict = sum(1 for p in provs if p == "d")
    n_other = len(provs) - n_dict
    cap = int(n_other * max_frac / (1.0 - max_frac))
    extra = n_dict - cap
    if extra <= 0:
        return html
    dropped = 0
    for m in reversed(
        list(
            re.finditer(
                r'<a\b[^>]*data-link-provider="d"[^>]*>(.*?)</a>', html, re.S
            )
        )
    ):
        if dropped >= extra:
            break
        html = html[: m.start()] + m.group(1) + html[m.end() :]
        dropped += 1
    return html


def restamp(html: str) -> str:
    dict_map, dict_missing = load_dict_catalog()
    if not dict_map:
        for lem in extract_dict_lemmas(html):
            if lem not in dict_missing:
                dict_map[lem] = lem
    index = load_index()
    html = unwrap_providers(html)
    html = restamp_bible_blocks(html)
    html = unwrap_spirit_authors(html)
    html = stamp_html(html, index, dict_map, dict_missing)
    html = drop_excess_dict(html, 0.33)
    return html


def count_prov(html: str) -> dict[str, int]:
    from collections import Counter

    c = Counter(re.findall(r'data-link-provider="([^"]+)"', html))
    return dict(c)


def process_book(book: str) -> None:
    root = SHELL / book
    body = root / "body.html"
    bookj = root / "book.json"
    if body.exists():
        raw = body.read_text(encoding="utf-8")
        new = restamp(raw)
        body.write_text(new, encoding="utf-8")
        print(f"{book} body.html {count_prov(raw)} → {count_prov(new)}")
        if bookj.exists():
            data = json.loads(bookj.read_text(encoding="utf-8"))
            pages = data.get("pages") or []
            if pages and "html" in pages[0]:
                pages[0]["html"] = new
                bookj.write_text(
                    json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                    encoding="utf-8",
                )
        return
    data = json.loads(bookj.read_text(encoding="utf-8"))
    pages = data.get("pages") or []
    raw = pages[0]["html"]
    new = restamp(raw)
    pages[0]["html"] = new
    bookj.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"{book} book.json {count_prov(raw)} → {count_prov(new)}")


def main() -> int:
    books = sys.argv[1:] or ["lde", "ldm", "ese", "ceu", "gen"]
    for b in books:
        process_book(b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
