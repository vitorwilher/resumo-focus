# Boletim Focus — Pipeline

Pipeline que baixa o boletim Focus do Banco Central do Brasil (PDF), extrai o
texto e, numa automação agendada, gera um resumo executivo em markdown.

A divisão de responsabilidades é deliberada: **os scripts Python cuidam só de
baixar e extrair** o texto; **o resumo é gerado por um agente lendo o texto
extraído**. Nenhum script tenta interpretar números ou redigir o resumo — essa
etapa é do agente, que se apoia exclusivamente no texto do PDF (nunca inventa
um valor).

## Estrutura

```
.
├── src/
│   ├── baixar_focus.py     # baixa o PDF mais recente (com lógica de feriado)
│   └── extrair_texto.py    # extrai o texto do PDF e salva como .txt
├── tests/                  # testes (offline + um marcado como `network`)
├── data/                   # PDFs e textos baixados (artefatos brutos)
├── output/
│   └── focus/              # resumos executivos em markdown (entregável do agente)
├── .github/
│   └── workflows/          # automação agendada (download semanal)
├── demo.py                 # roda o pipeline local: baixa + extrai
├── requirements.txt        # dependências com versões fixas
├── pytest.ini              # config do pytest + marker `network`
└── CLAUDE.md               # briefing do projeto para o agente
```

## Como rodar localmente

```bash
python -m pip install -r requirements.txt
python demo.py --abrir
```

O `demo.py` executa as duas etapas em sequência (baixa o Focus em `data/` e
extrai o texto). A flag `--abrir` abre o `.txt` gerado no navegador padrão ao
final.

## Testes

```bash
pytest                  # roda toda a suíte
pytest -m "not network" # pula os testes que fazem download real
```

Os testes de rede são marcados com `@pytest.mark.network`; rode só eles com
`pytest -m network`.

## Como o pipeline funciona (duas etapas)

O fluxo é dividido em duas etapas que rodam em lugares diferentes:

1. **Download e extração (GitHub Action).** Um workflow agendado baixa o PDF
   do Focus e extrai o texto, versionando o resultado no repositório. O passo
   de download precisa rodar de um ambiente cujo IP o BCB não bloqueie — o site
   restringe acessos vindos de faixas de nuvem, então o runner que baixa tem de
   estar nessa condição (ex.: runner self-hosted / IP liberado).

2. **Resumo (automação do agente).** A automação do agente **consome o texto já
   pronto** (o `.txt` versionado pela etapa anterior) e gera o resumo executivo
   em `output/focus/`. Ela não baixa nada: só lê o texto e escreve o markdown,
   garantindo que todo número citado venha do texto extraído.

Essa separação mantém a parte sensível a rede (download) isolada da parte de
geração de conteúdo (resumo), e permite reproduzir cada etapa de forma
independente.
