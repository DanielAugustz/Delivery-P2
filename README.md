# T2 Delivery — Plataforma de Pedidos (Prova Acadêmica)

Plataforma de delivery com pizza e hambúrguer. Pagamento PIX (5% desconto) ou cartão.
Arquitetura de **4 microsserviços** com Arquitetura Limpa, SOLID, TDD e BDD.

| Serviço | Porta | Função |
|---------|-------|--------|
| catalog-service | 5001 | Catálogo |
| payment-service | 5002 | Pagamentos |
| order-service | 5003 | Pedidos |
| api-gateway | 5000 | Interface web |

**Deploy:** https://t2-gateway.onrender.com  
**Documentação:** [docs/DOCUMENTACAO_PROVA.md](docs/DOCUMENTACAO_PROVA.md)

## Executar com Docker
...
## Testes
pip install -r requirements.txt   # dependências de teste
python -m pytest