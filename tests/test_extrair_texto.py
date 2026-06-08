"""Testes para src/extrair_texto.py (sem rede).

Gera um PDF mínimo, válido e com texto embutido dentro do próprio teste,
para exercitar a extração sem depender de download.
"""

import sys
from pathlib import Path

# Insere src/ no path de import, como no demo.py.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extrair_texto import extrair  # noqa: E402


def _make_pdf(caminho, texto):
    """Escreve um PDF de 1 página com `texto` extraível em `caminho`.

    Constrói os objetos manualmente e calcula os offsets da tabela xref
    em tempo de execução, evitando depender de bibliotecas de geração.
    """
    # Fluxo de conteúdo: desenha o texto com a fonte Helvetica.
    fluxo = f"BT /F1 18 Tf 72 700 Td ({texto}) Tj ET".encode("latin-1")

    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(fluxo)).encode() + b" >>\nstream\n"
        + fluxo + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    # Monta o corpo, registrando o offset (byte) de início de cada objeto.
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, corpo in enumerate(objetos, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + corpo + b"\nendobj\n"

    # Tabela xref.
    inicio_xref = len(pdf)
    pdf += f"xref\n0 {len(objetos) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()

    # Trailer.
    pdf += b"trailer\n"
    pdf += f"<< /Size {len(objetos) + 1} /Root 1 0 R >>\n".encode()
    pdf += f"startxref\n{inicio_xref}\n%%EOF".encode()

    Path(caminho).write_bytes(pdf)


def test_extrair_gera_txt_com_o_texto(tmp_path):
    pdf = tmp_path / "focus_2026-05-29.pdf"
    _make_pdf(pdf, "Mediana IPCA 4,50")

    txt = extrair(pdf)

    # Retorna o caminho do .txt, ao lado do PDF e com a extensão trocada.
    assert txt == pdf.with_suffix(".txt")
    assert txt.exists()

    # Conteúdo extraído contém o texto embutido, em UTF-8.
    conteudo = txt.read_text(encoding="utf-8")
    assert "Mediana IPCA 4,50" in conteudo


def test_extrair_preserva_nome_trocando_extensao(tmp_path):
    pdf = tmp_path / "focus_2026-06-01.pdf"
    _make_pdf(pdf, "Selic 9,00")

    txt = extrair(pdf)

    assert txt.name == "focus_2026-06-01.txt"
