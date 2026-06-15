from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class EstrategiaPagamento(ABC):
    @abstractmethod
    def processar(self, valor: float) -> tuple[float, str]:
        pass

    @abstractmethod
    def nome_metodo(self) -> str:
        pass


class EstrategiaPagamentoPix(EstrategiaPagamento):
    def processar(self, valor: float) -> tuple[float, str]:
        valor_final = valor * 0.95
        return valor_final, f"Pago via PIX com 5% de desconto: R$ {valor_final:.2f}"

    def nome_metodo(self) -> str:
        return "PIX"


class EstrategiaPagamentoCartao(EstrategiaPagamento):
    def processar(self, valor: float) -> tuple[float, str]:
        return valor, f"Pago via Cartão: R$ {valor:.2f}"

    def nome_metodo(self) -> str:
        return "CARTAO"


@dataclass(frozen=True)
class ResultadoPagamento:
    valor_original: float
    valor_final: float
    metodo: str
    mensagem: str
