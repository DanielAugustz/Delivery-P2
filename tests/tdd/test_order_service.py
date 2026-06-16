"""TDD — Order Service"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "order-service" / "src"))

from pedido_casos_uso import CasoUsoCriarPedido, CasoUsoExcluirPedido, CasoUsoListarPedidos  # noqa: E402
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
        assert caso_criacao.executar(["PIZZA"], "PIX").preco_final == 47.5

    def test_deve_criar_pedido_burger_com_cartao(self, caso_criacao):
        assert caso_criacao.executar(["BURGER"], "CARTAO").preco_final == 30.0

    def test_deve_criar_pedido_com_varios_produtos(self, caso_criacao):
        pedido = caso_criacao.executar(["PIZZA", "BURGER"], "PIX")
        assert pedido.preco_original == 80.0
        assert pedido.preco_final == 76.0
        assert len(pedido.itens) == 2

    def test_deve_criar_pedido_com_quantidades(self, caso_criacao):
        pedido = caso_criacao.executar({"PIZZA": 2, "BURGER": 2}, "PIX")
        assert pedido.preco_original == 160.0
        assert pedido.preco_final == 152.0
        assert pedido.resumo_produtos() == "2x Pizza Grande, 2x Hambúrguer Artesanal"
        assert len(pedido.itens) == 2
        assert pedido.itens[0].quantidade == 2

    def test_deve_rejeitar_sem_produtos(self, caso_criacao):
        with pytest.raises(ValueError, match="ao menos um produto"):
            caso_criacao.executar([], "PIX")

    def test_deve_rejeitar_produto_invalido(self, caso_criacao):
        with pytest.raises(ValueError, match="não encontrado"):
            caso_criacao.executar(["SUSHI"], "PIX")


class TestCasoUsoListarPedidos:
    def test_deve_listar_pedidos_criados(self, repositorio, caso_criacao):
        caso_criacao.executar(["PIZZA"], "CARTAO")
        caso_criacao.executar(["BURGER"], "PIX")
        assert len(CasoUsoListarPedidos(repositorio).executar()) == 2


class TestCasoUsoExcluirPedido:
    def test_deve_excluir_pedido_existente(self, repositorio, caso_criacao):
        pedido = caso_criacao.executar(["PIZZA"], "PIX")
        CasoUsoExcluirPedido(repositorio).executar(pedido.id)
        assert len(CasoUsoListarPedidos(repositorio).executar()) == 0

    def test_deve_falhar_pedido_inexistente(self, repositorio):
        with pytest.raises(ValueError, match="não encontrado"):
            CasoUsoExcluirPedido(repositorio).executar("invalido")
