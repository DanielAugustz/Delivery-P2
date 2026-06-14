from __future__ import annotations

from catalogo_dominio import Produto, RepositorioProduto


class CasoUsoListarProdutos:
    def __init__(self, repositorio: RepositorioProduto) -> None:
        self._repositorio = repositorio

    def executar(self) -> list[Produto]:
        return self._repositorio.listar_todos()


class CasoUsoObterProduto:
    def __init__(self, repositorio: RepositorioProduto) -> None:
        self._repositorio = repositorio

    def executar(self, codigo: str) -> Produto:
        produto = self._repositorio.buscar_por_codigo(codigo.strip().upper())
        if produto is None:
            raise ValueError(f"Produto não encontrado: {codigo}")
        return produto
