from __future__ import annotations

from flask import Blueprint, jsonify, request

from pagamento_casos_uso import CasoUsoProcessarPagamento

payment_bp = Blueprint("payment", __name__)
_caso_uso = CasoUsoProcessarPagamento()


@payment_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "payment-service"})


@payment_bp.post("/pagamentos")
def processar_pagamento():
    dados = request.get_json(silent=True) or {}
    try:
        resultado = _caso_uso.executar(float(dados.get("valor")), str(dados.get("metodo", "")))
    except (TypeError, ValueError) as erro:
        return jsonify({"erro": str(erro)}), 400
    return jsonify(
        {
            "valor_original": resultado.valor_original,
            "valor_final": resultado.valor_final,
            "metodo": resultado.metodo,
            "mensagem": resultado.mensagem,
        }
    ), 201
