"""TDD — Payment Service"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "payment-service" / "src"))

from pagamento_casos_uso import CasoUsoProcessarPagamento  # noqa: E402


class TestCasoUsoProcessarPagamento:
    def setup_method(self):
        self.caso_uso = CasoUsoProcessarPagamento()

    def test_pix_aplica_desconto_de_cinco_porcento(self):
        assert self.caso_uso.executar(100.0, "PIX").valor_final == 95.0

    def test_cartao_mantem_valor_original(self):
        assert self.caso_uso.executar(30.0, "CARTAO").valor_final == 30.0

    def test_rejeita_valor_zero(self):
        with pytest.raises(ValueError, match="positivo"):
            self.caso_uso.executar(0, "PIX")

    def test_rejeita_metodo_invalido(self):
        with pytest.raises(ValueError, match="inválido"):
            self.caso_uso.executar(50.0, "BOLETO")
