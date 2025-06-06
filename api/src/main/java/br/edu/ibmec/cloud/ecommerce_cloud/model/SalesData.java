package br.edu.ibmec.cloud.ecommerce_cloud.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Classe que representa os dados de vendas que serão enviados para o Event Hub
 * Esta classe contém informações resumidas sobre uma venda para análise
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SalesData {
    
    // ID único da venda
    private String orderId;
    
    // ID do usuário que fez a compra
    private Integer userId;
    
    // Data e hora da venda
    private LocalDateTime saleDate;
    
    // Valor total da venda
    private Double totalAmount;
    
    // Status do pedido
    private String status;
    
    // Quantidade de itens vendidos
    private Integer totalItems;
    
    // Lista dos produtos vendidos (apenas IDs e quantidades)
    private List<SalesItem> items;
    
    // Método de pagamento usado
    private String paymentMethod;
    
    // Cidade do cliente (para análise geográfica)
    private String customerCity;
    
    // Construtor que cria SalesData a partir de um Order
    public SalesData(Order order) {
        this.orderId = order.getId();
        this.userId = order.getUserId();
        this.saleDate = order.getOrderDate();
        this.totalAmount = order.getTotalAmount();
        this.status = order.getStatus();
        this.totalItems = order.getItems().size();
        this.paymentMethod = "Credit Card"; // Por enquanto só temos cartão
        
        // Converter OrderItems para SalesItems (dados simplificados)
        this.items = order.getItems().stream()
                .map(orderItem -> new SalesItem(
                    orderItem.getProductId(),
                    orderItem.getProductName(),
                    orderItem.getQuantity(),
                    orderItem.getUnitPrice()
                ))
                .collect(java.util.stream.Collectors.toList());
        
        // Se tiver endereço, pegar a cidade
        if (order.getShippingAddress() != null && !order.getShippingAddress().isEmpty()) {
            // Extrair cidade do endereço (formato: "rua, bairro, cidade, estado")
            String[] addressParts = order.getShippingAddress().split(", ");
            if (addressParts.length >= 3) {
                this.customerCity = addressParts[2];
            } else {
                this.customerCity = "Unknown";
            }
        } else {
            this.customerCity = "Unknown";
        }
    }
    
    /**
     * Classe interna que representa um item vendido de forma simplificada
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SalesItem {
        private String productId;
        private String productName;
        private Integer quantity;
        private Double unitPrice;
    }
}