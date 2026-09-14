# Link methodology

**Packs:** `general` (Holmes / secular) · `spiritism` (Kardec five + notes)  
Stamp the **book**. The shell allowlist only *shows* providers (Librus: wiki · dict · map).

One span, one provider. First match wins.

---

## 1. Shared core

1. Do not link stopwords, chrome, or headings used only as structure.  
2. Do not wrap a span that is already a serial (`#s0964`) or an off-book URL.  
3. Map (`m`) is places when a map is more useful than a wiki article.  
4. Select-to-search in Consulte still works on unstamped text.

---

## 2. Pack `general` (Sherlock Holmes)

Entities, not vocabulary.

| Span | Provider |
|------|----------|
| Person, work, institution | Wikipedia (`w`) |
| City, street, region | Map (`m`), else wiki |
| Period / jargon the reader will miss | Wiktionary (`d`) — first hit per section |
| Everything else | unstamped |

No Luz, Bible-as-doctrine, or Kardecpedia.

---

## 3. Pack `spiritism` — priority

**Luz → Map (places) → Wikipedia → Wiktionary → Bible (cites only).**  
Kardecpedia is not in this ladder (see §5).

### 3.1 Luz (`l`) — maximize (catalog first)

The matcher is driven by a **full Luz encyclopedia listing** (`catalogs/luz-articles.json`), not by a hand-picked lemma list.

**Catalog** — one object per article, at least:

```json
{ "item": "Perispírito", "title": "Perispírito", "aliases": ["perispirito"] }
```

`item` is the `?item=` query (same encoding Luz uses). Extra aliases optional; the injector also derives them.

**Index (build once from JSON)**

1. Key = NFC, lowercased title / `item` / aliases.  
2. Derive: strip leading *o/a/os/as*; simple PT plural (*Espírito* ↔ *Espíritos*); adjective where the article is the noun (*Espírita* → *espírita*).  
3. Sort keys **longest first** so *Doutrina Espírita* wins over *Doutrina* or *Espírita*.  
4. Drop keys shorter than 3 letters unless they are an exact catalog `item` (*Fé*, *Mal*, *Bem*).

**Scan (spiritism books only)**

1. Walk visible text (not headings-as-chrome, not existing links, not `{#serials}`).  
2. Longest catalog key that matches a token/phrase → stamp Luz, `href` =  
   `https://www.luzespirita.org.br/index.php?lisPage=enciclopedia&item={item}`.  
3. Non-verbatim is expected: the span in the book can be *espíritas* while `item` is `Espírita`.  
4. **Once per lemma per H5 / section.** Later hits stay plain.  
5. Do not stamp if the span is already a five-book serial or an off-shelf Kardecpedia title.

Only after this pass: map (places), then Wikipedia, then capped Wiktionary.

### 3.2 Map (`m`) — places

If Luz did not take the span and it is a **toponym**: OpenStreetMap, `data-link-provider="m"`.

Gazetteer: `catalogs/places.json` (seeded from Wikipedia toponyms in the five books: Paris, Lyon, França, Rio de Janeiro, …). Once per lemma per H5 / section.

Do **not** map people, works, doctrines, or bible books. If Luz has a location article (*Palais-Royal*, *Museu AKOL*), Luz still wins.

### 3.3 Wikipedia (`w`) — after places

Allowlist: `catalogs/wiki-allowlist.json` — lemma → canonical `pt.wikipedia` title. Seeded from current five-book stamps, minus Luz overlap and minus places.

Not a Wikipedia dump. Disambiguation lives here (*João, o Evangelista*, *Almeida Revista e Corrigida* for ARC).

Bible **chapter** wiki pages (*Mateus 13*) stay on the cite line only — not in this allowlist.

Same once-per-section cap for a given article.

### 3.4 Wiktionary (`d`) — remainder, capped, existence-checked

Only if neither Luz nor wiki claimed it, and the word still helps study (not *disse*, *então*, *obra*).

**Existence (librus-linker#1):** do not stamp a dict href unless `pt.wiktionary` has that page. Audit: `python3 scripts/audit_dict.py` batch-queries `action=query` (≤50 titles, `redirects=1`). Writes `catalogs/dict-allowlist.json` + `catalogs/dict-missing.json`. Restamp uses the allowlist canonical title (so `Providência` → `providência`; first letter is significant on Wiktionary). Conservative inflection only (`existências` → `existência`). No opensearch neighbor swaps (`espiritualista` is not `espiritualismo`). Pages without a Português section (`{{-pt-}}`) go on missing.

Do **not** `HEAD` the article URL — MediaWiki soft-404s.

**Balance (source lists are lopsided; dict must not flood):**

1. **First lemma per H5 / section** — later copies stay plain.  
2. **At most 2 dict spans per paragraph.**  
3. After inject, dict should not exceed **about one third** of in-book links in a book. If it does, drop extra dict spans (keep Luz/wiki).  
4. Target mix of stamped spans (spiritism running text, excluding bible blocks): **Luz plurality**, wiki clearly visible, dict a support layer — not 80% dict (current LDE stamp is inverted: ~5.2k `d` · ~0.9k `l` · ~0.3k `w`).

### 3.5 Bible (`bible`) — quotes only, specified cite

Never stamp running words (*Deus*, *evangelho*, *pecado*) as Bible.

Only inside `.bible-block` / `.bible-cite`, split as today:

| Token | Provider |
|-------|----------|
| Book name (Mateus, João, Gênesis) | Wikipedia |
| **cap. N** (label includes `cap.`) | Wikipedia chapter page |
| **vers. N** (label includes `vers.`) | Bible.com ARC (`bible.com/pt/bible/212/…ARC`) |
| Translation label (ARC) | Bible.com version page (`/pt/versions/212-arc-…`) |

The verse token is the only `data-link-provider="bible"` on that line.

---

## 4. In-shelf vs off-shelf (Kardecpedia)

The five featured books — LDE · LDM · ESE · CEU · GEN — stay **in-app** (serials). Never Kardecpedia.

**Kardecpedia (`kardec`) only** for a title that is **not** one of those five:

- *Revista Espírita* (issue / month / year)  
- *O Que é o Espiritismo*  
- *Obras Póstumas*  
- opúsculos and other extra-shelf works  

Canonical example: shared **Nota Explicativa** (`::: kardec` + *Revista Espírita* → kardecpedia.com; *O Livro dos Espíritos* Q.207 stays local).

---

## 5. Flavor vs book

| Book profile | Stamps |
|--------------|--------|
| `spiritism` | Luz, wiki, dict, map, bible-cites, kardec off-shelf |
| `general` | wiki, dict (capped), map |

A Kardec book on Librus still carries Luz stamps; the shell hides the Luz button. A Holmes book never gets `l` / `bible` / `kardec`.

---

## 6. Markup

```html
<a href="…" data-link-provider="l|w|d|m|bible|kardec"
   data-doutrina-link="1">…</a>
```

`data-doutrina-link` only on spiritism stamps. Holmes uses `g-link` + provider, no doutrina flag.

Do not stamp `data-link-interest`. Priority and caps replace lo/med/hi.
