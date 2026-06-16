from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify, render_template, request

from fachada import FachadaServicoPedidos

BASE = Path(__file__).parent
app = Flask(__name__, template_folder=str(BASE / "templates"), static_folder=str(BASE / "static"))
_fachada = FachadaServicoPedidos(os.getenv("ORDER_SERVICE_URL"))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    payload: dict = {"status": "ok", "service": "api-gateway"}
    try:
        payload["order_service"] = _fachada.verificar_saude()
    except Exception as erro:
        payload["order_service"] = {"status": "unreachable", "erro": str(erro)}
    return jsonify(payload)


@app.post("/pedido")
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    itens = dados.get("itens")
    if not itens:
        produtos = dados.get("produtos") or []
        if isinstance(produtos, list) and produtos:
            itens = produtos
        elif dados.get("tipo_produto"):
            itens = [dados.get("tipo_produto")]
        else:
            itens = []
    try:
        resultado = _fachada.criar_pedido(itens, str(dados.get("metodo_pagamento", "")))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except Exception as erro:
        return jsonify({"erro": f"Serviço indisponível: {erro}"}), 503
    return jsonify(resultado), 201


@app.delete("/pedido/<pedido_id>")
def excluir_pedido(pedido_id: str):
    try:
        return jsonify(_fachada.excluir_pedido(pedido_id))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 404
    except Exception as erro:
        return jsonify({"erro": f"Serviço indisponível: {erro}"}), 503


@app.get("/pedidos")
def listar_pedidos():
    try:
        return jsonify(_fachada.listar_pedidos())
    except Exception as erro:
        return jsonify({"erro": f"Serviço indisponível: {erro}"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
