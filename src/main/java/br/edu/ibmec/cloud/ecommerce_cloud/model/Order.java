package br.edu.ibmec.cloud.ecommerce_cloud.model;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.data.annotation.Id;

import com.azure.spring.data.cosmos.core.mapping.Container;
import com.azure.spring.data.cosmos.core.mapping.PartitionKey;

import lombok.Data;

@Data
@Container(containerName = "orders")
public class Order {
    
    @Id
    private String id;
    
    @PartitionKey
    private Integer userId;
    
    private LocalDateTime orderDate;
    
    private String status; // "PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"
    
    private Double totalAmount;
    
    private List<OrderItem> items;
    
    private String shippingAddress;
    
    private String paymentInfo;
    
    private String transactionId;
}