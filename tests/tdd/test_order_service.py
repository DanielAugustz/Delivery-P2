"""TDD — Order Service"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "order-service" / "src"))

from pedido_casos_uso import CasoUsoCriarPedido, CasoUsoListarPedidos  # noqa: E402
from pedido_infra import AdaptadorCatalogoMemoria, AdaptadorPagamentoMemoria, RepositorioPedidoMemoria  # noqa: E402


@pytest.fixture(autouse=True)
def resetar_repositorio():
    RepositorioPedidoMemoria.resetar_para_testes()
    yield
    RepositorioPedidoMemoria.resetar_para_testes()


@pytest.fixture
def repositorio():
    return RepositorioPedidoMemoria.obter_instancia()


@pytest.fixture
def caso_criacao(repositorio):
    return CasoUsoCriarPedido(AdaptadorCatalogoMemoria(), AdaptadorPagamentoMemoria(), repositorio)


class TestCasoUsoCriarPedido:
    def test_deve_criar_pedido_pizza_com_pix(self, caso_criacao):
        assert caso_criacao.executar("PIZZA", "PIX").preco_final == 47.5

    def test_deve_criar_pedido_burger_com_cartao(self, caso_criacao):
        assert caso_criacao.executar("BURGER", "CARTAO").preco_final == 30.0

    def test_deve_rejeitar_produto_invalido(self, caso_criacao):
        with pytest.raises(ValueError, match="não encontrado"):
            caso_criacao.executar("SUSHI", "PIX")


class TestCasoUsoListarPedidos:
    def test_deve_listar_pedidos_criados(self, repositorio, caso_criacao):
        caso_criacao.executar("PIZZA", "CARTAO")
        caso_criacao.executar("BURGER", "PIX")
        assert len(CasoUsoListarPedidos(repositorio).executar()) == 2
