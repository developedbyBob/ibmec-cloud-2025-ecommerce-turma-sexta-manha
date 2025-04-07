package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Endereco;
import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.EnderecoRepository;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.UsuarioRepository;

@RestController
@RequestMapping("/users/{id_user}/address")
public class EnderecoController {

    @Autowired
    private EnderecoRepository enderecoRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @PostMapping
    public ResponseEntity<Usuario> create(@PathVariable("id_user") int id_user, @RequestBody Endereco endereco) {
        //Verificando se o usuario existe na base
        Optional<Usuario> optionalUsuario = this.usuarioRepository.findById(id_user);

        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        //Cria o endereco  na base
        enderecoRepository.save(endereco);

        Usuario usuario = optionalUsuario.get();

        usuario.getEnderecos().add(endereco);
        usuarioRepository.save(usuario);

        return new ResponseEntity<>(usuario, HttpStatus.CREATED);

    }

}
