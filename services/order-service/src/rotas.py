from __future__ import annotations

import os

from flask import Blueprint, jsonify, request

from pedido_casos_uso import CasoUsoCriarPedido, CasoUsoExcluirPedido, CasoUsoListarPedidos
from pedido_infra import AdaptadorCatalogoHttp, AdaptadorPagamentoHttp, obter_repositorio

order_bp = Blueprint("order", __name__)
_repositorio = obter_repositorio()


def _pedido_para_dict(pedido) -> dict:
    return {
        "id": pedido.id,
        "produtos": pedido.resumo_produtos(),
        "itens": [
            {
                "codigo": i.codigo,
                "nome": i.nome,
                "preco_unitario": i.preco_unitario,
                "quantidade": i.quantidade,
                "subtotal": i.subtotal,
            }
            for i in pedido.itens
        ],
        "valor_original": pedido.preco_original,
        "valor_final": pedido.preco_final,
        "metodo_pagamento": pedido.metodo_pagamento,
        "criado_em": pedido.criado_em,
    }


def _extrair_itens(dados: dict):
    if itens := dados.get("itens"):
        if isinstance(itens, list):
            return itens
    if produtos := dados.get("produtos"):
        if isinstance(produtos, dict):
            return produtos
        if isinstance(produtos, list):
            return produtos
    if tipo := dados.get("tipo_produto"):
        return [str(tipo)]
    return []


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
        ).executar(_extrair_itens(dados), str(dados.get("metodo_pagamento", "")))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    linhas_log = pedido.linhas_resumo()
    linhas_log.append(f"Total de pedidos: {_repositorio.contar()}")
    return jsonify(
        {
            "log": linhas_log,
            "pedido": _pedido_para_dict(pedido),
            "produto": pedido.resumo_produtos(),
            "valor": pedido.preco_original,
        }
    ), 201


@order_bp.get("/pedidos")
def listar_pedidos():
    pedidos = CasoUsoListarPedidos(_repositorio).executar()
    return jsonify({"pedidos": [_pedido_para_dict(p) for p in pedidos], "total": len(pedidos)})


@order_bp.delete("/pedidos/<pedido_id>")
def excluir_pedido(pedido_id: str):
    try:
        CasoUsoExcluirPedido(_repositorio).executar(pedido_id)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 404
    return jsonify({"mensagem": "Pedido excluído", "total": _repositorio.contar()})
