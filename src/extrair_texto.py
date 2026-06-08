"""Extrai o texto de um PDF do boletim Focus e salva como .txt (UTF-8).

Uso:
    python src/extrair_texto.py                 # pega o PDF mais recente de data/
    python src/extrair_texto.py --pdf caminho   # extrai de um PDF específico
"""

import argparse
import sys
from pathlib import Path

import pdfplumber


def extrair(pdf_path):
    """Extrai o texto de todas as páginas do PDF e salva como .txt.

    O arquivo de saída tem o mesmo nome do PDF, trocando a extensão para
    .txt, gravado em UTF-8. Retorna o caminho do .txt gerado.
    """
    pdf_path = Path(pdf_path)
    partes = []

    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # extract_text() devolve None em páginas sem texto; trocamos por "".
            partes.append(pagina.extract_text() or "")

    # Junta as páginas separando por quebra de linha.
    texto = "\n".join(partes)

    # Mesmo nome do PDF, com extensão .txt.
    txt_path = pdf_path.with_suffix(".txt")
    txt_path.write_text(texto, encoding="utf-8")

    return txt_path


def _pdf_mais_recente(pasta):
    """Retorna o focus_*.pdf mais recente da pasta, ou None se não houver."""
    pdfs = sorted(Path(pasta).glob("focus_*.pdf"))
    # A nomenclatura focus_AAAA-MM-DD ordena cronologicamente como texto,
    # então o último item é o mais recente.
    return pdfs[-1] if pdfs else None


def main():
    """CLI: extrai o texto de um PDF (informado ou o mais recente de data/)."""
    parser = argparse.ArgumentParser(
        description="Extrai o texto de um PDF do Focus e salva como .txt."
    )
    parser.add_argument(
        "--pdf",
        help="Caminho de um PDF específico. Se omitido, usa o mais recente de data/.",
    )
    args = parser.parse_args()

    if args.pdf:
        pdf_path = Path(args.pdf)
    else:
        pdf_path = _pdf_mais_recente("data")
        if pdf_path is None:
            print(
                "Nenhum PDF encontrado em data/. "
                "Rode `python src/baixar_focus.py` primeiro.",
                file=sys.stderr,
            )
            return 1

    txt_path = extrair(pdf_path)
    print(f"Texto extraído: {txt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
