from __future__ import annotations

from pagamento_dominio import (
    EstrategiaPagamentoCartao,
    EstrategiaPagamentoPix,
    ResultadoPagamento,
)


class CasoUsoProcessarPagamento:
    def executar(self, valor: float, metodo: str) -> ResultadoPagamento:
        if valor <= 0:
            raise ValueError("Valor deve ser positivo")
        metodo_maiusculo = metodo.strip().upper()
        if metodo_maiusculo == "PIX":
            estrategia = EstrategiaPagamentoPix()
        elif metodo_maiusculo == "CARTAO":
            estrategia = EstrategiaPagamentoCartao()
        else:
            raise ValueError(f"Método de pagamento inválido: {metodo}")
        valor_final, mensagem = estrategia.processar(valor)
        return ResultadoPagamento(valor, valor_final, estrategia.nome_metodo(), mensagem)
