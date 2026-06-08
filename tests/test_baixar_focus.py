"""Testes para src/baixar_focus.py."""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Insere src/ no path de import, como no demo.py.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from baixar_focus import baixar, ultima_segunda  # noqa: E402


# --------------------------------------------------------------------------
# Testes puros (sem rede) para ultima_segunda
# --------------------------------------------------------------------------

def test_quinta_recua_para_segunda_da_mesma_semana():
    # Quinta 2026-06-04 -> segunda 2026-06-01 (mesma semana).
    assert ultima_segunda(date(2026, 6, 4)) == date(2026, 6, 1)


def test_terca_recua_para_segunda_da_mesma_semana():
    # Terça 2026-06-02 -> segunda 2026-06-01 (dia anterior).
    assert ultima_segunda(date(2026, 6, 2)) == date(2026, 6, 1)


def test_segunda_recua_uma_semana():
    # Segunda 2026-06-08 -> segunda anterior 2026-06-01 (estritamente antes).
    assert ultima_segunda(date(2026, 6, 8)) == date(2026, 6, 1)


def test_domingo_recua_para_segunda_da_mesma_semana():
    # Domingo 2026-06-07 -> segunda 2026-06-01.
    assert ultima_segunda(date(2026, 6, 7)) == date(2026, 6, 1)


def test_varredura_60_dias_sempre_segunda_anterior():
    # Para 60 dias seguidos, o retorno deve ser sempre uma segunda-feira
    # estritamente anterior à data dada, e a no máximo 7 dias de distância.
    base = date(2026, 1, 1)
    for i in range(60):
        dia = base + timedelta(days=i)
        resultado = ultima_segunda(dia)
        assert resultado.weekday() == 0          # é segunda-feira
        assert resultado < dia                   # estritamente anterior
        assert (dia - resultado).days <= 7       # no máximo uma semana atrás


# --------------------------------------------------------------------------
# Teste de rede (download real)
# --------------------------------------------------------------------------

@pytest.mark.network
def test_baixar_download_real(tmp_path):
    data_pub, caminho = baixar(tmp_path)

    # Arquivo criado.
    assert caminho.exists()

    # Começa com a assinatura %PDF.
    assert caminho.read_bytes()[:4] == b"%PDF"

    # Mais de 50 KB.
    assert caminho.stat().st_size > 50 * 1024

    # Nome do arquivo bate com a data de publicação.
    assert caminho.name == f"focus_{data_pub.isoformat()}.pdf"

    # Data dentro da janela esperada: não no futuro e não muito no passado.
    hoje = date.today()
    assert data_pub <= hoje                       # não no futuro
    assert (hoje - data_pub).days <= 14           # não muito no passado
