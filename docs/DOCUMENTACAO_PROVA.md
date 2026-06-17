# Documentação de Entrega — Prova

## 1. Descrição do Problema

**Sistema de Pedidos** é uma plataforma de pedidos de comida para pequenos restaurantes. O problema real abordado:

- Clientes precisam escolher produtos, calcular valores e pagar de forma simples (PIX ou cartão).
- O negócio precisa de serviços independentes: catálogo, pagamentos e pedidos — para escalar e manter cada parte separadamente.
- A operação exige rastreabilidade (histórico de pedidos com data/hora) e regras de desconto (5% no PIX).

A solução entrega uma interface web onde o usuário monta pedidos (vários produtos, quantidades, carrinho e exclusão); por trás, **quatro microsserviços** se comunicam via HTTP.

---

## 2. Divisão em Microsserviços

| Serviço | Porta | Responsabilidade |
|---------|-------|------------------|
| **catalog-service** | 5001 | Catálogo de produtos (PIZZA, BURGER) |
| **payment-service** | 5002 | Processamento de pagamentos (PIX/Cartão) |
| **order-service** | 5003 | Orquestração de pedidos (catálogo + pagamento + persistência) |
| **api-gateway** | 5000 | Interface web + Facade para o cliente |


**Justificativa:** cada bounded context (catálogo, pagamento, pedido) evolui e escala de forma independente. Falha isolada no pagamento não derruba o catálogo.

---

## 3. Arquitetura Limpa (Clean Architecture)

Cada microsserviço segue **4 camadas em arquivos planos** — regra de dependência: externo depende do interno.

```
services/<nome>/
├── Dockerfile
├── requirements.txt
└── src/
    ├── *_dominio.py       # Entidades e interfaces (domain)
    ├── *_casos_uso.py     # Casos de uso (application)
    ├── *_infra.py         # Repositório/adapters (infrastructure)
    ├── rotas.py           # Rotas Flask (presentation)
    └── principal.py       # Entrada da aplicação
```

**Exemplo — order-service:**
- **pedido_dominio.py:** `Pedido`, `RepositorioPedido`, `PortaCatalogo`, `PortaPagamento`
- **pedido_casos_uso.py:** `CasoUsoCriarPedido`, `CasoUsoListarPedidos`, `CasoUsoExcluirPedido`
- **pedido_infra.py:** `RepositorioPedidoMemoria`, `RepositorioPedidoPostgres`, `obter_repositorio()`, adapters HTTP
- **rotas.py:** `GET/POST /pedidos`, `DELETE /pedidos/<id>`, `GET /health`
- **Persistência:** histórico de pedidos em **PostgreSQL** quando `DATABASE_URL` está definida; memória nos testes

---

## 4. Princípios SOLID

| Princípio | Onde aparece |
|-----------|--------------|
| **S** — Single Responsibility | `CasoUsoProcessarPagamento` só processa pagamento; `CasoUsoListarProdutos` só lista produtos |
| **O** — Open/Closed | `EstrategiaPagamento`: novos métodos (ex.: BOLETO) sem alterar `CasoUsoProcessarPagamento` |
| **L** — Liskov Substitution | `EstrategiaPagamentoPix` e `EstrategiaPagamentoCartao` substituem `EstrategiaPagamento` |
| **I** — Interface Segregation | `PortaCatalogo` e `PortaPagamento` expõem apenas o necessário ao order-service |
| **D** — Dependency Inversion | Casos de uso dependem de `RepositorioPedido`, `PortaCatalogo` (abstrações), não de HTTP direto |

---

## 5. Design Patterns (5 padrões)

| Padrão | Local | Propósito |
|--------|-------|-----------|
| **Strategy** | `EstrategiaPagamento` (PIX/Cartão) | Algoritmos de pagamento intercambiáveis |
| **Singleton** | `RepositorioProdutoMemoria`, `RepositorioPedidoMemoria` | Instância única em memória (testes e fallback local) |
| **Facade** | `FachadaServicoPedidos` (api-gateway) | Interface simplificada para o frontend |
| **Repository** | `RepositorioPedido` → memória ou `RepositorioPedidoPostgres` | Abstração de persistência; PostgreSQL em produção |
| **Adapter** | `AdaptadorCatalogoHttp`, `AdaptadorPagamentoHttp` | Integração REST entre microsserviços |

---

## 6. Clean Code — Evidências

- **Nomes expressivos:** `CasoUsoCriarPedido`, `CasoUsoProcessarPagamento`, `AdaptadorCatalogoHttp`
- **Funções pequenas:** cada caso de uso tem um método `executar()` focado
- **Imutabilidade:** `Produto`, `ResultadoPagamento`, `InfoProduto` como `@dataclass(frozen=True)`
- **Validação no domínio:** `Produto.validar()`, checagem de valor positivo no pagamento
- **Separação de concerns:** Flask só na camada `presentation`
- **DRY moderado:** `_pedido_para_dict` evita repetição nas rotas do order-service

---

## 7. TDD — Testes Unitários

Local: `tests/tdd/`

```bash
pip install -r requirements.txt
python -m pytest tests/tdd -v
```

Total: **18 testes** unitários (catalog, payment, order).

| Arquivo | Cobertura |
|---------|-----------|
| `test_catalog_service.py` | Catálogo, listagem e busca de produtos |
| `test_payment_service.py` | PIX 5%, cartão, validações |
| `test_order_service.py` | Criação, listagem, exclusão, múltiplos produtos e quantidades |

---

## 8. BDD — Cenários de Comportamento

Local: `tests/bdd/features/pedido.feature` (Gherkin em português)

```bash
pytest tests/bdd -v
```

Total: **4 cenários** BDD. Suite completa: `python -m pytest` → **22 testes**.

Cenários:
- Pedido pizza + PIX → valor R$ 47,50
- Pedido burger + cartão → valor R$ 30,00
- Produto inválido → erro
- Pagamento inválido → erro

---

## 9. Docker e Docker Compose

Stack local: **PostgreSQL** + 4 microsserviços.

```bash
docker compose up --build
```

Acesse: **http://localhost:5000**

- **postgres** (5432): banco `sistema_pedidos`; schema em `services/order-service/init.sql`
- **order-service** recebe `DATABASE_URL` e só sobe após postgres, catalog e payment estarem saudáveis

---

## 10. Deploy em Servidor

### Opção recomendada: Render.com (Blueprint)

Repositório: `DanielAugustz/Delivery-P2`

1. Faça push do código para o GitHub (incluindo `render.yaml` na raiz)
2. No Render: **Dashboard → New → Blueprint**
3. Conecte o repositório e aplique o Blueprint
4. O Render cria automaticamente:
   - **pedidos-catalog**, **pedidos-payment**, **pedidos-order** — microsserviços Docker
   - **sistema-pedidos** — api-gateway (único serviço público)
5. Variáveis ligadas pelo Blueprint:
   - `pedidos-order`: `CATALOG_SERVICE_URL`, `PAYMENT_SERVICE_URL`
   - `sistema-pedidos`: `ORDER_SERVICE_URL`
6. **PostgreSQL:** o plano free permite **apenas 1 banco por conta**. O Blueprint **não cria** banco — crie manualmente:
   - Render → **New + → PostgreSQL** (plan Free)
   - Copie a **Internal Database URL**
   - Cole em **`DATABASE_URL`** quando o Blueprint pedir (ou depois em **pedidos-order → Environment**)
   - Sem essa variável, pedidos ficam em memória (somem ao reiniciar o serviço)

Arquivo de referência: `render.yaml`. Instruções detalhadas: `docs/DEPLOY.md`.

### Link publicado

> **Substitua pela URL real do gateway após deploy:**
> `https://sistema-pedidos.onrender.com`

*(A URL exata aparece no dashboard do serviço `sistema-pedidos`.)*

---

## 11. Justificativa Técnica das Escolhas

| Decisão | Justificativa |
|---------|---------------|
| **Python + Flask** | Leve, familiar ao código original, adequado para APIs REST |
| **Microsserviços** | Demonstra separação de responsabilidades exigida na prova |
| **Repository + PostgreSQL** | Histórico persistente em produção; memória nos testes via mesma interface `RepositorioPedido` |
| **HTTP síncrono** | Comunicação clara entre serviços; adapters isolam detalhes |
| **pytest + pytest-bdd** | TDD e BDD no mesmo ecossistema Python |
| **Gunicorn + Docker** | Produção próxima de ambiente real |
| **API Gateway** | Ponto único de entrada; esconde complexidade dos microsserviços |

---

## 12. Estrutura Completa do Repositório

```
Sistema-de-Pedidos/
├── docs/
│   ├── DOCUMENTACAO_PROVA.md   ← este arquivo
│   └── DEPLOY.md
├── services/
│   ├── catalog-service/
│   ├── payment-service/
│   ├── order-service/
│   │   └── init.sql            ← schema PostgreSQL
│   └── api-gateway/
├── tests/
│   ├── tdd/                    ← TDD
│   └── bdd/                    ← BDD (Gherkin)
├── docker-compose.yml
├── render.yaml
├── pytest.ini
├── requirements.txt            ← dependências de teste (pytest, pytest-bdd)
└── README.md
```

