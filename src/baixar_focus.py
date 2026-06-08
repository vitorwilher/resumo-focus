"""Baixa o PDF mais recente do boletim Focus do Banco Central do Brasil.

Uso:
    python src/baixar_focus.py
"""

from datetime import date, timedelta
from pathlib import Path

import requests

# URL do PDF do Focus; {data} é preenchido no formato AAAAMMDD (sem hífens).
URL_FOCUS = "https://www.bcb.gov.br/content/focus/focus/R{data}.pdf"

# User-Agent de navegador: o site do BCB pode rejeitar clientes "robôs".
CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Número máximo de dias que recuamos procurando um PDF (cobre feriados).
MAX_TENTATIVAS = 7


def ultima_segunda(hoje):
    """Retorna a segunda-feira mais recente ESTRITAMENTE anterior a `hoje`.

    Se `hoje` já for uma segunda-feira, recua para a segunda da semana
    passada (e não devolve o próprio dia).
    """
    # weekday(): segunda=0, ..., domingo=6.
    # Para terça..domingo, weekday() já é a distância até a segunda da semana.
    # Para segunda (0), usamos 7 para pular a semana inteira.
    dias_para_tras = hoje.weekday() or 7
    return hoje - timedelta(days=dias_para_tras)


def baixar(dest):
    """Baixa o PDF do Focus mais recente para a pasta `dest`.

    Parte da última segunda-feira e, se não encontrar o arquivo, recua um
    dia por vez (até MAX_TENTATIVAS) para cobrir semanas em que a segunda
    foi feriado e a publicação saiu em outro dia.

    Retorna a tupla (data_da_publicacao, caminho_do_arquivo).
    Levanta RuntimeError se nenhuma tentativa funcionar.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    data_alvo = ultima_segunda(date.today())

    for _ in range(MAX_TENTATIVAS):
        # Data sem hífens para a URL (ex.: 20260608).
        url = URL_FOCUS.format(data=data_alvo.strftime("%Y%m%d"))
        resposta = requests.get(url, headers=CABECALHOS, timeout=30)

        # Aceita apenas se a resposta for OK e começar com a assinatura %PDF.
        if resposta.status_code == 200 and resposta.content.startswith(b"%PDF"):
            # Nome do arquivo pela data de publicação: focus_AAAA-MM-DD.pdf.
            caminho = dest / f"focus_{data_alvo.isoformat()}.pdf"
            caminho.write_bytes(resposta.content)
            return data_alvo, caminho

        # Não encontrou: recua um dia e tenta novamente.
        data_alvo -= timedelta(days=1)

    raise RuntimeError(
        f"Nenhum PDF do Focus encontrado em {MAX_TENTATIVAS} tentativas "
        f"(até {data_alvo.isoformat()})."
    )


def main():
    """Baixa o Focus para a pasta data/ e imprime caminho e tamanho em KB."""
    data_publicacao, caminho = baixar("data")
    tamanho_kb = caminho.stat().st_size / 1024
    print(f"Publicação: {data_publicacao.isoformat()}")
    print(f"Arquivo:    {caminho}")
    print(f"Tamanho:    {tamanho_kb:.1f} KB")


if __name__ == "__main__":
    main()
