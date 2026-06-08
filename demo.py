"""Roda o pipeline do Focus localmente: baixa o PDF e extrai o texto.

Uso:
    python demo.py            # baixa e extrai
    python demo.py --abrir    # ao final, abre o .txt no navegador padrão
"""

import argparse
import sys
import webbrowser
from pathlib import Path

# Adiciona a pasta src/ ao path de import para acessar os módulos do projeto.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from baixar_focus import baixar  # noqa: E402
from extrair_texto import extrair  # noqa: E402


def main():
    """Executa as duas etapas do pipeline em sequência."""
    parser = argparse.ArgumentParser(
        description="Baixa o Focus e extrai o texto, em sequência."
    )
    parser.add_argument(
        "--abrir",
        action="store_true",
        help="Abre o .txt gerado no navegador padrão ao final.",
    )
    args = parser.parse_args()

    # [1/2] Download do PDF para a pasta data/.
    _, pdf_path = baixar("data")
    tamanho_kb = pdf_path.stat().st_size / 1024
    print(f"[1/2] PDF baixado: {pdf_path.name} ({tamanho_kb:.1f} KB)")

    # [2/2] Extração do texto para um .txt ao lado do PDF.
    txt_path = extrair(pdf_path)
    print(f"[2/2] Texto extraído: {txt_path}")

    # Opcional: abre o texto no navegador padrão.
    if args.abrir:
        webbrowser.open(txt_path.resolve().as_uri())


if __name__ == "__main__":
    main()
