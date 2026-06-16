# Projeto Boletim Focus

Briefing do projeto para o agente (Claude) e para a equipe.

## Objetivo

Baixar o Boletim Focus do Banco Central do Brasil (BCB) **toda segunda-feira**, extrair o texto do PDF e preparar um **resumo executivo**.

## Fonte

- **Página de referência:** https://www.bcb.gov.br/publicacoes/focus
- **Padrão de URL do PDF:** `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`
  - Exemplo: a publicação de 02/06/2026 estaria em `https://www.bcb.gov.br/content/focus/focus/R20260602.pdf`.

## Estrutura de pastas

```
.
├── src/                  # código-fonte (download, extração, resumo)
├── tests/                # testes automatizados
├── data/                 # PDFs e textos baixados (entrada bruta)
├── output/
│   └── focus/            # resumos em markdown (saída final)
└── .github/
    └── workflows/        # automação (CI / agendamento semanal)
```

## Convenções

- **Nomenclatura de arquivos:** `focus_AAAA-MM-DD` usando a **data da publicação**
  (ex.: `focus_2026-06-02.pdf`, `focus_2026-06-02.txt`, `focus_2026-06-02.md`).
- **`data/`** guarda os PDFs e os textos extraídos (insumo bruto).
- **`output/focus/`** guarda os resumos em markdown (entregável final).

## Regras

1. **Nunca inventar número.** Toda mediana (ou qualquer valor) citada no resumo
   **deve** estar presente no texto extraído do PDF. Se um número não aparece na
   fonte, ele não entra no resumo.
2. **Feriado na segunda-feira:** quando a segunda é feriado, o BCB publica na terça.
   A lógica de download deve **retroceder dia a dia** a partir da data alvo até
   encontrar o PDF disponível (segunda → terça → quarta..., conforme o caso, ou
   ajustando a data alvo da semana), em vez de falhar na primeira tentativa.
