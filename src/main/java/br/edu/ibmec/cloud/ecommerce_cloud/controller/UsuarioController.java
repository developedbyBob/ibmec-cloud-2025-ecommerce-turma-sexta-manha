package br.edu.ibmec.cloud.ecommerce_cloud.controller;

import br.edu.ibmec.cloud.ecommerce_cloud.model.Usuario;
import br.edu.ibmec.cloud.ecommerce_cloud.repository.UsuarioRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/users")
public class UsuarioController {

    @Autowired
    private UsuarioRepository repository;

    @GetMapping
    public ResponseEntity<List<Usuario>> getUsers() {
        List<Usuario> response = repository.findAll();
        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    @GetMapping("{id}")
    public ResponseEntity<Usuario> getById(@PathVariable Integer id) {
        Optional<Usuario> response = this.repository.findById(id);
        if (response.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        return new ResponseEntity<>(response.get() ,HttpStatus.OK);
    }

    @PostMapping
    public ResponseEntity<Usuario> create(@RequestBody Usuario usuario){
        this.repository.save(usuario);
        return new ResponseEntity<>(usuario ,HttpStatus.CREATED);
    }

    @PutMapping("{id}")
    public ResponseEntity<Usuario> update(@PathVariable Integer id, @RequestBody Usuario usuario) {
        Optional<Usuario> optionalUsuario = this.repository.findById(id);
        
        if (optionalUsuario.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        
        Usuario existingUsuario = optionalUsuario.get();
        
        // Mantenha o ID original
        usuario.setId(id);
        
        // Mantenha os relacionamentos existentes se não forem fornecidos na requisição
        if (usuario.getCartoes() == null || usuario.getCartoes().isEmpty()) {
            usuario.setCartoes(existingUsuario.getCartoes());
        }
        
        if (usuario.getEnderecos() == null || usuario.getEnderecos().isEmpty()) {
            usuario.setEnderecos(existingUsuario.getEnderecos());
        }
        
        // Salva o usuário atualizado
        this.repository.save(usuario);
        
        return new ResponseEntity<>(usuario, HttpStatus.OK);
    }

    @DeleteMapping("{id}")
    public ResponseEntity<Usuario> delete(@PathVariable Integer id) {
        Optional<Usuario> response = this.repository.findById(id);
        if (response.isEmpty())
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);

        //Exclui o usuario da base
        this.repository.delete(response.get());

        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}