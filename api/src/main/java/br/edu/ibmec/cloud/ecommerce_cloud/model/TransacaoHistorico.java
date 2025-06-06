package br.edu.ibmec.cloud.ecommerce_cloud.model;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Entity(name="transacao_historico")
public class TransacaoHistorico {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column
    private Integer cartaoId;

    @Column
    private LocalDateTime dataTransacao;

    @Column
    private Double valor;

    @Column
    private String tipoTransacao; // "COMPRA", "ESTORNO", "CARGA"

    @Column
    private String descricao;

    @Column
    private String codigoAutorizacao;

    // Construtor vazio (obrigatório para JPA)
    public TransacaoHistorico() {}

    // Construtor para facilitar a criação
    public TransacaoHistorico(Integer cartaoId, Double valor, String tipoTransacao, String descricao, String codigoAutorizacao) {
        this.cartaoId = cartaoId;
        this.dataTransacao = LocalDateTime.now();
        this.valor = valor;
        this.tipoTransacao = tipoTransacao;
        this.descricao = descricao;
        this.codigoAutorizacao = codigoAutorizacao;
    }
}