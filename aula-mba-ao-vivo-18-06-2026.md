# Aula ao vivo — MBA em Aplicações de IA (18/06/2026)

## Construindo um agente de ponta a ponta com Claude Code: o Projeto Boletim Focus

Este roteiro mostra como construir, ao vivo e do zero, um agente que lê o **Boletim Focus do Banco Central do Brasil** toda semana e envia um **resumo executivo por e-mail** — sem ninguém abrir o PDF.

O objetivo pedagógico central é demonstrar o princípio mais importante de aplicações de IA confiáveis: **separar o que é determinístico (scripts) do que exige julgamento (o agente)**.

> Projeto de referência: [github.com/vitorwilher/resumo-focus](https://github.com/vitorwilher/resumo-focus)
> Descrição do projeto: [vitorwilher.github.io/projetos/projeto-boletim-focus.html](https://vitorwilher.github.io/projetos/projeto-boletim-focus.html)

---

## Abertura (fala, sem prompt)

> "Vamos construir um agente que lê o Boletim Focus do Banco Central toda semana e manda um resumo executivo por e-mail — sem ninguém abrir o PDF. O segredo não é jogar tudo na IA: é decidir o que o código faz e o que a IA faz."

Abra um terminal numa pasta vazia e rode `claude`.

---

## Bloco 1 — Briefing do projeto (o `CLAUDE.md`)

**Objetivo didático:** mostrar que um bom projeto de IA começa definindo contexto e regras, não código.

**Prompt:**

```
Vamos criar um projeto chamado resumo-focus. Antes de qualquer código,
crie um arquivo CLAUDE.md que sirva de briefing do projeto.

Contexto: automatizar o acompanhamento do Boletim Focus do Banco Central
do Brasil. O Focus é um PDF semanal publicado em
https://www.bcb.gov.br/publicacoes/focus com projeções de IPCA, Selic, PIB
e câmbio. Queremos transformar esse PDF num resumo executivo enviado por e-mail.

O briefing deve deixar explícito o PRINCÍPIO DE DESIGN central:
separar rigorosamente o determinístico do que exige julgamento.
- Scripts Python apenas BAIXAM e EXTRAEM texto (nunca interpretam).
- O agente Claude redige o resumo (a parte de julgamento).
- GitHub Actions orquestram o fluxo.

REGRA DE OURO que deve constar no CLAUDE.md: nunca inventar número.
Toda mediana ou valor citado no resumo precisa estar literalmente no texto
do PDF.

Proponha também a estrutura de pastas do projeto.
```

**Destacar:** o `CLAUDE.md` é a "memória" do agente — toda vez que eu rodar, leio esse arquivo. É aqui que se ancora a governança ("nunca inventa número"), o ponto mais sensível em IA aplicada a finanças.

---

## Bloco 2 — O determinístico: download do PDF

**Objetivo didático:** a parte "boba" e confiável. Python puro, testável, previsível.

**Prompt:**

```
Implemente src/baixar_focus.py. Ele baixa o PDF mais recente do Boletim Focus.

Os PDFs seguem o padrão de URL com a data de publicação no formato
R{AAAAMMDD}.pdf. O Focus sai às segundas. Trate o caso de feriado:
se a data alvo não existir (HTTP 404), recue um dia e tente de novo,
até um limite razoável de tentativas.

Salve o arquivo como data/focus_AAAA-MM-DD.pdf.
Use a biblioteca requests. Escreva código limpo e com funções pequenas
e testáveis. Crie também o requirements.txt.
```

**Destacar:** repare que eu *não* peço pra IA "entender" o Focus aqui. Só pego o arquivo. Robustez (feriado, 404) é responsabilidade do código determinístico.

---

## Bloco 3 — O determinístico: extração de texto + testes

**Objetivo didático:** introduzir testes como rede de segurança — e mostrar que peço pra IA escrever os testes também.

**Prompt:**

```
Agora implemente src/extrair_texto.py: converte o PDF baixado em texto puro
e salva como data/focus_AAAA-MM-DD.txt.

Em seguida, crie tests/test_baixar_focus.py com pytest. Use marcadores
para separar testes OFFLINE (que não acessam a rede) de testes que fazem
conexão real. Configure o pytest.ini.

Por fim, crie um demo.py que roda o pipeline local completo:
baixa e extrai o Focus mais recente, com opção de abrir o .txt resultante.
```

**Prompt de validação ao vivo (mostra a IA executando e se corrigindo):**

```
Rode o demo.py e os testes offline. Se algo quebrar, corrija e rode de novo
até passar. Me mostre o texto extraído do PDF.
```

**Destacar:** este é o momento "uau" da aula — os alunos veem o agente rodar, ler o erro, corrigir e re-executar sozinho. É o loop agêntico na prática.

---

## Bloco 4 — O julgamento: o resumo executivo (o coração da IA)

**Objetivo didático:** aqui mora a inteligência. Mostre que a qualidade vem do *prompt/instrução*, não de mais código.

**Prompt:**

```
Agora a parte de julgamento. Com base no texto extraído mais recente
(data/focus_*.txt), gere o resumo executivo seguindo as regras do CLAUDE.md.

Antes de escrever, VALIDE o insumo:
- frescor: o arquivo precisa ter entre 0 e 7 dias.
- integridade: pelo menos 2.000 caracteres e presença de palavras-chave
  como IPCA, Selic, PIB e câmbio.
Se falhar a validação, pare e explique o motivo.

O resumo deve ter:
- no máximo 200 palavras, em tom executivo;
- citações LITERAIS dos números (nada inventado — regra de ouro);
- uma seção "Três principais revisões" no formato:
  Variável (ano): anterior -> atual

Me mostre o resumo em texto antes de formatar em HTML.
```

**Destacar:** compare com os blocos anteriores. Aqui não escrevi nenhuma linha de código de "resumir" — a competência é linguística e está na instrução. **Esse é o divisor de águas da aula:** o que é código vs. o que é prompt. E a validação de frescor/integridade é o "cinto de segurança" antes de deixar a IA julgar.

---

## Bloco 5 — Entregável com identidade visual (HTML)

**Objetivo didático:** transformar inteligência em produto consumível.

**Prompt:**

```
Monte o resumo num HTML em output/focus/focus_AAAA-MM-DD.html com
identidade visual: use a cor institucional #282f6b nos títulos/destaques
e um espaço para o logo da Análise Macro no topo.

O HTML deve ser bonito o suficiente para servir como CORPO de um e-mail
(layout simples, inline styles, responsivo). Me mostre o resultado
renderizado.
```

**Destacar:** o entregável não é "uma resposta de chat", é um artefato versionado e distribuível. IA aplicada = produto, não conversa.

---

## Bloco 6 — Orquestração (GitHub Actions)

**Objetivo didático:** de script manual para sistema autônomo. Os três estágios.

**Prompt:**

```
Vamos automatizar. Crie .github/workflows/focus-download.yml:
- roda toda segunda às 9h15 BRT (cron 15 12 * * 1 em UTC);
- instala dependências, roda baixar_focus.py e extrair_texto.py;
- commita os arquivos data/focus_*.{pdf,txt} na branch main.

Explique, em comentários no YAML, como este workflow se conecta aos outros
dois estágios do pipeline: (2) a routine do agente que gera o HTML e
(3) o workflow de envio de e-mail disparado pelo push do HTML.
```

**Destacar:** a arquitetura em 3 estágios — cada um com responsabilidade única. O agente é *um estágio orquestrado*, não o sistema inteiro. Isso é design de aplicação de IA madura.

---

## Bloco 7 — Envio por e-mail + fechamento

**Objetivo didático:** o "última milha" e o tratamento de segredos/credenciais.

**Prompt:**

```
Crie src/enviar_email.py: envia o HTML mais recente de output/focus/
como corpo de um e-mail, via SMTP do Gmail. As credenciais
(usuário e senha de app) devem vir de variáveis de ambiente / GitHub
Secrets — NUNCA hardcoded.

Depois, crie o workflow .github/workflows/focus-email.yml que dispara
automaticamente quando um novo HTML é commitado em main, e roda o envio.
```

**Prompt de encerramento (síntese pros alunos):**

```
Faça um resumo final do que construímos, mapeando cada peça em uma de duas
categorias: DETERMINÍSTICO (código) ou JULGAMENTO (IA). Explique por que
essa separação é o princípio mais importante para aplicações de IA
confiáveis em produção.
```

**Destacar (fala de fechamento):** "O agente não substituiu o sistema — ele ocupou *exatamente* o pedaço onde julgamento agrega valor: ler o PDF e redigir. O resto é engenharia clássica. É assim que se constrói IA aplicada confiável."

---

## Dicas de condução ao vivo

- **Tempo:** blocos 1–4 são o núcleo (~40 min). Se o tempo apertar, mostre os blocos 6–7 já prontos do [repo original](https://github.com/vitorwilher/resumo-focus) em vez de construir.
- **Plano B:** tenha um PDF do Focus já baixado em `data/` caso a rede/BCB falhe ao vivo — assim o Bloco 4 roda mesmo sem internet.
- **Momento de ouro:** force um erro de propósito no Bloco 3 (ex: rode antes de instalar dependências) pra plateia ver o loop de auto-correção.
- **Pergunta pra plateia** entre o Bloco 3 e o 4: *"O que aqui é código e o que é IA?"* — prepara o insight do Bloco 4.

---

## Resumo da arquitetura em 3 estágios

| Estágio | Responsável | Tipo | O que faz |
|---------|-------------|------|-----------|
| 1. Download e extração | GitHub Action + Python | Determinístico | Baixa o PDF e extrai texto |
| 2. Resumo | Agente Claude (routine) | Julgamento | Valida, redige resumo e monta HTML |
| 3. Envio | GitHub Action + Python | Determinístico | Envia o HTML por e-mail (SMTP Gmail) |

---

*Material da aula ao vivo do MBA em Aplicações de IA — 18/06/2026 — Análise Macro.*
