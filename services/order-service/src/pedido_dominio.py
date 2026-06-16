from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import uuid4


@dataclass
class Pedido:
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    codigo_produto: str = ""
    nome_produto: str = ""
    preco_original: float = 0.0
    preco_final: float = 0.0
    metodo_pagamento: str = ""
    mensagem_pagamento: str = ""
    criado_em: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def linhas_resumo(self) -> list[str]:
        return [
            "--- Último Pedido Feito ---",
            f"Produto: {self.nome_produto}",
            f"Valor do produto: R$ {self.preco_original:.2f}",
            self.mensagem_pagamento,
        ]


class RepositorioPedido(ABC):
    @abstractmethod
    def salvar(self, pedido: Pedido) -> Pedido:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Pedido]:
        pass

    @abstractmethod
    def contar(self) -> int:
        pass


@dataclass(frozen=True)
class InfoProduto:
    codigo: str
    nome: str
    preco: float


@dataclass(frozen=True)
class InfoPagamento:
    valor_original: float
    valor_final: float
    metodo: str
    mensagem: str


class PortaCatalogo(ABC):
    @abstractmethod
    def obter_produto(self, codigo: str) -> InfoProduto:
        pass


class PortaPagamento(ABC):
    @abstractmethod
    def processar(self, valor: float, metodo: str) -> InfoPagamento:
        pass
