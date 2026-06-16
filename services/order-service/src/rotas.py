from __future__ import annotations

import os

from flask import Blueprint, jsonify, request

from pedido_casos_uso import CasoUsoCriarPedido, CasoUsoListarPedidos
from pedido_infra import AdaptadorCatalogoHttp, AdaptadorPagamentoHttp, RepositorioPedidoMemoria

order_bp = Blueprint("order", __name__)
_repositorio = RepositorioPedidoMemoria.obter_instancia()


@order_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "order-service"})


@order_bp.post("/pedidos")
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    try:
        pedido = CasoUsoCriarPedido(
            AdaptadorCatalogoHttp(os.getenv("CATALOG_SERVICE_URL")),
            AdaptadorPagamentoHttp(os.getenv("PAYMENT_SERVICE_URL")),
            _repositorio,
        ).executar(str(dados.get("tipo_produto", "")), str(dados.get("metodo_pagamento", "")))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    linhas_log = pedido.linhas_resumo()
    linhas_log.append(f"Total de pedidos: {_repositorio.contar()}")
    return jsonify(
        {
            "log": linhas_log,
            "pedido": {
                "id": pedido.id,
                "produto": pedido.nome_produto,
                "codigo_produto": pedido.codigo_produto,
                "valor_original": pedido.preco_original,
                "valor_final": pedido.preco_final,
                "metodo_pagamento": pedido.metodo_pagamento,
                "criado_em": pedido.criado_em,
            },
            "produto": pedido.nome_produto,
            "valor": pedido.preco_original,
        }
    ), 201


@order_bp.get("/pedidos")
def listar_pedidos():
    pedidos = CasoUsoListarPedidos(_repositorio).executar()
    return jsonify({"pedidos": [p.nome_produto for p in pedidos], "total": len(pedidos)})
