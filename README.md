# librus-linker

**Build step 2 of 4** · Provider link injection (maintainers & volunteers)

---

## 📑 Table of contents

1. 🇺🇸 [English](#-english--build-step-2-of-4)
   1. 🎯 [Audience](#-audience)
   2. 🗺️ [Pipeline position](#-pipeline-position)
   3. ⚙️ [What this repo owns](#️-what-this-repo-owns)
   4. 📥 [Inputs / outputs](#-inputs--outputs)
   5. 🚧 [Status](#-status)
   6. 📐 [Methodology](#-methodology)
   7. 🤝 [How to help](#-how-to-help)
2. 🇧🇷 [Português](#-português--etapa-2-de-4)
   1. 🎯 [Público](#-público)
   2. 🗺️ [Posição no pipeline](#-posição-no-pipeline)
   3. ⚙️ [O que este repo possui](#️-o-que-este-repo-possui)
   4. 📥 [Entradas / saídas](#-entradas--saídas)
   5. 🚧 [Estado](#-estado)
   6. 📐 [Metodologia](#-metodologia)
   7. 🤝 [Como ajudar](#-como-ajudar)

---

# 🇺🇸 English — Build step 2 of 4

Takes content artifacts from **`doutrina-content`** and enriches them with provider anchors (`data-link-provider`, …). The shell reads those anchors at runtime.

## 🎯 Audience

1. Maintainers of the injection tooling  
2. Volunteers tuning provider rules / QA of injected links  
3. Reviewers who need to know **why** terms light up in the reader  

**Not** for end users.

## 🗺️ Pipeline position

1. [`doutrina-content`](https://github.com/sergioSHKLR/doutrina-content) — Markdown source  
2. **This repo** — link injection  
3. [`librus-shell`](https://github.com/sergioSHKLR/librus-shell) — SPA + books  
4. Host repos — live Pages  

```text
doutrina-content  →  librus-linker  →  librus-shell  →  host Pages
     (1/4)              (2/4)             (3/4)            (4/4)
```

## ⚙️ What this repo owns

1. Injection scripts and contracts you maintain  
2. Provider targeting rules (Luz, wiki/encyc, dict, maps, Bible, Kardecpedia, …)  
3. **Not** the book prose itself (that stays in `doutrina-content`)  

## 📥 Inputs / outputs

1. **In:** built / full Markdown or HTML from step 1  
2. **Out:** same artifacts with `data-link-*` markup for the shell  
3. **Consumed by:** step 3 (`librus-shell` catalog / `public/books/`)  

## 🚧 Status

1. Scaffold and pipeline contract are documented here.  
2. Provider rules: [METHODOLOGY.md](./METHODOLOGY.md) (Luz → wiki → dict → Bible cites; Kardecpedia off-shelf only).  
3. Injection scripts continue to land as they are split out of ad-hoc tooling.  
4. Restamp: `python3 scripts/restamp.py` (Luz → map → wiki → capped dict; Bible cites). Consumes `catalogs/*.json` and writes `librus-shell/public/books/{lde,ldm,ese,ceu,gen}`.  
5. Dict 404s: `python3 scripts/audit_dict.py` refreshes `catalogs/dict-allowlist.json` + `dict-missing.json` from live stamps (Wiktionary `action=query`, ≤50/title). Restamp then stamps `d` only for allowlisted lemmas. See [librus-linker#1](https://github.com/sergioSHKLR/librus-linker/issues/1).  
6. Bible cites (2026-09-12): book → Wikipedia; **cap. N** (label includes `cap.`) → Wikipedia chapter; **vers. N** → Bible.com ARC verse; **ARC** → Bible.com version page. Verse regex must not swallow `A` from ARC. Spirit signature last lines drop `<strong>`. The shell must load the stamped `href` (not re-search the label).  

## 📐 Methodology

Rules live in [METHODOLOGY.md](./METHODOLOGY.md): two packs (`general` / `spiritism`); Luz catalog longest-match first, then Wikipedia, then capped Wiktionary; Bible only on `.bible-cite` verse tokens; Kardecpedia only for titles outside the five featured books.

Catalogs in `catalogs/`: `luz-articles.json`, `wiki-allowlist.json` (seeded from current stamps), `places.json` (toponyms pulled out of those stamps), `dict-allowlist.json` / `dict-missing.json` (Wiktionary existence audit).

## 🤝 How to help

1. Propose provider coverage rules (what should / should not link).  
2. File issues with example passages and expected provider.  
3. Help port one-shot scripts into a repeatable CLI with tests.  

## 🏅 Credits

1. See [CREDITS.md](./CREDITS.md) — Sergio SHKLR (lead, git metrics) · Grok / xAI (assisted docs).  

---

# 🇧🇷 Português — Etapa 2 de 4

Recebe artefatos de **`doutrina-content`** e enriquece com âncoras de provedores (`data-link-provider`, …). O shell lê essas âncoras em tempo de execução.

## 🎯 Público

1. Mantenedores da ferramenta de injeção  
2. Voluntários que ajustam regras / QA dos links  
3. Revisores que precisam entender **por que** termos acendem no leitor  

**Não** é para o usuário final.

## 🗺️ Posição no pipeline

1. [`doutrina-content`](https://github.com/sergioSHKLR/doutrina-content) — fonte Markdown  
2. **Este repositório** — injeção de ligações  
3. [`librus-shell`](https://github.com/sergioSHKLR/librus-shell) — SPA + livros  
4. Repos host — Pages ao vivo  

## ⚙️ O que este repo possui

1. Scripts e contratos de injeção  
2. Regras de provedores (Luz, wiki/encyc, dict, mapas, Bíblia, Kardecpedia, …)  
3. **Não** o texto dos livros (permanece em `doutrina-content`)  

## 📥 Entradas / saídas

1. **Entrada:** Markdown/HTML full da etapa 1  
2. **Saída:** mesmos artefatos com markup `data-link-*`  
3. **Consumidor:** etapa 3 (`librus-shell`)  

## 🚧 Estado

1. Contrato do pipeline documentado.  
2. Regras: [METHODOLOGY.md](./METHODOLOGY.md).  
3. Scripts migrando de ferramentas ad hoc para este repo.  
4. Enquanto isso, livros em `librus-shell` são o consumidor de trabalho. O inject atual da LDE é denso em dicionário e **ainda não** segue o mix.  
5. 404s do dicionário: `python3 scripts/audit_dict.py` atualiza `dict-allowlist.json` / `dict-missing.json`. O restamp só carimba `d` na allowlist.  
6. Cites (2026-09-12): livro → Wikipédia; **cap. N** → capítulo; **vers. N** → Bible.com ARC; **ARC** → página da versão no Bible.com. O regex do versículo não pode engolir o `A` de ARC. Assinaturas ✨ sem `<strong>`. O shell abre o `href` carimbado (não pesquisa o rótulo).

## 📐 Metodologia

Ver [METHODOLOGY.md](./METHODOLOGY.md): Luz → Wikipédia → Wikcionário limitado; Bíblia só na linha de citação; Kardecpedia só para obras fora das cinco.

## 🤝 Como ajudar

1. Propor regras de cobertura de provedores.  
2. Abrir issues com trechos e provedor esperado.  
3. Ajudar a transformar scripts one-shot em CLI testável.  

## 🏅 Créditos

1. Ver [CREDITS.md](./CREDITS.md) — Sergio SHKLR (líder, métricas git) · Grok / xAI (docs assistidos).  
