from __future__ import annotations

import sys

from flask import Flask, jsonify, render_template, request

from delivery import DeliveryFacade

app = Flask(__name__)
_facade = DeliveryFacade()


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/pedido")
def criar_pedido():
    data = request.get_json(silent=True) or {}
    tipo = str(data.get("tipo_produto", ""))
    metodo = str(data.get("metodo_pagamento", ""))

    try:
        resultado = _facade.realizar_pedido_completo(tipo, metodo)
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    return jsonify(resultado), 201


@app.get("/pedidos")
def listar_pedidos():
    return jsonify(_facade.listar_pedidos())


def _demo_no_console() -> None:
    sistema = DeliveryFacade()

    r1 = sistema.realizar_pedido_completo("PIZZA", "PIX")
    for linha in r1["log"]:
        print(linha)
    print()

    r2 = sistema.realizar_pedido_completo("BURGER", "CARTAO")
    for linha in r2["log"]:
        print(linha)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        _demo_no_console()
    else:
        app.run(debug=True, port=5000)
