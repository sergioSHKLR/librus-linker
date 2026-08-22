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
   6. 🤝 [How to help](#-how-to-help)
2. 🇧🇷 [Português](#-português--etapa-2-de-4)
   1. 🎯 [Público](#-público)
   2. 🗺️ [Posição no pipeline](#-posição-no-pipeline)
   3. ⚙️ [O que este repo possui](#️-o-que-este-repo-possui)
   4. 📥 [Entradas / saídas](#-entradas--saídas)
   5. 🚧 [Estado](#-estado)
   6. 🤝 [Como ajudar](#-como-ajudar)

---

# 🇺🇸 English — Build step 2 of 4

Takes content artifacts from **`doutrina-content`** and enriches them with provider anchors (`data-link-provider`, `data-link-interest`, …). The shell reads those anchors at runtime.

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
2. Injection scripts continue to land as they are split out of ad-hoc tooling.  
3. Until scripts are fully in-repo, treat linked books in `librus-shell` as the working consumer of injection output.  

## 🤝 How to help

1. Propose provider coverage rules (what should / should not link).  
2. File issues with example passages and expected provider.  
3. Help port one-shot scripts into a repeatable CLI with tests.  

---

# 🇧🇷 Português — Etapa 2 de 4

Recebe artefatos de **`doutrina-content`** e enriquece com âncoras de provedores (`data-link-provider`, `data-link-interest`, …). O shell lê essas âncoras em tempo de execução.

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
2. Scripts migrando de ferramentas ad hoc para este repo.  
3. Enquanto isso, livros em `librus-shell` são o consumidor de trabalho.  

## 🤝 Como ajudar

1. Propor regras de cobertura de provedores.  
2. Abrir issues com trechos e provedor esperado.  
3. Ajudar a transformar scripts one-shot em CLI testável.  
