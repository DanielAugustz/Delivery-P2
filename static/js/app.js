var precos = { PIZZA: 50, BURGER: 30 };

function carregarPedidos() {
  fetch("/pedidos")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var pedidos = data.pedidos || [];
      var lista = document.getElementById("lista-pedidos");
      var i;

      lista.innerHTML = "";
      for (i = 0; i < pedidos.length; i++) {
        lista.innerHTML += "<li>" + (i + 1) + ". " + pedidos[i] + "</li>";
      }
      document.getElementById("total-pedidos").textContent = "Total: " + pedidos.length;
      document.getElementById("lista-vazia").style.display = pedidos.length ? "none" : "block";
    });
}

document.getElementById("select-produto").onchange = function () {
  var el = document.getElementById("valor-produto");
  if (precos[this.value]) {
    el.textContent = "Valor: R$ " + precos[this.value];
  } else {
    el.textContent = "Valor: —";
  }
};

document.getElementById("form-pedido").onsubmit = function (e) {
  e.preventDefault();
  var fd = new FormData(this);

  fetch("/pedido", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tipo_produto: fd.get("tipo_produto"),
      metodo_pagamento: fd.get("metodo_pagamento")
    })
  })
    .then(function (r) {
      return r.json().then(function (data) {
        if (r.ok) {
          document.getElementById("resultado").textContent = (data.log || []).join("\n");
          document.getElementById("resultado").className = "resultado";
          carregarPedidos();
        } else {
          document.getElementById("resultado").textContent = data.erro || "Erro";
          document.getElementById("resultado").className = "resultado";
        }
      });
    });
};

document.getElementById("btn-atualizar").onclick = carregarPedidos;

carregarPedidos();
