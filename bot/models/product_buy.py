class ProductBuyModel:
    """
    Modelo que representa os dados de uma compra de produto
    Usado para coletar e organizar as informações do usuário
    """
    
    def __init__(self, product_id: str = None, numero_cartao: str = None, 
                 data_expiracao: str = None, cvv: str = None):
        self.product_id = product_id
        self.numero_cartao = numero_cartao
        self.data_expiracao = data_expiracao
        self.cvv = cvv
        self.user_id = None  # Será preenchido durante o processo
        self.produto_info = None  # Informações do produto (nome, preço, etc.)

    def __str__(self):
        return (f"ProductBuyModel("
                f"product_id={self.product_id}, "
                f"numero_cartao=***{self.numero_cartao[-4:] if self.numero_cartao else 'N/A'}, "
                f"cvv=***, "
                f"user_id={self.user_id})")

    def is_complete(self):
        """
        Verifica se todos os dados necessários foram coletados
        """
        return all([
            self.product_id,
            self.numero_cartao,
            self.data_expiracao,
            self.cvv,
            self.user_id
        ])

    def to_api_format(self):
        """
        Converte os dados para o formato esperado pela API de pedidos
        Returns: dict no formato da API
        """
        if not self.is_complete():
            raise ValueError("Dados incompletos para criar pedido")
        
        # Formato esperado pela sua API
        return {
            "userId": self.user_id,
            "items": [
                {
                    "productId": self.product_id,
                    "productName": self.produto_info.get("productName", "Produto") if self.produto_info else "Produto",
                    "price": self.produto_info.get("price", 0.0) if self.produto_info else 0.0,
                    "quantity": 1  # Por enquanto sempre 1
                }
            ],
            "cartaoId": "1"  # Por enquanto fixo, depois podemos melhorar
        }