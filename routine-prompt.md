# Rotina semanal — Resumo do Boletim Focus

Roteiro que a automação agendada executa toda semana para transformar o texto
já extraído do Focus num resumo executivo em markdown. Siga os passos em ordem;
quando um passo mandar **parar**, encerre sem produzir saída.

## Passos

1. **Localizar o texto mais recente.**
   Procure o arquivo `data/focus_*.txt` mais recente (a nomenclatura
   `focus_AAAA-MM-DD` ordena cronologicamente). Se **não houver nenhum**,
   **pare** sem fazer nada.

2. **Verificar o frescor pela data no nome.**
   Extraia a data `AAAA-MM-DD` do nome do arquivo e compare com a data de hoje:
   - **0 a 3 dias:** está fresco, siga normalmente.
   - **4 a 7 dias:** siga, mas **marque para revisão** (inclua um aviso no
     topo do markdown, ex.: `> ⚠️ Texto com N dias — revisar`).
   - **mais de 7 dias:** **pare** (o texto está velho demais para um resumo
     semanal confiável).

3. **Sanity check do conteúdo.**
   Confirme que o texto tem **pelo menos 2000 caracteres** e que contém as
   palavras **IPCA**, **Selic** e **PIB**. Se qualquer uma dessas condições
   falhar, o layout pode ter mudado — **pare** e sinalize o problema (não tente
   adivinhar o conteúdo).

4. **Gerar o resumo.**
   Leia o texto e produza um markdown com duas seções:
   - **Resumo executivo (até 200 palavras):** comece pelas **medianas
     principais** (ex.: IPCA, Selic, PIB, câmbio) e contextualize brevemente.
   - **Três principais revisões da semana:** liste as três mudanças mais
     relevantes em relação às semanas anteriores, cada uma com uma **hipótese
     de motivo** (claramente identificada como hipótese, não como fato).

   **Regra inviolável:** nunca invente número. Toda mediana ou valor citado
   **tem de estar presente no texto extraído**. Se um número não está no texto,
   ele não entra no resumo.

5. **Salvar o resultado.**
   Grave o markdown em `output/focus/focus_AAAA-MM-DD.md`, usando a **mesma
   data** do arquivo de texto de origem (data de publicação), em UTF-8.
