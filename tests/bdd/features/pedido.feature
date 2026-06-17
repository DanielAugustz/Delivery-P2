# language: pt
Funcionalidade: Realizar pedido no Sistema de Pedidos
  Como cliente de delivery
  Eu quero fazer pedidos de comida
  Para receber refeições com pagamento conveniente

  Cenário: Pedido de pizza pago com PIX
    Dado que o catálogo possui o produto "PIZZA" por R$ 50
    Quando eu realizo um pedido de "PIZZA" com pagamento "PIX"
    Então o valor final do pedido deve ser R$ 47.50
    E o método de pagamento deve ser "PIX"

  Cenário: Pedido de hambúrguer pago com cartão
    Dado que o catálogo possui o produto "BURGER" por R$ 30
    Quando eu realizo um pedido de "BURGER" com pagamento "CARTAO"
    Então o valor final do pedido deve ser R$ 30.00
    E o método de pagamento deve ser "CARTAO"

  Cenário: Produto inválido no pedido
    Quando eu tento realizar um pedido de "SUSHI" com pagamento "PIX"
    Então devo receber erro de produto não encontrado

  Cenário: Pagamento inválido
    Dado que o catálogo possui o produto "PIZZA" por R$ 50
    Quando eu tento realizar um pedido de "PIZZA" com pagamento "BOLETO"
    Então devo receber erro de pagamento inválido
