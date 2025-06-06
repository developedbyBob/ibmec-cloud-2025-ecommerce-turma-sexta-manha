package br.edu.ibmec.cloud.ecommerce_cloud.repository;

import br.edu.ibmec.cloud.ecommerce_cloud.model.TransacaoHistorico;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TransacaoHistoricoRepository extends JpaRepository<TransacaoHistorico, Integer> {
    
    // Busca todas as transações de um cartão específico, ordenadas pela data (mais recente primeiro)
    List<TransacaoHistorico> findByCartaoIdOrderByDataTransacaoDesc(Integer cartaoId);
}