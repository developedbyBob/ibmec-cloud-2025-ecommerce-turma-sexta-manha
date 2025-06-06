from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from api.product_api import ProductAPI
from datetime import datetime

class ConsultarPedidosDialog(ComponentDialog):
    """
    Diálogo para consultar pedidos de um usuário
    """
    
    def __init__(self):
        super(ConsultarPedidosDialog, self).__init__("ConsultarPedidosDialog")

        # Adiciona os prompts necessários
        self.add_dialog(TextPrompt("userIdPrompt"))

        # Adiciona o fluxo principal
        self.add_dialog(
            WaterfallDialog(
                "consultarPedidoWaterfall",
                [
                    self.solicitar_user_id_step,
                    self.buscar_pedidos_step,
                ],
            )
        )

        # Define o diálogo inicial
        self.initial_dialog_id = "consultarPedidoWaterfall"

    async def solicitar_user_id_step(self, step_context: WaterfallStepContext):
        """
        Solicita o ID do usuário para buscar os pedidos
        """
        await step_context.context.send_activity(
            MessageFactory.text(
                "📦 **Consulta de Pedidos**\n\n"
                "Para consultar seus pedidos, preciso do seu ID de usuário.\n\n"
                "💡 **Em um sistema real, você já estaria logado automaticamente.**"
            )
        )
        
        prompt_message = MessageFactory.text("👤 Digite seu ID de usuário (número):")

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite um número válido para o ID do usuário."),
        )
        
        return await step_context.prompt("userIdPrompt", prompt_options)

    async def buscar_pedidos_step(self, step_context: WaterfallStepContext):
        """
        Busca e exibe os pedidos do usuário
        """
        user_id_input = step_context.result.strip()
        
        # Valida se é um número
        if not user_id_input.isdigit():
            await step_context.context.send_activity(
                MessageFactory.text("❌ ID do usuário deve ser um número válido.")
            )
            return await step_context.end_dialog()
        
        user_id = int(user_id_input)
        
        # Testa conexão com a API
        produto_api = ProductAPI()
        if not produto_api.test_connection():
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Erro de Conexão**\n\n"
                    "Não foi possível conectar com o sistema de pedidos. "
                    "Tente novamente em alguns instantes."
                )
            )
            return await step_context.end_dialog()

        # Busca os pedidos
        await step_context.context.send_activity(
            MessageFactory.text(f"🔄 Buscando pedidos do usuário {user_id}...")
        )

        try:
            pedidos = produto_api.get_user_orders(user_id)
            
            if pedidos is None:
                await step_context.context.send_activity(
                    MessageFactory.text(
                        "❌ **Erro na Consulta**\n\n"
                        "Ocorreu um erro ao buscar seus pedidos. Tente novamente."
                    )
                )
                return await step_context.end_dialog()

            elif len(pedidos) == 0:
                await step_context.context.send_activity(
                    MessageFactory.text(
                        "📭 **Nenhum pedido encontrado**\n\n"
                        f"O usuário {user_id} ainda não possui pedidos realizados.\n\n"
                        "🛍️ **Que tal fazer sua primeira compra?**\n"
                        "Use a opção 'Consultar Produtos' no menu principal!"
                    )
                )
                return await step_context.end_dialog()

            else:
                # Exibe os pedidos encontrados
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"✅ **{len(pedidos)} pedido(s) encontrado(s)!**\n\n"
                        f"📋 Aqui estão seus pedidos:"
                    )
                )
                
                # Exibe cada pedido
                await self.exibir_pedidos(pedidos, step_context)

                await step_context.context.send_activity(
                    MessageFactory.text(
                        "✅ **Consulta finalizada!**\n\n"
                        "💬 Digite qualquer mensagem para voltar ao menu principal."
                    )
                )

        except Exception as e:
            print(f"[BOT] Erro inesperado na consulta de pedidos: {e}")
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Erro Inesperado**\n\n"
                    "Ocorreu um erro inesperado. Tente novamente."
                )
            )

        return await step_context.end_dialog()

    async def exibir_pedidos(self, pedidos, step_context: WaterfallStepContext):
        """
        Exibe os pedidos de forma organizada
        """
        for i, pedido in enumerate(pedidos, 1):
            try:
                # Extrai informações do pedido
                order_id = pedido.get("id", "N/A")
                order_date = pedido.get("orderDate", "")
                status = pedido.get("status", "UNKNOWN")
                total_amount = pedido.get("totalAmount", 0.0)
                items = pedido.get("items", [])
                shipping_address = pedido.get("shippingAddress", "Não informado")
                transaction_id = pedido.get("transactionId", "N/A")

                # Formata a data
                data_formatada = self.formatar_data(order_date)
                
                # Formata o valor
                valor_formatado = f"R$ {total_amount:.2f}".replace(".", ",")
                
                # Formata o status
                status_emoji = self.get_status_emoji(status)
                status_texto = self.get_status_texto(status)
                
                # Monta a lista de itens
                itens_texto = ""
                for item in items:
                    product_name = item.get("productName", "Produto")
                    quantity = item.get("quantity", 1)
                    unit_price = item.get("unitPrice", 0.0)
                    subtotal = item.get("subTotal", 0.0)
                    
                    itens_texto += (
                        f"   • **{product_name}**\n"
                        f"     Qtd: {quantity} | Preço: R$ {unit_price:.2f} | "
                        f"Subtotal: R$ {subtotal:.2f}\n"
                    )

                # Monta a mensagem do pedido
                mensagem_pedido = (
                    f"🛍️ **PEDIDO #{i}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎫 **ID:** {order_id}\n"
                    f"📅 **Data:** {data_formatada}\n"
                    f"{status_emoji} **Status:** {status_texto}\n"
                    f"💰 **Total:** {valor_formatado}\n"
                    f"🏠 **Entrega:** {shipping_address}\n"
                    f"🔑 **Transação:** {transaction_id[:8]}...\n\n"
                    f"📦 **Itens:**\n{itens_texto}\n"
                )

                await step_context.context.send_activity(
                    MessageFactory.text(mensagem_pedido)
                )
                
            except Exception as e:
                print(f"[BOT] Erro ao exibir pedido: {e}")
                # Se der erro, exibe versão simplificada
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"📦 **Pedido #{i}:** {pedido.get('id', 'N/A')} - "
                        f"R$ {pedido.get('totalAmount', 0.0):.2f}"
                    )
                )

    def formatar_data(self, data_str: str) -> str:
        """
        Formata a data para exibição amigável
        """
        try:
            # Tenta parsear a data ISO
            if 'T' in data_str:
                data = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
            else:
                data = datetime.fromisoformat(data_str)
            
            return data.strftime("%d/%m/%Y às %H:%M")
        except:
            return data_str

    def get_status_emoji(self, status: str) -> str:
        """
        Retorna emoji baseado no status do pedido
        """
        status_emojis = {
            "PENDING": "⏳",
            "PAID": "✅",
            "SHIPPED": "🚚",
            "DELIVERED": "📦",
            "CANCELLED": "❌"
        }
        return status_emojis.get(status.upper(), "❓")

    def get_status_texto(self, status: str) -> str:
        """
        Retorna texto amigável para o status
        """
        status_textos = {
            "PENDING": "Pendente",
            "PAID": "Pago",
            "SHIPPED": "Enviado",
            "DELIVERED": "Entregue",
            "CANCELLED": "Cancelado"
        }
        return status_textos.get(status.upper(), status)