from __future__ import annotations

import os
from typing import List

import requests

from pedido_dominio import (
    InfoPagamento,
    InfoProduto,
    Pedido,
    PortaCatalogo,
    PortaPagamento,
    RepositorioPedido,
)


def _normalizar_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return url


class RepositorioPedidoMemoria(RepositorioPedido):
    _instancia: RepositorioPedidoMemoria | None = None

    def __new__(cls) -> RepositorioPedidoMemoria:
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._pedidos: List[Pedido] = []
        return cls._instancia

    @classmethod
    def obter_instancia(cls) -> RepositorioPedidoMemoria:
        return cls()

    def salvar(self, pedido: Pedido) -> Pedido:
        self._pedidos.append(pedido)
        return pedido

    def listar_todos(self) -> List[Pedido]:
        return list(self._pedidos)

    def contar(self) -> int:
        return len(self._pedidos)

    @classmethod
    def resetar_para_testes(cls) -> None:
        if cls._instancia is not None:
            cls._instancia._pedidos = []


class AdaptadorCatalogoHttp(PortaCatalogo):
    def __init__(self, url_base: str | None = None) -> None:
        self._url_base = _normalizar_url(
            url_base or os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:5001")
        )

    def obter_produto(self, codigo: str) -> InfoProduto:
        resposta = requests.get(f"{self._url_base}/produtos/{codigo}", timeout=10)
        if resposta.status_code == 404:
            raise ValueError(f"Produto não encontrado: {codigo}")
        resposta.raise_for_status()
        dados = resposta.json()
        return InfoProduto(dados["codigo"], dados["nome"], dados["preco"])


class AdaptadorPagamentoHttp(PortaPagamento):
    def __init__(self, url_base: str | None = None) -> None:
        self._url_base = _normalizar_url(
            url_base or os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:5002")
        )

    def processar(self, valor: float, metodo: str) -> InfoPagamento:
        resposta = requests.post(
            f"{self._url_base}/pagamentos",
            json={"valor": valor, "metodo": metodo},
            timeout=10,
        )
        if resposta.status_code >= 400:
            raise ValueError(resposta.json().get("erro", "Erro no pagamento"))
        dados = resposta.json()
        return InfoPagamento(dados["valor_original"], dados["valor_final"], dados["metodo"], dados["mensagem"])


class AdaptadorCatalogoMemoria(PortaCatalogo):
    _PRODUTOS = {
        "PIZZA": InfoProduto("PIZZA", "Pizza Grande", 50.0),
        "BURGER": InfoProduto("BURGER", "Hambúrguer Artesanal", 30.0),
    }

    def obter_produto(self, codigo: str) -> InfoProduto:
        produto = self._PRODUTOS.get(codigo.strip().upper())
        if produto is None:
            raise ValueError(f"Produto não encontrado: {codigo}")
        return produto


class AdaptadorPagamentoMemoria(PortaPagamento):
    def processar(self, valor: float, metodo: str) -> InfoPagamento:
        metodo_maiusculo = metodo.strip().upper()
        if metodo_maiusculo == "PIX":
            valor_final = valor * 0.95
            mensagem = f"Pago via PIX com 5% de desconto: R$ {valor_final:.2f}"
        elif metodo_maiusculo == "CARTAO":
            valor_final = valor
            mensagem = f"Pago via Cartão: R$ {valor:.2f}"
        else:
            raise ValueError(f"Método de pagamento inválido: {metodo}")
        return InfoPagamento(valor, valor_final, metodo_maiusculo, mensagem)
