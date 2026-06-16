var precos = { PIZZA: 50, BURGER: 30 };
var codigos = ["PIZZA", "BURGER"];

function obterItensDoFormulario(form) {
  var itens = [];
  for (var i = 0; i < codigos.length; i++) {
    var codigo = codigos[i];
    var qtd = parseInt(form.elements["qtd_" + codigo].value, 10) || 0;
    if (qtd > 0) itens.push({ codigo: codigo, quantidade: qtd });
  }
  return itens;
}

function atualizarSubtotal() {
  var form = document.getElementById("form-pedido");
  var total = 0;
  var temItem = false;
  for (var i = 0; i < codigos.length; i++) {
    var codigo = codigos[i];
    var qtd = parseInt(form.elements["qtd_" + codigo].value, 10) || 0;
    if (qtd > 0) {
      total += (precos[codigo] || 0) * qtd;
      temItem = true;
    }
  }
  var el = document.getElementById("valor-produto");
  el.textContent = temItem ? "Subtotal: R$ " + total.toFixed(2) : "Subtotal: —";
}

function excluirPedido(id) {
  if (!confirm("Excluir este pedido?")) return;
  fetch("/pedido/" + id, { method: "DELETE" })
    .then(function (r) { return r.json().then(function (d) {
      if (r.ok) carregarPedidos();
      else alert(d.erro || "Erro ao excluir");
    }); })
    .catch(function () { alert("Serviço indisponível."); });
}

function carregarPedidos() {
  fetch("/pedidos")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var pedidos = data.pedidos || [];
      var lista = document.getElementById("lista-pedidos");
      lista.innerHTML = "";
      for (var i = 0; i < pedidos.length; i++) {
        var p = pedidos[i];
        var texto = typeof p === "string" ? p : p.produtos + " — R$ " + (p.valor_final || 0).toFixed(2);
        var id = typeof p === "object" ? p.id : null;
        var li = document.createElement("li");
        li.className = "item-pedido";
        li.innerHTML = "<span>" + (i + 1) + ". " + texto + "</span>";
        if (id) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn-excluir";
          btn.textContent = "Excluir";
          btn.onclick = function (pedidoId) { return function () { excluirPedido(pedidoId); }; }(id);
          li.appendChild(btn);
        }
        lista.appendChild(li);
      }
      document.getElementById("total-pedidos").textContent = "Total: " + pedidos.length;
      document.getElementById("lista-vazia").style.display = pedidos.length ? "none" : "block";
    });
}

codigos.forEach(function (codigo) {
  document.querySelector('input[name="qtd_' + codigo + '"]').oninput = atualizarSubtotal;
});

document.getElementById("form-pedido").onsubmit = function (e) {
  e.preventDefault();
  var form = e.target;
  var itens = obterItensDoFormulario(form);
  if (!itens.length) {
    alert("Informe a quantidade de ao menos um produto.");
    return;
  }
  var resultado = document.getElementById("resultado");
  fetch("/pedido", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ itens: itens, metodo_pagamento: form.elements.metodo_pagamento.value })
  })
    .then(function (r) { return r.json().then(function (d) {
      if (r.ok) {
        resultado.textContent = (d.log || []).join("\n");
        resultado.className = "resultado";
        form.reset();
        atualizarSubtotal();
        carregarPedidos();
      } else {
        resultado.textContent = d.erro || "Erro";
        resultado.className = "resultado erro";
      }
    }); })
    .catch(function () { resultado.textContent = "Serviço indisponível."; resultado.className = "resultado erro"; });
};

document.getElementById("btn-atualizar").onclick = carregarPedidos;
carregarPedidos();
