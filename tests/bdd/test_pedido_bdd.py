"""BDD — pytest-bdd"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "order-service" / "src"))

from pedido_casos_uso import CasoUsoCriarPedido  # noqa: E402
from pedido_infra import AdaptadorCatalogoMemoria, AdaptadorPagamentoMemoria, RepositorioPedidoMemoria  # noqa: E402

scenarios(Path(__file__).parent / "features" / "pedido.feature")


@pytest.fixture(autouse=True)
def resetar_estado():
    RepositorioPedidoMemoria.resetar_para_testes()
    yield
    RepositorioPedidoMemoria.resetar_para_testes()


@pytest.fixture
def contexto():
    return {}


@given(parsers.parse('que o catálogo possui o produto "{codigo}" por R$ {preco:g}'))
def catalogo_possui_produto(contexto, codigo: str, preco: float):
    assert AdaptadorCatalogoMemoria().obter_produto(codigo).preco == preco


@when(parsers.parse('eu realizo um pedido de "{produto}" com pagamento "{metodo}"'))
def realizar_pedido(contexto, produto: str, metodo: str):
    repo = RepositorioPedidoMemoria.obter_instancia()
    contexto["pedido"] = CasoUsoCriarPedido(
        AdaptadorCatalogoMemoria(), AdaptadorPagamentoMemoria(), repo
    ).executar([produto], metodo)


@when(parsers.parse('eu tento realizar um pedido de "{produto}" com pagamento "{metodo}"'))
def tentar_realizar_pedido(contexto, produto: str, metodo: str):
    repo = RepositorioPedidoMemoria.obter_instancia()
    try:
        contexto["pedido"] = CasoUsoCriarPedido(
            AdaptadorCatalogoMemoria(), AdaptadorPagamentoMemoria(), repo
        ).executar([produto], metodo)
        contexto["erro"] = None
    except ValueError as erro:
        contexto["erro"] = str(erro)


@then(parsers.parse("o valor final do pedido deve ser R$ {esperado:g}"))
def verificar_preco_final(contexto, esperado: float):
    assert contexto["pedido"].preco_final == pytest.approx(esperado)


@then(parsers.parse('o método de pagamento deve ser "{metodo}"'))
def verificar_metodo_pagamento(contexto, metodo: str):
    assert contexto["pedido"].metodo_pagamento == metodo


@then("devo receber erro de produto não encontrado")
def verificar_erro_produto(contexto):
    assert contexto["erro"] and "não encontrado" in contexto["erro"].lower()


@then("devo receber erro de pagamento inválido")
def verificar_erro_pagamento(contexto):
    assert contexto["erro"] and "inválido" in contexto["erro"].lower()
