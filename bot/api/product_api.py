import requests
import json
from config import DefaultConfig

class ProductAPI:
    """
    Cliente para integração com a API do E-commerce
    Responsável por fazer chamadas HTTP para sua API no Azure
    """
    
    def __init__(self):
        self.config = DefaultConfig()
        self.base_url = self.config.URL_PREFIX
        
        # Headers padrão para as requisições
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_products(self):
        """
        Busca todos os produtos disponíveis
        Returns: Lista de produtos ou None se der erro
        """
        try:
            url = f"{self.base_url}/products"
            print(f"[API] Buscando produtos em: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                products = response.json()
                print(f"[API] ✅ Encontrados {len(products)} produtos")
                return products
            else:
                print(f"[API] ❌ Erro ao buscar produtos: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[API] ❌ Timeout ao buscar produtos")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[API] ❌ Erro de conexão ao buscar produtos: {e}")
            return None

    def search_product(self, product_name):
        """
        Busca produtos por nome (usa o novo endpoint que criamos)
        Args: product_name (str) - Nome do produto para buscar
        Returns: Lista de produtos encontrados ou None se der erro
        """
        try:
            url = f"{self.base_url}/products/search"
            params = {"productName": product_name}
            
            print(f"[API] Buscando produtos com nome '{product_name}' em: {url}")
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                products = response.json()
                print(f"[API] ✅ Encontrados {len(products)} produtos para '{product_name}'")
                return products
            elif response.status_code == 404:
                print(f"[API] ℹ️ Nenhum produto encontrado para '{product_name}'")
                return []
            else:
                print(f"[API] ❌ Erro ao buscar produtos: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[API] ❌ Timeout ao buscar produtos para '{product_name}'")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[API] ❌ Erro de conexão ao buscar produtos: {e}")
            return None

    def get_user_orders(self, user_id):
        """
        Busca os pedidos de um usuário específico
        Args: user_id (int) - ID do usuário
        Returns: Lista de pedidos ou None se der erro
        """
        try:
            url = f"{self.base_url}/orders/user/{user_id}"
            print(f"[API] Buscando pedidos do usuário {user_id} em: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                orders = response.json()
                print(f"[API] ✅ Encontrados {len(orders)} pedidos para usuário {user_id}")
                return orders
            elif response.status_code == 404:
                print(f"[API] ℹ️ Usuário {user_id} não encontrado ou sem pedidos")
                return []
            else:
                print(f"[API] ❌ Erro ao buscar pedidos: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[API] ❌ Timeout ao buscar pedidos do usuário {user_id}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[API] ❌ Erro de conexão ao buscar pedidos: {e}")
            return None

    def get_card_statement(self, user_id, card_id):
        """
        Busca o extrato de um cartão específico (novo endpoint que criamos)
        Args: 
            user_id (int) - ID do usuário
            card_id (int) - ID do cartão
        Returns: Lista de transações ou None se der erro
        """
        try:
            url = f"{self.base_url}/users/{user_id}/credit-card/{card_id}/statement"
            print(f"[API] Buscando extrato do cartão {card_id} para usuário {user_id}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"[API] ✅ Encontradas {len(transactions)} transações")
                return transactions
            elif response.status_code == 404:
                print(f"[API] ℹ️ Usuário ou cartão não encontrado")
                return []
            elif response.status_code == 403:
                print(f"[API] ❌ Cartão não pertence ao usuário")
                return None
            else:
                print(f"[API] ❌ Erro ao buscar extrato: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[API] ❌ Timeout ao buscar extrato")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[API] ❌ Erro de conexão ao buscar extrato: {e}")
            return None

    def create_order(self, order_data):
        """
        Cria um novo pedido (compra)
        Args: order_data (dict) - Dados do pedido no formato esperado pela API
        Returns: Dados do pedido criado ou None se der erro
        """
        try:
            url = f"{self.base_url}/orders"
            print(f"[API] Criando pedido em: {url}")
            
            response = requests.post(
                url, 
                data=json.dumps(order_data), 
                headers=self.headers, 
                timeout=15
            )
            
            if response.status_code == 201:
                order_response = response.json()
                print(f"[API] ✅ Pedido criado com sucesso: {order_response.get('orderId', 'N/A')}")
                return order_response
            else:
                print(f"[API] ❌ Erro ao criar pedido: {response.status_code}")
                if response.text:
                    print(f"[API] Detalhes do erro: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[API] ❌ Timeout ao criar pedido")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[API] ❌ Erro de conexão ao criar pedido: {e}")
            return None

    def test_connection(self):
        """
        Testa se a API está respondendo
        Returns: True se conectou, False caso contrário
        """
        try:
            url = f"{self.base_url}/products"
            print(f"[API] Testando conexão com: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                print("[API] ✅ Conexão com a API funcionando!")
                return True
            else:
                print(f"[API] ⚠️ API respondeu mas com status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[API] ❌ Falha na conexão com a API: {e}")
            return False