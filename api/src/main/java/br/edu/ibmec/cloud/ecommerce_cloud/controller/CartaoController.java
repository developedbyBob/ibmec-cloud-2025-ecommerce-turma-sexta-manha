package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Cartao;
import br.edu.ibmec.cloud.ecommerce_cloud.model.TransacaoHistorico;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.CartaoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.TransacaoHistoricoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.UsuarioRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.request.TransacaoRequest;
import br.edu.ibmec.cloud.ecommerce_cloud.request.TransacaoResponse;

@RestController
@RequestMapping("users/{id_user}/credit-card")
public class CartaoController {

    @Autowired
    private CartaoRepository cartaoRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    // NOVA INJEÇÃO - Repository para histórico de transações
    @Autowired
    private TransacaoHistoricoRepository transacaoHistoricoRepository;

    @PostMapping
    public ResponseEntity<Usuario> create(@PathVariable("id_user") int id_user, @RequestBody Cartao cartao) {
        //Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        //Cria o cartao de credito na base
        cartaoRepository.save(cartao);

        // NOVO - Registra a criação do cartão no histórico
        TransacaoHistorico historico = new TransacaoHistorico(
            cartao.getId(),
            cartao.getSaldo(),
            "CARGA",
            "Criação do cartão com saldo inicial",
            "INICIAL-" + UUID.randomUUID().toString().substring(0, 8)
        );
        transacaoHistoricoRepository.save(historico);

        //Associa o cartao de credito ao usuario
        Usuario usuario = optionalUsuario.get();
        usuario.getCartoes().add(cartao);
        usuarioRepository.save(usuario);

        return new ResponseEntity<>(usuario, HttpStatus.CREATED);
    }

    @PostMapping("/authorize")
    public ResponseEntity<TransacaoResponse> authorize(@PathVariable("id_user") int id_user,
                                                       @RequestBody TransacaoRequest request) {
        //Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        Usuario user = optionalUsuario.get();
        Cartao cartaoTransacao = null;

        for (Cartao cartao: user.getCartoes()) {
            if (cartao.getNumero().equals(request.getNumero()) && cartao.getCvv().equals(request.getCvv())) {
                cartaoTransacao = cartao;
                break;
            }
        }

        //Não achei o cartao associado para o usuario
        if (cartaoTransacao == null) {
            TransacaoResponse response = new TransacaoResponse();
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Cartão não encontrado para o usuario");
            return new ResponseEntity<>(response, HttpStatus.NOT_FOUND);
        }

        //Verifica se o cartao não está expirado
        if (cartaoTransacao.getDtExpiracao().isBefore(LocalDateTime.now())) {
            TransacaoResponse response = new TransacaoResponse();
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Cartão Expirado");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }

        //Verifica se tem dinheiro no cartao para realizar a compra
        if (cartaoTransacao.getSaldo() < request.getValor()) {
            TransacaoResponse response = new TransacaoResponse();
            response.setStatus("NOT_AUTHORIZED");
            response.setDtTransacao(LocalDateTime.now());
            response.setMessage("Sem saldo para realizar a compra");
            return new ResponseEntity<>(response, HttpStatus.BAD_REQUEST);
        }

        //Pega o saldo do cartão
        Double saldo = cartaoTransacao.getSaldo();

        //Substrai o saldo com o valor da compra
        saldo = saldo - request.getValor();

        //Atualiza o saldo do cartao
        cartaoTransacao.setSaldo(saldo);

        //Grava o novo saldo na base de dados
        this.cartaoRepository.save(cartaoTransacao);

        // NOVO - Registra a transação de compra no histórico
        String codigoAutorizacao = UUID.randomUUID().toString();
        TransacaoHistorico historico = new TransacaoHistorico(
            cartaoTransacao.getId(),
            request.getValor(),
            "COMPRA",
            "Compra autorizada - Valor: R$ " + request.getValor(),
            codigoAutorizacao
        );
        transacaoHistoricoRepository.save(historico);

        //Compra Autorizada
        TransacaoResponse response = new TransacaoResponse();
        response.setStatus("AUTHORIZED");
        response.setDtTransacao(LocalDateTime.now());
        response.setMessage("Compra autorizada");
        response.setCodigoAutorizacao(UUID.fromString(codigoAutorizacao));

        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    // ===== NOVO ENDPOINT - EXTRATO DO CARTÃO =====
    @GetMapping("/{card_id}/statement")
    public ResponseEntity<List<TransacaoHistorico>> getExtrato(
            @PathVariable("id_user") int id_user,
            @PathVariable("card_id") int card_id) {
        
        //Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);
        if (optionalUsuario.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        //Verificando se o cartão existe e pertence ao usuário
        Optional<Cartao> optionalCartao = this.cartaoRepository.findById(card_id);
        if (optionalCartao.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }

        Cartao cartao = optionalCartao.get();
        Usuario usuario = optionalUsuario.get();
        
        // Verifica se o cartão pertence ao usuário
        boolean cartaoPerenceUsuario = usuario.getCartoes().stream()
                .anyMatch(c -> c.getId() == card_id);
        
        if (!cartaoPerenceUsuario) {
            return new ResponseEntity<>(HttpStatus.FORBIDDEN);
        }

        // Busca o histórico de transações do cartão
        List<TransacaoHistorico> extrato = transacaoHistoricoRepository
                .findByCartaoIdOrderByDataTransacaoDesc(card_id);

        return new ResponseEntity<>(extrato, HttpStatus.OK);
    }
    // ==============================================
}