# librus-linker

Provider **link injection** for LIBRUS reader artifacts.

Takes built content from **`doutrina-content`** (and later other `*-content` shelves) and enriches HTML/MD with provider anchors (Luz, wiki/encyc, dict, maps, Bible, Kardecpedia, …). Output is consumed by **`librus-shell`** at assemble/deploy time.

This repo owns **tooling you wrote**, not the book texts.

## Pipeline

```text
doutrina-content  →  (artifact A)
librus-linker     →  (artifact B, with data-link-* / provider markup)
librus-shell      →  SPA + selective books → dist / PWA
```

## Status

Scaffold only — injection scripts and contracts land here when split from ad-hoc tooling.

## Repo map

| Repo | Role |
|------|------|
| **librus-shell** | SPA, flavors, PWA |
| **librus-linker** | This repo — link injection |
| **doutrina-content** | Editorial source (MD / QA) |
| **librus** / **doutrina** | Published site hosts (`dist` only) |
| `center-*` | Center manual + `flavor.json` |
