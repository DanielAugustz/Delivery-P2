from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import uuid4


@dataclass(frozen=True)
class ItemPedido:
    codigo: str
    nome: str
    preco_unitario: float
    quantidade: int = 1

    @property
    def subtotal(self) -> float:
        return self.preco_unitario * self.quantidade


@dataclass
class Pedido:
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    itens: List[ItemPedido] = field(default_factory=list)
    preco_original: float = 0.0
    preco_final: float = 0.0
    metodo_pagamento: str = ""
    mensagem_pagamento: str = ""
    criado_em: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def resumo_produtos(self) -> str:
        partes = []
        for item in self.itens:
            prefixo = f"{item.quantidade}x " if item.quantidade > 1 else ""
            partes.append(f"{prefixo}{item.nome}")
        return ", ".join(partes)

    def linhas_resumo(self) -> list[str]:
        linhas = ["--- Pedido Feito ---"]
        try:
            dt = datetime.fromisoformat(self.criado_em.replace("Z", "+00:00"))
            linhas.append(f"Data: {dt.strftime('%d/%m/%Y %H:%M')} UTC")
        except (ValueError, AttributeError):
            if self.criado_em:
                linhas.append(f"Data: {self.criado_em}")
        for item in self.itens:
            prefixo = f"{item.quantidade}x " if item.quantidade > 1 else ""
            linhas.append(f"  {prefixo}{item.nome}: R$ {item.subtotal:.2f}")
        linhas.append(f"Subtotal: R$ {self.preco_original:.2f}")
        linhas.append(self.mensagem_pagamento)
        linhas.append(f"Total: R$ {self.preco_final:.2f}")
        return linhas


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

    @abstractmethod
    def excluir(self, pedido_id: str) -> bool:
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
