package br.edu.ibmec.cloud.ecommerce_cloud.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import br.edu.ibmec.cloud.ecommerce_cloud.model.SalesData;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Serviço PowerBI melhorado com melhor tratamento de erros e formato de dados
 */
@Service
public class PowerBIService {
    
    private static final Logger logger = LoggerFactory.getLogger(PowerBIService.class);
    
    @Value("${powerbi.push.url:}")
    private String powerBIPushUrl;
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    public PowerBIService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
    }
    
    /**
     * Envia dados para Power BI com formato melhorado
     */
    public void sendToPowerBI(SalesData salesData) {
        try {
            if (powerBIPushUrl == null || powerBIPushUrl.isEmpty()) {
                logger.warn("Power BI Push URL não configurada. Dados não serão enviados.");
                return;
            }
            
            logger.info("Enviando dados para Power BI - Order ID: {}", salesData.getOrderId());
            logger.debug("Power BI URL: {}", powerBIPushUrl);
            
            // Prepara os dados no formato que o Power BI espera
            Map<String, Object> powerBIData = new HashMap<>();
            powerBIData.put("orderId", salesData.getOrderId());
            powerBIData.put("userId", salesData.getUserId());
            
            // Converte data para string no formato ISO
            String dateString = salesData.getSaleDate().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
            powerBIData.put("saleDate", dateString);
            
            powerBIData.put("totalAmount", salesData.getTotalAmount());
            powerBIData.put("status", salesData.getStatus());
            powerBIData.put("totalItems", salesData.getTotalItems());
            powerBIData.put("customerCity", salesData.getCustomerCity());
            powerBIData.put("paymentMethod", salesData.getPaymentMethod());
            
            // Cria array com os dados (Power BI espera array, não objeto único)
            List<Map<String, Object>> dataArray = new ArrayList<>();
            dataArray.add(powerBIData);
            
            // Configura headers HTTP
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Accept", "application/json");
            
            // Log dos dados para debug
            String jsonData = objectMapper.writeValueAsString(dataArray);
            logger.debug("Dados JSON para Power BI: {}", jsonData);
            
            // Cria a requisição HTTP
            HttpEntity<List<Map<String, Object>>> request = new HttpEntity<>(dataArray, headers);
            
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
                logger.debug("Resposta Body: {}", response.getBody());
            }
            
        } catch (Exception e) {
            logger.error("Erro ao enviar dados para Power BI - Order ID: {}, Erro: {}", 
                        salesData.getOrderId(), e.getMessage());
            
            // Log detalhado para debug
            if (e instanceof org.springframework.web.client.HttpClientErrorException) {
                org.springframework.web.client.HttpClientErrorException httpError = 
                    (org.springframework.web.client.HttpClientErrorException) e;
                logger.error("Status Code: {}", httpError.getStatusCode());
                logger.error("Response Body: {}", httpError.getResponseBodyAsString());
            }
        }
    }
    
    /**
     * Teste de conectividade melhorado
     */
    public boolean testConnection() {
        try {
            if (powerBIPushUrl == null || powerBIPushUrl.isEmpty()) {
                logger.warn("Power BI URL não configurada para teste");
                return false;
            }
            
            // Dados de teste simples
            Map<String, Object> testData = new HashMap<>();
            testData.put("orderId", "TEST-" + System.currentTimeMillis());
            testData.put("userId", 999);
            testData.put("saleDate", java.time.LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            testData.put("totalAmount", 1.0);
            testData.put("status", "TEST");
            testData.put("totalItems", 1);
            testData.put("customerCity", "Test City");
            testData.put("paymentMethod", "Test");
            
            List<Map<String, Object>> dataArray = new ArrayList<>();
            dataArray.add(testData);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<List<Map<String, Object>>> request = new HttpEntity<>(dataArray, headers);
            
            ResponseEntity<String> response = restTemplate.postForEntity(
                powerBIPushUrl, 
                request, 
                String.class
            );
            
            logger.info("Teste de conexão Power BI: {}", response.getStatusCode());
            return response.getStatusCode() == HttpStatus.OK;
            
        } catch (Exception e) {
            logger.error("Erro no teste de conexão Power BI: {}", e.getMessage());
            return false;
        }
    }
}