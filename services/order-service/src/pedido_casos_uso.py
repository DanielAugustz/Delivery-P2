from __future__ import annotations

from pedido_dominio import Pedido, PortaCatalogo, PortaPagamento, RepositorioPedido


class CasoUsoCriarPedido:
    def __init__(self, catalogo: PortaCatalogo, pagamento: PortaPagamento, repositorio: RepositorioPedido) -> None:
        self._catalogo = catalogo
        self._pagamento = pagamento
        self._repositorio = repositorio

    def executar(self, codigo_produto: str, metodo_pagamento: str) -> Pedido:
        produto = self._catalogo.obter_produto(codigo_produto)
        resultado = self._pagamento.processar(produto.preco, metodo_pagamento)
        pedido = Pedido(
            codigo_produto=produto.codigo,
            nome_produto=produto.nome,
            preco_original=produto.preco,
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
