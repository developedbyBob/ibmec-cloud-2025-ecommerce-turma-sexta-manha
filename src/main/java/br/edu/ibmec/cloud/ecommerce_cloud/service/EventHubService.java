package br.edu.ibmec.cloud.ecommerce_cloud.service;

import com.azure.messaging.eventhubs.EventData;
import com.azure.messaging.eventhubs.EventHubClientBuilder;
import com.azure.messaging.eventhubs.EventHubProducerClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import br.edu.ibmec.cloud.ecommerce_cloud.model.SalesData;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

/**
 * Serviço responsável por enviar dados de vendas para o Azure Event Hub
 * Este serviço é usado para implementar o pipeline de Big Data
 */
@Service
public class EventHubService {
    
    private static final Logger logger = LoggerFactory.getLogger(EventHubService.class);
    
    // Injeta as configurações do application.properties
    @Value("${azure.eventhub.connection-string}")
    private String connectionString;
    
    @Value("${azure.eventhub.name}")
    private String eventHubName;
    
    // Cliente para enviar eventos
    private EventHubProducerClient producer;
    
    // Para converter objetos em JSON
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    /**
     * Inicializa o cliente do Event Hub após a criação do bean
     * @PostConstruct é executado automaticamente pelo Spring
     */
    @PostConstruct
    public void initialize() {
        try {
            logger.info("Inicializando conexão com Event Hub: {}", eventHubName);
            
            // Cria o cliente produtor usando a connection string
            this.producer = new EventHubClientBuilder()
                    .connectionString(connectionString, eventHubName)
                    .buildProducerClient();
            
            logger.info("Event Hub Service inicializado com sucesso!");
            
        } catch (Exception e) {
            logger.error("Erro ao inicializar Event Hub Service: {}", e.getMessage(), e);
            // Em ambiente de desenvolvimento, não queremos que a aplicação pare
            // por causa do Event Hub, então só logamos o erro
        }
    }
    
    /**
     * Envia dados de vendas para o Event Hub
     * @param salesData - dados da venda a serem enviados
     */
    public void sendSalesData(SalesData salesData) {
        try {
            // Verifica se o producer foi inicializado
            if (producer == null) {
                logger.warn("Event Hub producer não está inicializado. Dados não serão enviados.");
                return;
            }
            
            logger.info("Enviando dados de venda para Event Hub - Order ID: {}", salesData.getOrderId());
            
            // Converte o objeto SalesData para JSON
            String salesDataJson = objectMapper.writeValueAsString(salesData);
            
            // Cria o evento
            EventData eventData = new EventData(salesDataJson);
            
            // Adiciona propriedades ao evento (metadata)
            eventData.getProperties().put("eventType", "sale");
            eventData.getProperties().put("orderId", salesData.getOrderId());
            eventData.getProperties().put("userId", salesData.getUserId().toString());
            eventData.getProperties().put("totalAmount", salesData.getTotalAmount().toString());
            
            // Envia o evento para o Event Hub
            producer.send(java.util.Arrays.asList(eventData));
            
            logger.info("Dados de venda enviados com sucesso para Event Hub - Order ID: {}", 
                       salesData.getOrderId());
            
        } catch (Exception e) {
            logger.error("Erro ao enviar dados para Event Hub - Order ID: {}, Erro: {}", 
                        salesData.getOrderId(), e.getMessage(), e);
            
            // Em ambiente de produção, você pode querer:
            // 1. Tentar reenviar
            // 2. Armazenar em uma fila de retry
            // 3. Enviar alerta para o time
            // Por enquanto, só logamos o erro
        }
    }
    
    /**
     * Fecha a conexão com o Event Hub quando o serviço é destruído
     * @PreDestroy é executado automaticamente pelo Spring
     */
    @PreDestroy
    public void cleanup() {
        try {
            if (producer != null) {
                logger.info("Fechando conexão com Event Hub");
                producer.close();
                logger.info("Conexão com Event Hub fechada com sucesso");
            }
        } catch (Exception e) {
            logger.error("Erro ao fechar conexão com Event Hub: {}", e.getMessage(), e);
        }
    }
    
    /**
     * Método para testar a conectividade (útil para debug)
     * @return true se a conexão está ok, false caso contrário
     */
    public boolean isHealthy() {
        return producer != null;
    }
}