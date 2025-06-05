package br.edu.ibmec.cloud.ecommerce_cloud.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import br.edu.ibmec.cloud.ecommerce_cloud.model.SalesData;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Serviço responsável por enviar dados para o Power BI Streaming Dataset
 * Este serviço conecta diretamente com a API do Power BI para visualização em tempo real
 */
@Service
public class PowerBIService {
    
    private static final Logger logger = LoggerFactory.getLogger(PowerBIService.class);
    
    // URL do Power BI Push API (você vai colar aqui a URL que copiou)
    @Value("${powerbi.push.url:}")
    private String powerBIPushUrl;
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    public PowerBIService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Envia dados de vendas para o Power BI
     * @param salesData - dados da venda a serem enviados
     */
    public void sendToPowerBI(SalesData salesData) {
        try {
            // Verifica se a URL está configurada
            if (powerBIPushUrl == null || powerBIPushUrl.isEmpty()) {
                logger.warn("Power BI Push URL não configurada. Dados não serão enviados.");
                return;
            }
            
            logger.info("Enviando dados para Power BI - Order ID: {}", salesData.getOrderId());
            
            // Prepara os dados no formato que o Power BI espera
            Map<String, Object> powerBIData = new HashMap<>();
            powerBIData.put("orderId", salesData.getOrderId());
            powerBIData.put("userId", salesData.getUserId());
            powerBIData.put("saleDate", salesData.getSaleDate().toString());
            powerBIData.put("totalAmount", salesData.getTotalAmount());
            powerBIData.put("status", salesData.getStatus());
            powerBIData.put("totalItems", salesData.getTotalItems());
            powerBIData.put("customerCity", salesData.getCustomerCity());
            powerBIData.put("paymentMethod", salesData.getPaymentMethod());
            
            // Configura headers HTTP
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // Cria a requisição HTTP
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(powerBIData, headers);
            
            // Envia para o Power BI
            ResponseEntity<String> response = restTemplate.postForEntity(
                powerBIPushUrl, 
                request, 
                String.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK) {
                logger.info("Dados enviados com sucesso para Power BI - Order ID: {}", 
                           salesData.getOrderId());
            } else {
                logger.warn("Resposta inesperada do Power BI: {} - Order ID: {}", 
                           response.getStatusCode(), salesData.getOrderId());
            }
            
        } catch (Exception e) {
            logger.error("Erro ao enviar dados para Power BI - Order ID: {}, Erro: {}", 
                        salesData.getOrderId(), e.getMessage(), e);
        }
    }
    
    /**
     * Método para testar a conectividade com Power BI
     * @return true se conseguiu conectar, false caso contrário
     */
    public boolean testConnection() {
        try {
            if (powerBIPushUrl == null || powerBIPushUrl.isEmpty()) {
                return false;
            }
            
            // Testa com dados fictícios
            Map<String, Object> testData = new HashMap<>();
            testData.put("orderId", "TEST");
            testData.put("userId", 0);
            testData.put("saleDate", java.time.LocalDateTime.now().toString());
            testData.put("totalAmount", 0.0);
            testData.put("status", "TEST");
            testData.put("totalItems", 0);
            testData.put("customerCity", "TEST");
            testData.put("paymentMethod", "TEST");
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> request = new HttpEntity<>(testData, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(
                powerBIPushUrl, 
                request, 
                String.class
            );
            
            return response.getStatusCode() == HttpStatus.OK;
            
        } catch (Exception e) {
            logger.error("Erro ao testar conexão com Power BI: {}", e.getMessage());
            return false;
        }
    }
}