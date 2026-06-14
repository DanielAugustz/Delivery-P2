from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

CATALOGO: dict[str, tuple[str, float]] = {
    "PIZZA": ("Pizza Grande", 50.0),
    "BURGER": ("Hambúrguer Artesanal", 30.0),
}


@dataclass(frozen=True)
class Produto:
    codigo: str
    nome: str
    preco: float

    def validar(self) -> None:
        if not self.codigo.strip():
            raise ValueError("Código do produto é obrigatório")
        if self.preco <= 0:
            raise ValueError("Preço deve ser positivo")


def criar_produto(tipo_produto: str) -> Produto:
    codigo = tipo_produto.strip().upper()
    if codigo not in CATALOGO:
        raise ValueError(f"Tipo de produto inválido: {tipo_produto}")
    nome, preco = CATALOGO[codigo]
    produto = Produto(codigo=codigo, nome=nome, preco=preco)
    produto.validar()
    return produto


def listar_codigos_disponiveis() -> list[str]:
    return list(CATALOGO.keys())


class RepositorioProduto(ABC):
    @abstractmethod
    def listar_todos(self) -> List[Produto]:
        pass

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> Optional[Produto]:
        pass
