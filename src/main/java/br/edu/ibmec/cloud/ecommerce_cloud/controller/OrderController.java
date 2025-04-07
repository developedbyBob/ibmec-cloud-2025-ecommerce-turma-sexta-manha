package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Cartao;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Order;
import br.edu.ibmec.cloud.ecommerce_cloud.model.OrderItem;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Product;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.OrderRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.ProductRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.request.CartRequest;
import br.edu.ibmec.cloud.ecommerce_cloud.request.OrderResponse;
import br.edu.ibmec.cloud.ecommerce_cloud.request.TransacaoRequest;
import br.edu.ibmec.cloud.ecommerce_cloud.request.TransacaoResponse;

@RestController
@RequestMapping("/orders")
public class OrderController {

    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private ProductRepository productRepository;
    
    @Autowired
    private UsuarioRepository usuarioRepository;
    
    @Autowired
    private CartaoRepository cartaoRepository;
    
    @Autowired
    private CartaoController cartaoController;
    
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@RequestBody CartRequest cartRequest) {
        OrderResponse response = new OrderResponse();
        
        // Verificar se o usuário existe
        Optional<Usuario> optUser = usuarioRepository.findById(cartRequest.getUserId());
        if (optUser.isEmpty()) {
            response.setMessage("Usuário não encontrado");
            return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
        }
        
        Usuario usuario = optUser.get();
        
        // Calcular o valor total e validar produtos
        Double totalAmount = 0.0;
        List<OrderItem> orderItems = new ArrayList<>();
        
        for (var cartItem : cartRequest.getItems()) {
            // Verificar se o produto existe
            Optional<Product> optProduct = productRepository.findById(cartItem.getProductId());
            if (optProduct.isEmpty()) {
                response.setMessage("Produto não encontrado: " + cartItem.getProductId());
                return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
            }
            
            Product product = optProduct.get();
            
            // Criar item de pedido
            OrderItem orderItem = new OrderItem();
            orderItem.setProductId(product.getId());
            orderItem.setProductName(product.getProductName());
            orderItem.setUnitPrice(product.getPrice());
            orderItem.setQuantity(cartItem.getQuantity());
            orderItem.setSubTotal(product.getPrice() * cartItem.getQuantity());
            
            orderItems.add(orderItem);
            totalAmount += orderItem.getSubTotal();
        }
        
        // Autorizar pagamento
        Optional<Cartao> optCartao = cartaoRepository.findById(Integer.parseInt(cartRequest.getCartaoId()));
        if (optCartao.isEmpty()) {
            response.setMessage("Cartão não encontrado");
            return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
        }
        
        Cartao cartao = optCartao.get();
        
        // Criar request de transação
        TransacaoRequest transacaoRequest = new TransacaoRequest();
        transacaoRequest.setNumero(cartao.getNumero());
        transacaoRequest.setCvv(cartao.getCvv());
        transacaoRequest.setDtExpiracao(cartao.getDtExpiracao());
        transacaoRequest.setValor(totalAmount);
        
        // Autorizar transação
        ResponseEntity<TransacaoResponse> transacaoResponse = 
            cartaoController.authorize(cartRequest.getUserId(), transacaoRequest);
        
        if (transacaoResponse.getStatusCode() != HttpStatus.OK || 
            !"AUTHORIZED".equals(transacaoResponse.getBody().getStatus())) {
            response.setMessage("Transação não autorizada: " + 
                (transacaoResponse.getBody() != null ? transacaoResponse.getBody().getMessage() : "Erro desconhecido"));
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }
        
        // Criar pedido
        Order order = new Order();
        order.setId(UUID.randomUUID().toString());
        order.setUserId(usuario.getId());
        order.setOrderDate(LocalDateTime.now());
        order.setStatus("PAID");
        order.setTotalAmount(totalAmount);
        order.setItems(orderItems);
        
        // Salvar endereço de entrega (primeiro endereço do usuário)
        if (usuario.getEnderecos() != null && !usuario.getEnderecos().isEmpty()) {
            order.setShippingAddress(usuario.getEnderecos().get(0).getLogradouro() + ", " + 
                                    usuario.getEnderecos().get(0).getBairro() + ", " +
                                    usuario.getEnderecos().get(0).getCidade() + ", " +
                                    usuario.getEnderecos().get(0).getEstado());
        }
        
        // Salvar informação do pagamento
        order.setPaymentInfo("Cartão final " + cartao.getNumero().substring(cartao.getNumero().length() - 4));
        order.setTransactionId(transacaoResponse.getBody().getCodigoAutorizacao().toString());
        
        // Salvar o pedido
        orderRepository.save(order);
        
        // Retornar resposta
        response.setOrderId(order.getId());
        response.setStatus(order.getStatus());
        response.setOrderDate(order.getOrderDate());
        response.setTotalAmount(order.getTotalAmount());
        response.setMessage("Pedido criado com sucesso");
        
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }
    
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Order>> getOrdersByUser(@PathVariable Integer userId) {
        // Verificar se o usuário existe
        Optional<Usuario> optUser = usuarioRepository.findById(userId);
        if (optUser.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        
        List<Order> orders = orderRepository.findByUserId(userId);
        return new ResponseEntity<>(orders, HttpStatus.OK);
    }
    
    @GetMapping("/{orderId}")
    public ResponseEntity<Order> getOrderById(@PathVariable String orderId) {
        Optional<Order> optOrder = orderRepository.findById(orderId);
        if (optOrder.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        
        return new ResponseEntity<>(optOrder.get(), HttpStatus.OK);
    }
}