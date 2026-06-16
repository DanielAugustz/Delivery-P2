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
    try:
        return jsonify({"status": "ok", "service": "api-gateway", "order_service": _fachada.verificar_saude()})
    except Exception as erro:
        return jsonify({"status": "degraded", "erro": str(erro)}), 503


@app.post("/pedido")
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    try:
        resultado = _fachada.criar_pedido(
            str(dados.get("tipo_produto", "")),
            str(dados.get("metodo_pagamento", "")),
        )
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except Exception as erro:
        return jsonify({"erro": f"Serviço indisponível: {erro}"}), 503
    return jsonify(resultado), 201


@app.get("/pedidos")
def listar_pedidos():
    try:
        return jsonify(_fachada.listar_pedidos())
    except Exception as erro:
        return jsonify({"erro": f"Serviço indisponível: {erro}"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
