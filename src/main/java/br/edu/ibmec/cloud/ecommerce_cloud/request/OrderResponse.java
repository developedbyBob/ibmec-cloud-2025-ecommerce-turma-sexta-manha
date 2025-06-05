package br.edu.ibmec.cloud.ecommerce_cloud.request;

import java.time.LocalDateTime;

import lombok.Data;

@Data
public class OrderResponse {
    private String orderId;
    private String status;
    private LocalDateTime orderDate;
    private Double totalAmount;
    private String message;
}