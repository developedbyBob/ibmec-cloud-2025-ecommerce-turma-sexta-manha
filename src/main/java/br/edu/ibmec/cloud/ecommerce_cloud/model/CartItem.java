package br.edu.ibmec.cloud.ecommerce_cloud.model;

import lombok.Data;

@Data
public class CartItem {
    private String productId;
    private String productName;
    private Double price;
    private Integer quantity;
}