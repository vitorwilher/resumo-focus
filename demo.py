"""Roda o pipeline do Boletim Focus localmente, de ponta a ponta.

Executa as duas etapas em sequência:
    1. Baixa o PDF do Focus mais recente para a pasta data/.
    2. Extrai o texto desse PDF para um arquivo .txt ao lado.

Uso:
    python demo.py            # baixa e extrai
    python demo.py --abrir    # idem e abre o .txt no navegador padrão
"""

import argparse
import sys
import webbrowser
from pathlib import Path

# A pasta src/ não é um pacote instalável: adicionamos seu caminho ao
# sys.path para conseguir importar os módulos diretamente.
RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from baixar_focus import baixar  # noqa: E402  (import após ajuste do sys.path)
from extrair_texto import extrair  # noqa: E402


def main():
    """Baixa o Focus, extrai o texto e (opcionalmente) abre o .txt."""
    parser = argparse.ArgumentParser(
        description="Roda o pipeline do Focus: baixa o PDF e extrai o texto."
    )
    parser.add_argument(
        "--abrir",
        action="store_true",
        help="Abre o .txt gerado no navegador padrão ao final.",
    )
    args = parser.parse_args()

    dest = RAIZ / "data"

    # Etapa 1: download do PDF mais recente para data/.
    data_publicacao, pdf_path = baixar(dest)
    tamanho_kb = pdf_path.stat().st_size / 1024
    print(f"[1/2] PDF baixado: {pdf_path.name} ({tamanho_kb:.1f} KB)")

    # Etapa 2: extração do texto para um .txt ao lado do PDF.
    txt_path = extrair(pdf_path)
    print(f"[2/2] Texto extraído: {txt_path}")

    # Com --abrir, abre o arquivo de texto no navegador padrão.
    if args.abrir:
        webbrowser.open(txt_path.resolve().as_uri())

    return 0


if __name__ == "__main__":
    sys.exit(main())
