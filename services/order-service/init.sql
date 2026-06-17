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
