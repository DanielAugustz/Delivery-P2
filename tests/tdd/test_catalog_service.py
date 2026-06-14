"""TDD — Catalog Service"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "catalog-service" / "src"))

from catalogo_dominio import criar_produto  # noqa: E402
from catalogo_casos_uso import CasoUsoListarProdutos, CasoUsoObterProduto  # noqa: E402
from catalogo_infra import RepositorioProdutoMemoria  # noqa: E402


@pytest.fixture
def repositorio():
    return RepositorioProdutoMemoria.obter_instancia()


class TestCatalogo:
    def test_deve_criar_pizza_com_preco_correto(self):
        produto = criar_produto("PIZZA")
        assert produto.nome == "Pizza Grande"
        assert produto.preco == 50.0

    def test_deve_rejeitar_tipo_invalido(self):
        with pytest.raises(ValueError, match="inválido"):
            criar_produto("SUSHI")


class TestCasoUsoListarProdutos:
    def test_deve_listar_todos_produtos(self, repositorio):
        assert {p.codigo for p in CasoUsoListarProdutos(repositorio).executar()} == {"PIZZA", "BURGER"}


class TestCasoUsoObterProduto:
    def test_deve_buscar_burger(self, repositorio):
        assert CasoUsoObterProduto(repositorio).executar("BURGER").preco == 30.0

    def test_deve_falhar_produto_inexistente(self, repositorio):
        with pytest.raises(ValueError, match="não encontrado"):
            CasoUsoObterProduto(repositorio).executar("INVALIDO")
