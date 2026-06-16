from __future__ import annotations

from pedido_dominio import ItemPedido, Pedido, PortaCatalogo, PortaPagamento, RepositorioPedido


def _normalizar_itens(itens_pedido: dict[str, int] | list | str) -> dict[str, int]:
    if isinstance(itens_pedido, str):
        codigo = itens_pedido.strip().upper()
        return {codigo: 1} if codigo else {}

    if isinstance(itens_pedido, list):
        resultado: dict[str, int] = {}
        for item in itens_pedido:
            if isinstance(item, dict):
                codigo = str(item.get("codigo", "")).strip().upper()
                quantidade = int(item.get("quantidade", 1))
            else:
                codigo = str(item).strip().upper()
                quantidade = 1
            if codigo and quantidade > 0:
                resultado[codigo] = resultado.get(codigo, 0) + quantidade
        return resultado

    if isinstance(itens_pedido, dict):
        resultado = {}
        for codigo, quantidade in itens_pedido.items():
            codigo_limpo = str(codigo).strip().upper()
            qtd = int(quantidade)
            if codigo_limpo and qtd > 0:
                resultado[codigo_limpo] = resultado.get(codigo_limpo, 0) + qtd
        return resultado

    return {}


class CasoUsoCriarPedido:
    def __init__(self, catalogo: PortaCatalogo, pagamento: PortaPagamento, repositorio: RepositorioPedido) -> None:
        self._catalogo = catalogo
        self._pagamento = pagamento
        self._repositorio = repositorio

    def executar(self, itens_pedido: dict[str, int] | list | str, metodo_pagamento: str) -> Pedido:
        itens_qtd = _normalizar_itens(itens_pedido)
        if not itens_qtd:
            raise ValueError("Informe ao menos um produto")

        itens: list[ItemPedido] = []
        total = 0.0
        for codigo, quantidade in itens_qtd.items():
            produto = self._catalogo.obter_produto(codigo)
            itens.append(ItemPedido(produto.codigo, produto.nome, produto.preco, quantidade))
            total += produto.preco * quantidade

        resultado = self._pagamento.processar(total, metodo_pagamento)
        pedido = Pedido(
            itens=itens,
            preco_original=total,
            preco_final=resultado.valor_final,
            metodo_pagamento=resultado.metodo,
            mensagem_pagamento=resultado.mensagem,
        )
        return self._repositorio.salvar(pedido)


class CasoUsoListarPedidos:
    def __init__(self, repositorio: RepositorioPedido) -> None:
        self._repositorio = repositorio

    def executar(self) -> list[Pedido]:
        return self._repositorio.listar_todos()


class CasoUsoExcluirPedido:
    def __init__(self, repositorio: RepositorioPedido) -> None:
        self._repositorio = repositorio

    def executar(self, pedido_id: str) -> None:
        if not self._repositorio.excluir(pedido_id.strip()):
            raise ValueError(f"Pedido não encontrado: {pedido_id}")
