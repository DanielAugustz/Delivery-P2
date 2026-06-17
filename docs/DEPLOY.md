# Guia de Deploy — T2 Delivery

Repositório: [DanielAugustz/Delivery-P2](https://github.com/DanielAugustz/Delivery-P2)

## Render.com (Blueprint — recomendado)

### Pré-requisitos

- Conta em [render.com](https://render.com)
- Código no GitHub (branch `main`)

### Passo a passo

1. **Dashboard → New → Blueprint**
2. Conecte o repositório **Delivery-P2**
3. Aplique o Blueprint — serão criados 4 serviços:
   - `t2-catalog`, `t2-payment`, `t2-order`, `delivery-p2`
4. Quando pedir `DATABASE_URL` no `t2-order`:
   - **Com Postgres existente:** cole a **Internal Database URL** do seu banco Render
   - **Sem banco / só prova:** deixe em branco → pedidos em memória
5. Aguarde todos os deploys ficarem **Live**
6. Acesse a URL do serviço **`delivery-p2`**

### PostgreSQL no plano free

O Render free permite **apenas 1 banco PostgreSQL ativo por conta**.

Por isso o `render.yaml` **não cria** banco automaticamente (evita erro *"cannot have more than one active free tier database"*).

**Para histórico persistente:**

1. Render → **Postgres** → use o banco que você já tem (ou apague um antigo se não usar)
2. Copie **Internal Database URL**
3. **t2-order → Environment → `DATABASE_URL`** → cole a URL → Save → redeploy

O schema (`pedidos`, `pedido_itens`) é criado automaticamente na primeira conexão pelo `order-service`.

### Health check

```bash
curl https://SEU-GATEWAY.onrender.com/health
```

Substitua pela URL real do `delivery-p2`.

---

## Docker Compose (local)

```bash
docker compose up --build
```

Acesse: http://localhost:5000

Localmente o Postgres sobe no Compose com `DATABASE_URL` já configurada.

---

## Deploy manual (alternativa ao Blueprint)

Crie 4 Web Services (Runtime: Docker), um por pasta em `services/`:

| Serviço | Root Directory | Porta |
|---------|----------------|-------|
| t2-catalog | `services/catalog-service` | 5001 |
| t2-payment | `services/payment-service` | 5002 |
| t2-order | `services/order-service` | 5003 |
| delivery-p2 | `services/api-gateway` | 5000 |

Variáveis:

- **t2-order:** `CATALOG_SERVICE_URL`, `PAYMENT_SERVICE_URL`, `DATABASE_URL` (opcional)
- **delivery-p2:** `ORDER_SERVICE_URL` → URL do `t2-order`

Exponha publicamente apenas o **delivery-p2**.
