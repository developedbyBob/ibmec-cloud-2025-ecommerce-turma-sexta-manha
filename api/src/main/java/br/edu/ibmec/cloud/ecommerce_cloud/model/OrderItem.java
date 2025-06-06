package br.edu.ibmec.cloud.ecommerce_cloud.model;

import lombok.Data;

@Data
public class OrderItem {
    private String productId;
    private String productName;
    private Double unitPrice;
    private Integer quantity;
    private Double subTotal;
}