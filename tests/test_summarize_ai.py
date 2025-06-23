import pytest
from summarize_ai import resumir_texto

def test_resumir_texto_curto():
    texto = "Pequeno texto."
    resumo = resumir_texto(texto)
    assert resumo == texto

def test_resumir_texto_longo():
    texto = "Palavra " * 300
    resumo = resumir_texto(texto)
    assert len(resumo) <= 203  # 200 + '...'
    assert resumo.endswith("...") 