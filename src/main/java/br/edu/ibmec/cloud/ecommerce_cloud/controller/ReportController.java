package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Order;
import br.edu.ibmec.cloud.ecommerce_cloud.model.OrderItem;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.cosmos.OrderRepository;

@RestController
@RequestMapping("/relatorio-vendas")
public class ReportController {

    @Autowired
    private OrderRepository orderRepository;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getSalesReport(
            @RequestParam(required = false) LocalDateTime startDate,
            @RequestParam(required = false) LocalDateTime endDate) {
        
        // Se as datas não forem fornecidas, use um período padrão
        final LocalDateTime effectiveStartDate = (startDate != null) ? 
                startDate : LocalDateTime.now().minusDays(30);
        
        final LocalDateTime effectiveEndDate = (endDate != null) ? 
                endDate : LocalDateTime.now();
        
        // Buscar todos os pedidos
        List<Order> allOrders = new ArrayList<>();
        orderRepository.findAll().forEach(allOrders::add);
        
        // Filtrar pedidos pelo período
        List<Order> filteredOrders = allOrders.stream()
                .filter(order -> order.getOrderDate().isAfter(effectiveStartDate) && 
                                order.getOrderDate().isBefore(effectiveEndDate))
                .toList();
        
        // Calcular estatísticas
        double totalRevenue = 0;
        int totalOrders = filteredOrders.size();
        Map<String, Integer> productsSold = new HashMap<>();
        
        for (Order order : filteredOrders) {
            totalRevenue += order.getTotalAmount();
            
            for (OrderItem item : order.getItems()) {
                String productName = item.getProductName();
                int quantity = item.getQuantity();
                
                productsSold.put(
                    productName, 
                    productsSold.getOrDefault(productName, 0) + quantity
                );
            }
        }
        
        // Organizar resultado do relatório
        Map<String, Object> report = new HashMap<>();
        report.put("startDate", effectiveStartDate);
        report.put("endDate", effectiveEndDate);
        report.put("totalRevenue", totalRevenue);
        report.put("totalOrders", totalOrders);
        report.put("averageOrderValue", totalOrders > 0 ? totalRevenue / totalOrders : 0);
        report.put("productsSold", productsSold);
        
        return new ResponseEntity<>(report, HttpStatus.OK);
    }
}