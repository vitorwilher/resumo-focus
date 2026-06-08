# Projeto Boletim Focus — Briefing

## Objetivo
Automatizar, toda **segunda-feira**, o ciclo:
1. **Baixar** o boletim Focus do Banco Central do Brasil (PDF).
2. **Extrair** o texto do PDF.
3. **Preparar** um resumo executivo a partir do texto extraído.

## Fonte dos dados
- Página de referência: https://www.bcb.gov.br/publicacoes/focus
- Padrão de URL do PDF: `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - `{AAAAMMDD}` é a data de publicação sem separadores (ex.: `R20260608.pdf`).

## Estrutura de pastas
```
.
├── src/                  # código-fonte (download, extração, resumo)
├── tests/                # testes automatizados
├── data/                 # PDFs e textos baixados (artefatos brutos)
├── output/
│   └── focus/            # resumos finais em markdown
└── .github/
    └── workflows/        # automação (agendamento semanal)
```

## Convenções de nomenclatura
- Arquivos nomeados pela **data de publicação**: `focus_AAAA-MM-DD`.
  - Ex.: `focus_2026-06-08.pdf`, `focus_2026-06-08.txt`, `focus_2026-06-08.md`.
- `data/` guarda os PDFs e os textos extraídos (insumos brutos).
- `output/focus/` guarda os resumos executivos em markdown (entregável final).

## Regras
1. **Nunca inventar número.** Toda mediana (ou qualquer valor) citada no resumo
   **deve estar presente no texto extraído** do PDF. Se não estiver no texto,
   não entra no resumo.
2. **Feriado na segunda.** Quando a segunda-feira é feriado, o BCB publica o
   Focus na terça. O download deve **retroceder dia a dia** a partir da data
   alvo até encontrar um PDF válido (HTTP 200 / conteúdo de PDF).
