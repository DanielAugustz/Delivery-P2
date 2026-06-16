from __future__ import annotations

import os

import requests


def _normalizar_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return url


class FachadaServicoPedidos:
    """Facade Pattern — simplifica acesso ao order-service."""

    def __init__(self, url_servico_pedidos: str | None = None) -> None:
        self._url_base = _normalizar_url(
            url_servico_pedidos or os.getenv("ORDER_SERVICE_URL", "http://order-service:5003")
        )

    def criar_pedido(self, tipo_produto: str, metodo_pagamento: str) -> dict:
        resposta = requests.post(
            f"{self._url_base}/pedidos",
            json={"tipo_produto": tipo_produto, "metodo_pagamento": metodo_pagamento},
            timeout=15,
        )
        dados = resposta.json()
        if resposta.status_code >= 400:
            raise ValueError(dados.get("erro", "Erro ao criar pedido"))
        return dados

    def listar_pedidos(self) -> dict:
        resposta = requests.get(f"{self._url_base}/pedidos", timeout=10)
        resposta.raise_for_status()
        return resposta.json()

    def verificar_saude(self) -> dict:
        resposta = requests.get(f"{self._url_base}/health", timeout=5)
        resposta.raise_for_status()
        return resposta.json()
