"""Baixa o PDF mais recente do Boletim Focus do Banco Central do Brasil (BCB).

A publicação ocorre, em regra, toda segunda-feira. Quando a segunda é feriado,
o BCB publica na terça (ou no próximo dia útil). Por isso o download parte da
última segunda-feira e, se não encontrar o PDF, recua um dia de cada vez.

Uso:
    python src/baixar_focus.py
"""

from datetime import date, timedelta
from pathlib import Path

import requests

# Padrão de URL do PDF do Focus. A data entra no formato AAAAMMDD (sem hífens).
URL_PADRAO = "https://www.bcb.gov.br/content/focus/focus/R{}.pdf"

# Cabeçalho com User-Agent de navegador: o servidor do BCB pode recusar
# requisições sem um User-Agent "de verdade".
CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Número máximo de tentativas, recuando um dia por vez. 7 dias cobrem qualquer
# sequência de feriados emendados dentro de uma semana.
MAX_TENTATIVAS = 7


def ultima_segunda(hoje):
    """Retorna a segunda-feira mais recente ESTRITAMENTE anterior a `hoje`.

    Se `hoje` já for uma segunda-feira, retrocede para a segunda da semana
    passada (nunca devolve a própria data recebida).
    """
    # Em date.weekday(): segunda = 0, ..., domingo = 6.
    dia_da_semana = hoje.weekday()
    # Se hoje é segunda (0), recua a semana inteira (7); caso contrário, recua
    # até a segunda desta semana, que já é anterior a `hoje`.
    recuo = dia_da_semana if dia_da_semana != 0 else 7
    return hoje - timedelta(days=recuo)


def baixar(dest):
    """Baixa o PDF do Focus mais recente para a pasta `dest`.

    Parte da última segunda-feira e tenta a URL do dia; se não der certo, recua
    um dia e tenta de novo, até MAX_TENTATIVAS. Valida que o conteúdo começa com
    os bytes mágicos "%PDF" antes de aceitar.

    Retorna a tupla (data_da_publicacao, caminho_do_arquivo).
    Levanta RuntimeError se nenhuma tentativa for bem-sucedida.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Data inicial da busca: a última segunda anterior a hoje.
    data_alvo = ultima_segunda(date.today())

    for _ in range(MAX_TENTATIVAS):
        # Monta a URL com a data no formato AAAAMMDD (sem hífens).
        url = URL_PADRAO.format(data_alvo.strftime("%Y%m%d"))
        try:
            resposta = requests.get(url, headers=CABECALHOS, timeout=30)
        except requests.RequestException:
            # Falha de rede nesta data: recua um dia e tenta a próxima.
            data_alvo -= timedelta(days=1)
            continue

        # Aceita apenas se o status for 200 E o conteúdo for de fato um PDF.
        if resposta.status_code == 200 and resposta.content[:4] == b"%PDF":
            # Nome do arquivo usa a data da publicação no formato AAAA-MM-DD.
            nome = f"focus_{data_alvo.isoformat()}.pdf"
            caminho = dest / nome
            caminho.write_bytes(resposta.content)
            return data_alvo, caminho

        # Não era um PDF válido (provável 404): recua um dia.
        data_alvo -= timedelta(days=1)

    # Esgotou as tentativas sem encontrar um PDF válido.
    raise RuntimeError(
        f"Não foi possível baixar o Focus após {MAX_TENTATIVAS} tentativas "
        f"(última data testada: {data_alvo.isoformat()})."
    )


def main():
    """Baixa o Focus para a pasta data/ e imprime o caminho e o tamanho em KB."""
    # A pasta data/ fica na raiz do projeto (um nível acima de src/).
    raiz = Path(__file__).resolve().parent.parent
    dest = raiz / "data"

    data_publicacao, caminho = baixar(dest)
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Publicação: {data_publicacao.isoformat()}")
    print(f"Arquivo:    {caminho}")
    print(f"Tamanho:    {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
