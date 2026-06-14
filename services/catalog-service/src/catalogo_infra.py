from __future__ import annotations

from typing import List, Optional

from catalogo_dominio import Produto, RepositorioProduto, criar_produto, listar_codigos_disponiveis


class RepositorioProdutoMemoria(RepositorioProduto):
    """Singleton + Repository — catálogo em memória."""

    _instancia: RepositorioProdutoMemoria | None = None

    def __new__(cls) -> RepositorioProdutoMemoria:
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._produtos = [
                criar_produto(codigo) for codigo in listar_codigos_disponiveis()
            ]
        return cls._instancia

    @classmethod
    def obter_instancia(cls) -> RepositorioProdutoMemoria:
        return cls()

    def listar_todos(self) -> List[Produto]:
        return list(self._produtos)

    def buscar_por_codigo(self, codigo: str) -> Optional[Produto]:
        codigo_normalizado = codigo.strip().upper()
        for produto in self._produtos:
            if produto.codigo == codigo_normalizado:
                return produto
        return None
