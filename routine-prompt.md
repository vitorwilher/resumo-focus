Você está executando a Routine de resumo semanal do Focus.

O download do PDF e a extração do texto já foram feitos por um GitHub
Action mais cedo (segunda 9h15 BRT). Os arquivos
`data/focus_AAAA-MM-DD.{pdf,txt}` já estão commitados em `main` quando
a Routine inicia. Sua tarefa é ler o `.txt` mais recente, gerar um
resumo em HTML com a logo da Análise Macro e commitá-lo no repositório.
O envio do e-mail é automático: um GitHub Action dispara quando o HTML é
publicado em `main` e envia a mensagem via SMTP do Gmail. Você não cria
rascunho nem envia nada à mão.

## Passos

1. **Localize o `.txt` mais recente.** Liste `data/focus_*.txt` e pegue
   o de data mais alta. Se não houver nenhum, pare sem commitar o HTML — o
   Action não rodou.

2. **Verifique frescor.** Extraia a data do nome e compare com hoje:
   - 0 a 3 dias: está fresco, siga.
   - 4 a 7 dias: siga, mas escreva `[REVISAR]` no início do assunto.
   - Mais de 7 dias: pare sem commitar o HTML.

3. **Sanity check do texto.** Confirme: pelo menos 2 000 caracteres e
   presença das palavras `IPCA`, `Selic`, `PIB`. Se falhar, o layout do
   PDF pode ter mudado — pare sem commitar o HTML.

4. **Leia o texto** e escreva o conteúdo do resumo:
   - **Resumo executivo** em até 200 palavras, em prosa corrida.
     Comece pelas medianas das principais variáveis (IPCA do ano,
     Selic fim de ano, PIB, câmbio). Cite literalmente entre aspas
     quando houver número-chave.
   - **Três principais revisões da semana** em bullets no formato:
     `Variável (ano): anterior → atual. Hipótese: motivo.`
   - Nunca invente número. Se não houver hipótese sólida, escreva
     "sem hipótese clara — pode ser ruído amostral".

5. **Monte o HTML** do e-mail em `output/focus/focus_AAAA-MM-DD.html`, com
   esta estrutura:
   - No topo, a logo da Análise Macro, carregada desta URL:
     `https://analisemacro.com.br/wp-content/uploads/dlm_uploads/2021/10/logo_am.png`
   - Um título `Focus — AAAA-MM-DD`.
   - O resumo executivo em parágrafo e as três revisões em lista.
   - Use as cores da marca: azul `#282f6b` nos títulos.

6. **Inspecione** o HTML gerado: a logo aparece, as medianas batem com
   o `.txt`, há ao menos uma citação literal entre aspas.

7. **Publique o HTML no repositório.** Faça `git add` do arquivo
   `output/focus/focus_AAAA-MM-DD.html`, commit e `git push` para `main`.
   É esse push que dispara o GitHub Action de envio (`focus-enviar.yml`),
   que manda o e-mail via SMTP do Gmail — você não cria rascunho nem
   dispara nada à mão. O destinatário, o remetente e a senha de app ficam
   nos Secrets do repositório (`FOCUS_EMAIL_DEST`, `FOCUS_SMTP_USER`,
   `FOCUS_SMTP_APP_PASSWORD`), nunca neste arquivo.

## Falhas

Em qualquer cenário abaixo, pare sem commitar o HTML. O motivo aparece no
transcript da Routine.

- Nenhum `.txt` em `data/` (Action não rodou).
- `.txt` com mais de 7 dias (Action quebrado).
- Sanity check do texto falhou (mudança de layout do PDF).

Nunca invente número.
