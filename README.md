# Projeto Boletim Focus

Pipeline que **baixa o Boletim Focus** do Banco Central do Brasil (BCB),
**extrai o texto** do PDF e, numa **automação agendada**, gera um **resumo
executivo** que é **enviado por e-mail**.

## Como funciona

O projeto tem uma divisão de responsabilidades importante:

- **Os scripts Python só baixam e extraem.** [`src/baixar_focus.py`](src/baixar_focus.py)
  busca o PDF mais recente no site do BCB e [`src/extrair_texto.py`](src/extrair_texto.py)
  converte esse PDF em texto puro (`.txt`). Eles **não** interpretam nem
  resumem nada.
- **O resumo é escrito por um agente.** Na automação agendada, um agente
  (Claude) **lê o texto extraído** e redige o resumo executivo em markdown.
  Regra de ouro: o agente **nunca inventa número** — toda mediana ou valor
  citado precisa estar presente no texto extraído do PDF.
- **O resumo é enviado por e-mail** ao final da automação.

## Fonte dos dados

- **Página de referência:** <https://www.bcb.gov.br/publicacoes/focus>
- **Padrão de URL do PDF:** `https://www.bcb.gov.br/content/focus/focus/R{AAAAMMDD}.pdf`

O Focus é publicado, em regra, **toda segunda-feira**. Quando a segunda é
feriado, o BCB publica no próximo dia útil; por isso o download parte da
última segunda-feira e **recua dia a dia** até encontrar o PDF disponível.

## Árvore de pastas

```
.
├── src/                       # código-fonte (só download e extração)
│   ├── baixar_focus.py        # baixa o PDF mais recente do BCB
│   └── extrair_texto.py       # extrai o texto do PDF para .txt
├── tests/                     # testes automatizados (pytest)
│   └── test_baixar_focus.py
├── data/                      # PDFs e textos extraídos (insumo bruto)
├── output/
│   └── focus/                 # resumos em markdown (entregável final, versionado)
├── .github/
│   └── workflows/
│       └── focus-download.yml # automação semanal (download + extração)
├── demo.py                    # roda o pipeline localmente (baixar + extrair)
├── requirements.txt
├── pytest.ini
└── CLAUDE.md                  # briefing do projeto
```

## Convenções

- **Nomenclatura:** `focus_AAAA-MM-DD` usando a **data da publicação**
  (ex.: `focus_2026-06-08.pdf`, `focus_2026-06-08.txt`, `focus_2026-06-08.md`).
- **`data/`** guarda os PDFs e textos extraídos (insumo bruto).
- **`output/focus/`** guarda os resumos em markdown (entregável final).

## Como rodar localmente

Requer Python 3. Recomenda-se um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Rode o pipeline de ponta a ponta (baixa o Focus mais recente e extrai o texto):

```bash
python demo.py            # baixa e extrai
python demo.py --abrir    # idem e abre o .txt no navegador padrão
```

Ou rode cada etapa separadamente:

```bash
python src/baixar_focus.py     # baixa o PDF para data/
python src/extrair_texto.py    # extrai o texto do PDF mais recente em data/
```

## Como rodar os testes

```bash
pytest -m "not network"   # testes offline (rápidos, sem download)
pytest -m network         # teste de rede (faz o download real do BCB)
pytest                    # todos os testes
```
