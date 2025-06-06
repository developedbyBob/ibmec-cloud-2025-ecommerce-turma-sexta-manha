package br.edu.ibmec.cloud.ecommerce_cloud.request;

import java.util.List;

import br.edu.ibmec.cloud.ecommerce_cloud.model.CartItem;
import lombok.Data;

@Data
public class CartRequest {
    private Integer userId;
    private List<CartItem> items;
    private String cartaoId;
}