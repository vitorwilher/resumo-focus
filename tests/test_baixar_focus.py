"""Testes para src/baixar_focus.py.

Os testes de `ultima_segunda` são puros (sem rede). O teste de `baixar` faz
download real do PDF do BCB e está marcado com @pytest.mark.network — rode
'pytest -m "not network"' para pulá-lo.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# A pasta src/ não é um pacote instalável: inserimos seu caminho no sys.path
# para importar os módulos diretamente (mesmo padrão usado no demo.py).
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from baixar_focus import baixar, ultima_segunda  # noqa: E402


# ---------------------------------------------------------------------------
# Testes puros (sem rede) de ultima_segunda
# ---------------------------------------------------------------------------

def test_ultima_segunda_a_partir_de_quinta():
    """Quinta-feira deve recuar até a segunda da mesma semana."""
    # 2026-06-04 é uma quinta-feira; a segunda anterior é 2026-06-01.
    assert ultima_segunda(date(2026, 6, 4)) == date(2026, 6, 1)


def test_ultima_segunda_a_partir_de_terca():
    """Terça-feira deve recuar até a segunda da mesma semana."""
    # 2026-06-09 é uma terça-feira; a segunda anterior é 2026-06-08.
    assert ultima_segunda(date(2026, 6, 9)) == date(2026, 6, 8)


def test_ultima_segunda_quando_hoje_e_segunda_recua_uma_semana():
    """Se a data já é segunda, deve devolver a segunda da semana anterior."""
    # 2026-06-08 é uma segunda-feira; o esperado é 2026-06-01 (semana passada).
    resultado = ultima_segunda(date(2026, 6, 8))
    assert resultado == date(2026, 6, 1)
    # Garante que nunca devolve a própria data recebida.
    assert resultado < date(2026, 6, 8)


def test_ultima_segunda_a_partir_de_domingo():
    """Domingo deve recuar até a segunda da mesma semana (6 dias atrás)."""
    # 2026-06-07 é um domingo; a segunda anterior é 2026-06-01.
    assert ultima_segunda(date(2026, 6, 7)) == date(2026, 6, 1)


def test_ultima_segunda_varredura_60_dias():
    """Para 60 dias seguidos, o retorno é sempre uma segunda anterior à data."""
    base = date(2026, 1, 1)
    for i in range(60):
        hoje = base + timedelta(days=i)
        resultado = ultima_segunda(hoje)
        # weekday() == 0 significa segunda-feira.
        assert resultado.weekday() == 0, f"{resultado} não é segunda (de {hoje})"
        # O resultado é estritamente anterior à data dada.
        assert resultado < hoje, f"{resultado} não é anterior a {hoje}"
        # E a distância é de no máximo 7 dias (a segunda mais próxima atrás).
        assert (hoje - resultado).days <= 7


# ---------------------------------------------------------------------------
# Teste de rede (download real do PDF do BCB)
# ---------------------------------------------------------------------------

@pytest.mark.network
def test_baixar_download_real(tmp_path):
    """Baixa o Focus de verdade e valida o arquivo, o nome e a data."""
    data_publicacao, caminho = baixar(tmp_path)

    # O arquivo foi de fato criado em disco.
    assert caminho.exists()

    # O conteúdo começa com os bytes mágicos de um PDF.
    conteudo = caminho.read_bytes()
    assert conteudo[:4] == b"%PDF"

    # Um Focus real tem bem mais que 50 KB.
    assert caminho.stat().st_size > 50 * 1024

    # O nome do arquivo bate com a data da publicação retornada.
    assert caminho.name == f"focus_{data_publicacao.isoformat()}.pdf"

    # A data está dentro da janela esperada: não no futuro e não muito no
    # passado (no máximo ~14 dias atrás, cobrindo feriados emendados).
    hoje = date.today()
    assert data_publicacao <= hoje, "data de publicação não pode ser no futuro"
    assert (hoje - data_publicacao).days <= 14, "data de publicação muito antiga"
