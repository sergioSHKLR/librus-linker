# 🔗 Librus Linker / Linkador Librus

* **EN:** [sergioSHKLR/librus-linker](https://github.com/sergioSHKLR/librus-linker)
* **PT:** [sergioSHKLR/librus-linker](https://github.com/sergioSHKLR/librus-linker)

## 🇺🇸 Overview & Intent
`librus-linker` is an automated pre-build processing utility designed to scan raw markdown files, identify targeted reference keys, and inject deep links and cross-references across the Librus ecosystem content pipeline. Its primary intent is to eliminate manual curation overhead, ensuring uniform citation mapping and robust inter-textual linking for digital editions of historical literature.

### Architecture & Code Choices
* **Language/Runtime:** Node.js script architecture optimized for fast batch parsing of static file systems.
* **Design Pattern:** Pure functional parsing utility operating on upstream source trees without complex ORM or database dependencies.
* **Modularity:** Decoupled from the reader application, executing strictly within the CI/CD or local build preparation phase before static site compilation.

### Site Map & Repository Structure
* `src/` — Core parsing and regex-matching engine logic.
* `config/` — Keyword definition tables and reference mapping dictionaries.
* `tests/` — Automated validation suites ensuring target link integrity.

### Contributing & Volunteer Onboarding
We welcome contributions to improve regex performance, expand cross-reference dictionaries, or optimize processing speed for large book repositories. See issues for open tasks.

---

## 🇧🇷 Visão Geral & Intenção
O `librus-linker` é um utilitário de processamento automatizado de pré-compilação projetado para escanear arquivos markdown brutos, identificar chaves de referência direcionadas e injetar links diretos e referências cruzadas em todo o pipeline de conteúdo do ecossistema Librus. Sua principal intenção é eliminar a sobrecarga de curadoria manual, garantindo um mapeamento de citações uniforme e ligações intertextuais robustas para edições digitais de literatura histórica.

### Arquitetura & Escolhas de Código
* **Linguagem/Ambiente:** Arquitetura de scripts em Node.js otimizada para processamento rápido em lote de sistemas de arquivos estáticos.
* **Padrão de Projeto:** Utilitário de parsing funcional puro que opera em árvores de origem sem dependências complexas de ORM ou banco de dados.
* **Modularidade:** Desacoplado do aplicativo leitor, executando estritamente na fase de preparação de build (CI/CD ou local) antes da compilação estática do site.

### Mapa do Site & Estrutura do Repositório
* `src/` — Lógica do motor de análise e correspondência por expressões regulares.
* `config/` — Tabelas de definição de palavras-chave e dicionários de mapeamento de referência.
* `tests/` — Suítes de validação automatizadas que garantem a integridade dos links de destino.

### Contribuição & Integração de Voluntários
Recebemos contribuições para melhorar o desempenho de regex, expandir dicionários de referências cruzadas ou otimizar a velocidade de processamento para grandes repositórios de livros. Consulte as issues para tarefas abertas.
