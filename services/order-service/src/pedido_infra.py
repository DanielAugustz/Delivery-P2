from __future__ import annotations

import os
from typing import List

import requests

from pedido_dominio import (
    InfoPagamento,
    InfoProduto,
    ItemPedido,
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

    def excluir(self, pedido_id: str) -> bool:
        for indice, pedido in enumerate(self._pedidos):
            if pedido.id == pedido_id:
                del self._pedidos[indice]
                return True
        return False

    @classmethod
    def resetar_para_testes(cls) -> None:
        if cls._instancia is not None:
            cls._instancia._pedidos = []


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pedidos (
    id VARCHAR(8) PRIMARY KEY,
    preco_original NUMERIC(10, 2) NOT NULL,
    preco_final NUMERIC(10, 2) NOT NULL,
    metodo_pagamento VARCHAR(20) NOT NULL,
    mensagem_pagamento TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS pedido_itens (
    id SERIAL PRIMARY KEY,
    pedido_id VARCHAR(8) NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    codigo VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    preco_unitario NUMERIC(10, 2) NOT NULL,
    quantidade INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_pedido_itens_pedido_id ON pedido_itens(pedido_id);
"""


class RepositorioPedidoPostgres(RepositorioPedido):
    def __init__(self, database_url: str) -> None:
        import psycopg
        from psycopg.rows import dict_row

        self._psycopg = psycopg
        self._dict_row = dict_row
        self._database_url = database_url
        self._garantir_schema()

    def _conectar(self):
        return self._psycopg.connect(self._database_url, row_factory=self._dict_row)

    def _garantir_schema(self) -> None:
        with self._psycopg.connect(self._database_url) as conn:
            conn.execute(_SCHEMA_SQL)
            conn.commit()

    def _montar_pedidos(self, rows: list) -> List[Pedido]:
        pedidos: dict[str, Pedido] = {}
        for row in rows:
            pedido_id = row["id"]
            if pedido_id not in pedidos:
                criado_em = row["criado_em"]
                pedidos[pedido_id] = Pedido(
                    id=pedido_id,
                    preco_original=float(row["preco_original"]),
                    preco_final=float(row["preco_final"]),
                    metodo_pagamento=row["metodo_pagamento"],
                    mensagem_pagamento=row["mensagem_pagamento"],
                    criado_em=criado_em.isoformat() if hasattr(criado_em, "isoformat") else str(criado_em),
                    itens=[],
                )
            if row["codigo"]:
                pedidos[pedido_id].itens.append(
                    ItemPedido(
                        row["codigo"],
                        row["nome"],
                        float(row["preco_unitario"]),
                        int(row["quantidade"]),
                    )
                )
        return list(pedidos.values())

    def salvar(self, pedido: Pedido) -> Pedido:
        with self._conectar() as conn:
            conn.execute(
                """
                INSERT INTO pedidos (id, preco_original, preco_final, metodo_pagamento, mensagem_pagamento, criado_em)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    pedido.id,
                    pedido.preco_original,
                    pedido.preco_final,
                    pedido.metodo_pagamento,
                    pedido.mensagem_pagamento,
                    pedido.criado_em,
                ),
            )
            for item in pedido.itens:
                conn.execute(
                    """
                    INSERT INTO pedido_itens (pedido_id, codigo, nome, preco_unitario, quantidade)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (pedido.id, item.codigo, item.nome, item.preco_unitario, item.quantidade),
                )
            conn.commit()
        return pedido

    def listar_todos(self) -> List[Pedido]:
        with self._conectar() as conn:
            rows = conn.execute(
                """
                SELECT p.id, p.preco_original, p.preco_final, p.metodo_pagamento,
                       p.mensagem_pagamento, p.criado_em,
                       i.codigo, i.nome, i.preco_unitario, i.quantidade
                FROM pedidos p
                LEFT JOIN pedido_itens i ON i.pedido_id = p.id
                ORDER BY p.criado_em DESC, i.id
                """
            ).fetchall()
        return self._montar_pedidos(rows)

    def contar(self) -> int:
        with self._conectar() as conn:
            row = conn.execute("SELECT COUNT(*) AS total FROM pedidos").fetchone()
        return int(row["total"])

    def excluir(self, pedido_id: str) -> bool:
        with self._conectar() as conn:
            result = conn.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
            conn.commit()
        return result.rowcount > 0


def obter_repositorio() -> RepositorioPedido:
    url = os.getenv("DATABASE_URL", "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url:
        return RepositorioPedidoPostgres(url)
    return RepositorioPedidoMemoria.obter_instancia()


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
