var precos = { PIZZA: 50, BURGER: 30 };

function carregarPedidos() {
  fetch("/pedidos")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var pedidos = data.pedidos || [];
      var lista = document.getElementById("lista-pedidos");
      lista.innerHTML = "";
      for (var i = 0; i < pedidos.length; i++) {
        lista.innerHTML += "<li>" + (i + 1) + ". " + pedidos[i] + "</li>";
      }
      document.getElementById("total-pedidos").textContent = "Total: " + pedidos.length;
      document.getElementById("lista-vazia").style.display = pedidos.length ? "none" : "block";
    });
}

document.getElementById("select-produto").onchange = function () {
  var el = document.getElementById("valor-produto");
  el.textContent = precos[this.value] ? "Valor: R$ " + precos[this.value].toFixed(2) : "Valor: —";
};

document.getElementById("form-pedido").onsubmit = function (e) {
  e.preventDefault();
  var fd = new FormData(this);
  var resultado = document.getElementById("resultado");
  fetch("/pedido", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tipo_produto: fd.get("tipo_produto"), metodo_pagamento: fd.get("metodo_pagamento") })
  })
    .then(function (r) { return r.json().then(function (d) {
      if (r.ok) { resultado.textContent = (d.log || []).join("\n"); resultado.className = "resultado"; carregarPedidos(); }
      else { resultado.textContent = d.erro || "Erro"; resultado.className = "resultado erro"; }
    }); })
    .catch(function () { resultado.textContent = "Serviço indisponível."; resultado.className = "resultado erro"; });
};

document.getElementById("btn-atualizar").onclick = carregarPedidos;
carregarPedidos();
