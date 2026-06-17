var precos = { PIZZA: 50, BURGER: 30 };
var nomes = { PIZZA: "Pizza Grande", BURGER: "Hambúrguer Artesanal" };
var carrinho = [];

function renderizarPreviewCarrinho() {
  var preview = document.getElementById("preview-carrinho");
  if (!carrinho.length) {
    preview.className = "preview-carrinho hidden";
    preview.textContent = "";
    return;
  }

  var total = 0;
  var linhas = ["--- Produtos no pedido ---"];
  for (var i = 0; i < carrinho.length; i++) {
    var item = carrinho[i];
    var subtotal = (precos[item.codigo] || 0) * item.quantidade;
    total += subtotal;
    var prefixo = item.quantidade > 1 ? item.quantidade + "x " : "";
    linhas.push(prefixo + nomes[item.codigo] + ": R$ " + subtotal.toFixed(2));
  }
  linhas.push("Subtotal: R$ " + total.toFixed(2));
  preview.className = "preview-carrinho";
  preview.textContent = linhas.join("\n");
}

function formatarDataHora(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "America/Sao_Paulo",
  });
}

function montarLogPedido(pedido, indice, total) {
  var linhas = ["--- Pedido Feito ---"];
  if (pedido.criado_em) {
    linhas.push("Data: " + formatarDataHora(pedido.criado_em));
  }
  if (pedido.itens && pedido.itens.length) {
    for (var j = 0; j < pedido.itens.length; j++) {
      var item = pedido.itens[j];
      var prefixo = item.quantidade > 1 ? item.quantidade + "x " : "";
      var subtotal = item.subtotal != null ? item.subtotal : item.preco_unitario * item.quantidade;
      linhas.push(prefixo + item.nome + ": R$ " + Number(subtotal).toFixed(2));
    }
  } else if (pedido.produtos) {
    linhas.push(pedido.produtos);
  }
  linhas.push("Subtotal: R$ " + Number(pedido.valor_original || 0).toFixed(2));
  if (pedido.metodo_pagamento === "PIX") {
    linhas.push("Pago via PIX com 5% de desconto: R$ " + Number(pedido.valor_final || 0).toFixed(2));
  } else {
    linhas.push("Pago via Cartão: R$ " + Number(pedido.valor_final || 0).toFixed(2));
  }
  linhas.push("Total: R$ " + Number(pedido.valor_final || 0).toFixed(2));
  linhas.push("Total de pedidos: " + total);
  return linhas.join("\n");
}

function renderizarHistorico(pedidos) {
  var container = document.getElementById("historico-pedidos");
  container.innerHTML = "";
  document.getElementById("historico-vazio").style.display = pedidos.length ? "none" : "block";

  for (var i = 0; i < pedidos.length; i++) {
    var pedido = pedidos[i];
    if (typeof pedido === "string") continue;

    var entrada = document.createElement("div");
    entrada.className = "entrada-historico";

    var pre = document.createElement("pre");
    pre.className = "log-conteudo";
    pre.textContent = montarLogPedido(pedido, i, pedidos.length);

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn-excluir";
    btn.textContent = "Excluir";
    btn.onclick = (function (id) {
      return function () {
        excluirPedido(id);
      };
    })(pedido.id);

    entrada.appendChild(pre);
    entrada.appendChild(btn);
    container.appendChild(entrada);
  }
}

function adicionarProduto() {
  var select = document.getElementById("select-produto");
  var codigo = select.value;
  if (!codigo) {
    alert("Selecione um produto.");
    return;
  }
  var qtd = parseInt(document.getElementById("qtd-produto").value, 10) || 0;
  if (qtd < 1) {
    alert("Quantidade deve ser pelo menos 1.");
    return;
  }

  var existente = null;
  for (var i = 0; i < carrinho.length; i++) {
    if (carrinho[i].codigo === codigo) {
      existente = carrinho[i];
      break;
    }
  }
  if (existente) {
    existente.quantidade += qtd;
  } else {
    carrinho.push({ codigo: codigo, quantidade: qtd });
  }

  select.selectedIndex = 0;
  document.getElementById("qtd-produto").value = "1";
  renderizarPreviewCarrinho();
}

function obterItensDoCarrinho() {
  return carrinho.map(function (item) {
    return { codigo: item.codigo, quantidade: item.quantidade };
  });
}

function limparCarrinho() {
  carrinho = [];
  renderizarPreviewCarrinho();
}

function excluirPedido(id) {
  if (!confirm("Excluir este pedido?")) return;
  fetch("/pedido/" + id, { method: "DELETE" })
    .then(function (r) {
      return r.json().then(function (d) {
        if (r.ok) carregarHistorico();
        else alert(d.erro || "Erro ao excluir");
      });
    })
    .catch(function () {
      alert("Serviço indisponível.");
    });
}

function aquecerServicos(callback) {
  fetch("/warmup")
    .then(function (r) {
      return r.json();
    })
    .then(function () {
      if (callback) callback();
    })
    .catch(function () {
      if (callback) callback();
    });
}

function carregarHistorico() {
  fetch("/pedidos")
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      renderizarHistorico(data.pedidos || []);
    })
    .catch(function () {
      alert("Serviço indisponível.");
    });
}

document.getElementById("btn-adicionar").onclick = adicionarProduto;

document.getElementById("form-pedido").onsubmit = function (e) {
  e.preventDefault();
  var form = e.target;
  var itens = obterItensDoCarrinho();
  if (!itens.length) {
    alert("Adicione ao menos um produto com o botão +.");
    return;
  }
  fetch("/pedido", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ itens: itens, metodo_pagamento: form.elements.metodo_pagamento.value }),
  })
    .then(function (r) {
      return r.json().then(function (d) {
        if (r.ok) {
          form.elements.metodo_pagamento.selectedIndex = 0;
          limparCarrinho();
          carregarHistorico();
        } else {
          alert(d.erro || "Falha ao criar pedido");
        }
      });
    })
    .catch(function () {
      alert("Serviço indisponível.");
    });
};

aquecerServicos(carregarHistorico);
