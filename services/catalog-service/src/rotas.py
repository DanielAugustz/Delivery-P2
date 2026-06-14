from __future__ import annotations

from flask import Blueprint, jsonify

from catalogo_casos_uso import CasoUsoListarProdutos, CasoUsoObterProduto
from catalogo_infra import RepositorioProdutoMemoria

catalog_bp = Blueprint("catalog", __name__)
_repositorio = RepositorioProdutoMemoria.obter_instancia()


@catalog_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "catalog-service"})


@catalog_bp.get("/produtos")
def listar_produtos():
    produtos = CasoUsoListarProdutos(_repositorio).executar()
    return jsonify([{"codigo": p.codigo, "nome": p.nome, "preco": p.preco} for p in produtos])


@catalog_bp.get("/produtos/<codigo>")
def obter_produto(codigo: str):
    try:
        produto = CasoUsoObterProduto(_repositorio).executar(codigo)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 404
    return jsonify({"codigo": produto.codigo, "nome": produto.nome, "preco": produto.preco})
