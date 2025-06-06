package br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos;

import java.util.List;

import org.springframework.stereotype.Repository;

import com.azure.spring.data.cosmos.repository.CosmosRepository;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Order;

@Repository
public interface OrderRepository extends CosmosRepository<Order, String> {
    List<Order> findByUserId(Integer userId);
}