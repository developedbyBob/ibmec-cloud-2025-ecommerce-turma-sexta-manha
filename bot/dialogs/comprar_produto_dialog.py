from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory, UserState
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from models.product_buy import ProductBuyModel
from api.product_api import ProductAPI
import re
from datetime import datetime

class ComprarProdutoDialog(ComponentDialog):
    """
    Diálogo para realizar a compra de um produto
    Coleta dados do cartão e processa a compra
    """
    
    def __init__(self, user_state: UserState):
        super(ComprarProdutoDialog, self).__init__("ComprarProdutoDialog")

        # Adiciona os prompts necessários
        self.add_dialog(TextPrompt("userIdPrompt"))
        self.add_dialog(TextPrompt("numeroCartaoCreditoPrompt"))
        self.add_dialog(TextPrompt("dataExpiracaoPrompt"))
        self.add_dialog(TextPrompt("cvvPrompt"))
        self.add_dialog(TextPrompt("confirmacaoPrompt"))

        # Adiciona o fluxo principal
        self.add_dialog(
            WaterfallDialog(
                "comprarProdutoWaterfall",
                [
                    self.solicitar_user_id_step,
                    self.numero_cartao_step,
                    self.data_expiracao_step,
                    self.cvv_step,
                    self.confirmacao_step,
                    self.processar_compra_step
                ],
            )
        )

        # Define o diálogo inicial
        self.initial_dialog_id = "comprarProdutoWaterfall"

    async def solicitar_user_id_step(self, step_context: WaterfallStepContext):
        """
        Solicita o ID do usuário (simplificado para demonstração)
        """
        # Armazena informações do produto
        product_info = step_context.options
        step_context.values["product_info"] = product_info
        
        product_name = product_info.get("productName", "produto")
        
        await step_context.context.send_activity(
            MessageFactory.text(
                f"🛒 **Comprando: {product_name}**\n\n"
                f"Para processar sua compra, precisamos de algumas informações.\n\n"
                f"⚠️ **Importante:** Em um sistema real, você já estaria logado. "
                f"Para demonstração, por favor informe seu ID de usuário."
            )
        )
        
        prompt_message = MessageFactory.text("👤 **ID do Usuário:** Digite seu ID de usuário (número):")

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite um número válido para o ID do usuário."),
        )
        
        return await step_context.prompt("userIdPrompt", prompt_options)

    async def numero_cartao_step(self, step_context: WaterfallStepContext):
        """
        Solicita o número do cartão de crédito
        """
        user_id_input = step_context.result.strip()
        
        # Valida se é um número
        if not user_id_input.isdigit():
            await step_context.context.send_activity(
                MessageFactory.text("❌ ID do usuário deve ser um número válido.")
            )
            return await step_context.end_dialog()
        
        # Armazena o user_id
        step_context.values["user_id"] = int(user_id_input)
        
        prompt_message = MessageFactory.text(
            "💳 **Cartão de Crédito**\n\n"
            "Digite o número do seu cartão de crédito:\n\n"
            "💡 **Formato:** 1234567890123456 (16 dígitos)"
        )

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite um número de cartão válido (16 dígitos)."),
        )
        
        return await step_context.prompt("numeroCartaoCreditoPrompt", prompt_options)

    async def data_expiracao_step(self, step_context: WaterfallStepContext):
        """
        Solicita a data de expiração do cartão
        """
        numero_cartao = step_context.result.strip().replace(" ", "")
        
        # Validação básica do número do cartão
        if not self.validar_numero_cartao(numero_cartao):
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Número do cartão inválido**\n\n"
                    "O número deve ter exatamente 16 dígitos."
                )
            )
            return await step_context.end_dialog()
        
        # Armazena o número do cartão
        step_context.values["numero_cartao"] = numero_cartao
        
        prompt_message = MessageFactory.text(
            "📅 **Data de Expiração**\n\n"
            "Digite a data de expiração do cartão:\n\n"
            "💡 **Formato:** MM/AA (exemplo: 12/26)"
        )

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite uma data válida no formato MM/AA."),
        )

        return await step_context.prompt("dataExpiracaoPrompt", prompt_options)

    async def cvv_step(self, step_context: WaterfallStepContext):
        """
        Solicita o código CVV do cartão
        """
        data_expiracao = step_context.result.strip()
        
        # Validação da data de expiração
        if not self.validar_data_expiracao(data_expiracao):
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Data de expiração inválida**\n\n"
                    "Use o formato MM/AA (exemplo: 12/26) e certifique-se que o cartão não está expirado."
                )
            )
            return await step_context.end_dialog()
        
        # Armazena a data de expiração
        step_context.values["data_expiracao"] = data_expiracao
        
        prompt_message = MessageFactory.text(
            "🔒 **Código de Segurança**\n\n"
            "Digite o código CVV do cartão:\n\n"
            "💡 **CVV:** 3 dígitos no verso do cartão"
        )

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite um CVV válido (3 dígitos)."),
        )

        return await step_context.prompt("cvvPrompt", prompt_options)

    async def confirmacao_step(self, step_context: WaterfallStepContext):
        """
        Mostra um resumo da compra e pede confirmação
        """
        cvv = step_context.result.strip()
        
        # Validação do CVV
        if not self.validar_cvv(cvv):
            await step_context.context.send_activity(
                MessageFactory.text("❌ **CVV inválido**\n\nO CVV deve ter exatamente 3 dígitos.")
            )
            return await step_context.end_dialog()
        
        # Armazena o CVV
        step_context.values["cvv"] = cvv
        
        # Monta o resumo da compra
        product_info = step_context.values["product_info"]
        product_name = product_info.get("productName", "Produto")
        price = product_info.get("price", 0.0)
        numero_cartao = step_context.values["numero_cartao"]
        
        # Formata o preço
        price_formatted = f"R$ {price:.2f}".replace(".", ",")
        
        # Mascara o número do cartão
        cartao_mascarado = f"****-****-****-{numero_cartao[-4:]}"
        
        resumo = (
            f"🛒 **RESUMO DA COMPRA**\n\n"
            f"📦 **Produto:** {product_name}\n"
            f"💰 **Valor:** {price_formatted}\n"
            f"💳 **Cartão:** {cartao_mascarado}\n\n"
            f"❓ **Confirma a compra?**\n\n"
            f"Digite **'sim'** para confirmar ou **'não'** para cancelar."
        )
        
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(resumo),
            retry_prompt=MessageFactory.text("❌ Por favor, digite 'sim' para confirmar ou 'não' para cancelar."),
        )

        return await step_context.prompt("confirmacaoPrompt", prompt_options)

    async def processar_compra_step(self, step_context: WaterfallStepContext):
        """
        Processa a compra na API
        """
        confirmacao = step_context.result.strip().lower()
        
        if confirmacao not in ['sim', 's', 'yes', 'y']:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Compra Cancelada**\n\n"
                    "Sua compra foi cancelada com sucesso.\n\n"
                    "💬 Digite qualquer mensagem para voltar ao menu principal."
                )
            )
            return await step_context.end_dialog()
        
        # Monta o objeto de compra
        product_info = step_context.values["product_info"]
        
        product_buy = ProductBuyModel()
        product_buy.product_id = product_info.get("productId")
        product_buy.numero_cartao = step_context.values["numero_cartao"]
        product_buy.data_expiracao = step_context.values["data_expiracao"]
        product_buy.cvv = step_context.values["cvv"]
        product_buy.user_id = step_context.values["user_id"]
        product_buy.produto_info = product_info
        
        await step_context.context.send_activity(
            MessageFactory.text("🔄 **Processando compra...**\n\nPor favor, aguarde...")
        )
        
        try:
            # Chama a API para criar o pedido
            produto_api = ProductAPI()
            order_data = product_buy.to_api_format()
            
            print(f"[BOT] Enviando dados para API: {order_data}")
            
            result = produto_api.create_order(order_data)
            
            if result:
                # Compra realizada com sucesso
                order_id = result.get("orderId", "N/A")
                total_amount = result.get("totalAmount", 0.0)
                
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"✅ **COMPRA REALIZADA COM SUCESSO!**\n\n"
                        f"🎫 **Número do Pedido:** {order_id}\n"
                        f"💰 **Valor Total:** R$ {total_amount:.2f}\n"
                        f"📦 **Produto:** {product_info.get('productName', 'N/A')}\n\n"
                        f"🚚 **Próximos passos:**\n"
                        f"• Você receberá uma confirmação por email\n"
                        f"• O produto será enviado em até 5 dias úteis\n"
                        f"• Acompanhe seu pedido no menu 'Consultar Pedidos'\n\n"
                        f"🎉 **Obrigado pela sua compra!**"
                    )
                )
            else:
                # Erro na compra
                await step_context.context.send_activity(
                    MessageFactory.text(
                        "❌ **ERRO NO PROCESSAMENTO**\n\n"
                        "Não foi possível processar sua compra no momento.\n\n"
                        "🔄 **Possíveis causas:**\n"
                        "• Saldo insuficiente no cartão\n"
                        "• Cartão expirado ou bloqueado\n"
                        "• Produto fora de estoque\n"
                        "• Erro temporário no sistema\n\n"
                        "💡 **Tente novamente em alguns minutos.**"
                    )
                )
                
        except Exception as e:
            print(f"[BOT] Erro ao processar compra: {e}")
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **ERRO INESPERADO**\n\n"
                    "Ocorreu um erro inesperado ao processar sua compra.\n\n"
                    "🛠️ **Nossa equipe foi notificada do problema.**\n"
                    "Por favor, tente novamente em alguns minutos."
                )
            )

        return await step_context.end_dialog()

    def validar_numero_cartao(self, numero: str) -> bool:
        """Valida se o número do cartão tem 16 dígitos"""
        return numero.isdigit() and len(numero) == 16

    def validar_data_expiracao(self, data: str) -> bool:
        """Valida se a data está no formato MM/AA e não está expirada"""
        pattern = r'^(0[1-9]|1[0-2])\/([0-9]{2})$'
        if not re.match(pattern, data):
            return False
        
        try:
            mes, ano = data.split('/')
            mes = int(mes)
            ano = int('20' + ano)  # Converte YY para YYYY
            
            # Verifica se não está expirado
            agora = datetime.now()
            return ano > agora.year or (ano == agora.year and mes >= agora.month)
        except:
            return False

    def validar_cvv(self, cvv: str) -> bool:
        """Valida se o CVV tem 3 dígitos"""
        return cvv.isdigit() and len(cvv) == 3