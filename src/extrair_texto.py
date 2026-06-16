"""Extrai o texto de um PDF do Boletim Focus e salva como arquivo .txt.

Lê o PDF com pdfplumber, concatena o texto de todas as páginas e grava o
resultado em UTF-8, num .txt com o mesmo nome do PDF.

Uso:
    python src/extrair_texto.py                 # usa o focus_*.pdf mais recente de data/
    python src/extrair_texto.py --pdf caminho/para/arquivo.pdf
"""

import argparse
import sys
from pathlib import Path

import pdfplumber


def extrair(pdf_path):
    """Extrai o texto de `pdf_path` e salva num .txt de mesmo nome.

    Abre o PDF com pdfplumber, junta o texto de todas as páginas (uma página
    por bloco, separadas por uma linha em branco) e grava em UTF-8 trocando a
    extensão .pdf por .txt.

    Retorna o caminho (Path) do arquivo .txt gerado.
    """
    pdf_path = Path(pdf_path)

    # Coleta o texto de cada página numa lista; páginas sem texto extraível
    # (ex.: imagens) entram como string vazia para não quebrar o join.
    paginas = []
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            paginas.append(pagina.extract_text() or "")

    # Junta as páginas separando-as por uma linha em branco.
    texto = "\n\n".join(paginas)

    # Mesmo nome do PDF, porém com extensão .txt.
    txt_path = pdf_path.with_suffix(".txt")
    txt_path.write_text(texto, encoding="utf-8")

    return txt_path


def pdf_mais_recente(pasta):
    """Retorna o focus_*.pdf mais recente de `pasta`, ou None se não houver.

    "Mais recente" é decidido pelo nome do arquivo: como a nomenclatura é
    focus_AAAA-MM-DD.pdf, a ordem alfabética coincide com a ordem cronológica.
    """
    pdfs = sorted(Path(pasta).glob("focus_*.pdf"))
    return pdfs[-1] if pdfs else None


def main():
    """CLI: extrai o texto de um PDF específico ou do mais recente em data/."""
    parser = argparse.ArgumentParser(
        description="Extrai o texto de um PDF do Boletim Focus para um .txt."
    )
    parser.add_argument(
        "--pdf",
        help="Caminho de um PDF específico. Se omitido, usa o focus_*.pdf "
        "mais recente da pasta data/.",
    )
    args = parser.parse_args()

    # A pasta data/ fica na raiz do projeto (um nível acima de src/).
    raiz = Path(__file__).resolve().parent.parent

    if args.pdf:
        # Usa o PDF informado explicitamente na linha de comando.
        pdf_path = Path(args.pdf)
    else:
        # Sem --pdf: procura o Focus mais recente já baixado em data/.
        pdf_path = pdf_mais_recente(raiz / "data")
        if pdf_path is None:
            print(
                "Nenhum PDF encontrado em data/. "
                "Rode 'python src/baixar_focus.py' primeiro para baixar o Focus.",
                file=sys.stderr,
            )
            return 1

    txt_path = extrair(pdf_path)
    tamanho_kb = txt_path.stat().st_size / 1024
    print(f"PDF de origem: {pdf_path}")
    print(f"Texto salvo:   {txt_path}")
    print(f"Tamanho:       {tamanho_kb:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
