from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from api.product_api import ProductAPI
from datetime import datetime

class ExtratoCompraDialog(ComponentDialog):
    """
    Diálogo para consultar extrato de compras (histórico de transações do cartão)
    """
    
    def __init__(self):
        super(ExtratoCompraDialog, self).__init__("ExtratoCompraDialog")

        # Adiciona os prompts necessários
        self.add_dialog(TextPrompt("userIdPrompt"))
        self.add_dialog(TextPrompt("cardIdPrompt"))

        # Adiciona o fluxo principal
        self.add_dialog(
            WaterfallDialog(
                "extratoCompraWaterfall",
                [
                    self.solicitar_user_id_step,
                    self.solicitar_card_id_step,
                    self.buscar_extrato_step,
                ],
            )
        )

        # Define o diálogo inicial
        self.initial_dialog_id = "extratoCompraWaterfall"

    async def solicitar_user_id_step(self, step_context: WaterfallStepContext):
        """
        Solicita o ID do usuário
        """
        await step_context.context.send_activity(
            MessageFactory.text(
                "💳 **Extrato de Compras**\n\n"
                "Para consultar seu extrato de transações, preciso de algumas informações.\n\n"
                "💡 **Em um sistema real, você já estaria logado automaticamente.**"
            )
        )
        
        prompt_message = MessageFactory.text("👤 Digite seu ID de usuário (número):")

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite um número válido para o ID do usuário."),
        )
        
        return await step_context.prompt("userIdPrompt", prompt_options)

    async def solicitar_card_id_step(self, step_context: WaterfallStepContext):
        """
        Solicita o ID do cartão
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
            "💳 **ID do Cartão**\n\n"
            "Digite o ID do cartão para consultar o extrato:\n\n"
            "💡 **Dica:** Normalmente é 1, 2, 3... conforme a ordem que você cadastrou os cartões."
        )

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text("❌ Por favor, digite um número válido para o ID do cartão."),
        )
        
        return await step_context.prompt("cardIdPrompt", prompt_options)

    async def buscar_extrato_step(self, step_context: WaterfallStepContext):
        """
        Busca e exibe o extrato do cartão
        """
        card_id_input = step_context.result.strip()
        
        # Valida se é um número
        if not card_id_input.isdigit():
            await step_context.context.send_activity(
                MessageFactory.text("❌ ID do cartão deve ser um número válido.")
            )
            return await step_context.end_dialog()
        
        user_id = step_context.values["user_id"]
        card_id = int(card_id_input)
        
        # Testa conexão com a API
        produto_api = ProductAPI()
        if not produto_api.test_connection():
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Erro de Conexão**\n\n"
                    "Não foi possível conectar com o sistema de extratos. "
                    "Tente novamente em alguns instantes."
                )
            )
            return await step_context.end_dialog()

        # Busca o extrato
        await step_context.context.send_activity(
            MessageFactory.text(f"🔄 Buscando extrato do cartão {card_id} para usuário {user_id}...")
        )

        try:
            transacoes = produto_api.get_card_statement(user_id, card_id)
            
            if transacoes is None:
                await step_context.context.send_activity(
                    MessageFactory.text(
                        "❌ **Erro na Consulta**\n\n"
                        "Possíveis causas:\n"
                        "• Cartão não encontrado\n"
                        "• Cartão não pertence ao usuário\n"
                        "• Erro temporário no sistema\n\n"
                        "🔄 **Verifique os dados e tente novamente.**"
                    )
                )
                return await step_context.end_dialog()

            elif len(transacoes) == 0:
                await step_context.context.send_activity(
                    MessageFactory.text(
                        "📄 **Extrato Vazio**\n\n"
                        f"O cartão {card_id} ainda não possui transações registradas.\n\n"
                        "💡 **As transações aparecerão aqui quando você:**\n"
                        "• Realizar compras\n"
                        "• Adicionar créditos ao cartão\n"
                        "• Fazer outras operações financeiras"
                    )
                )
                return await step_context.end_dialog()

            else:
                # Exibe o extrato
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"✅ **Extrato encontrado!**\n\n"
                        f"💳 **Cartão:** {card_id}\n"
                        f"📊 **Total de transações:** {len(transacoes)}\n\n"
                        f"📋 **Histórico de transações:**"
                    )
                )
                
                # Exibe cada transação
                await self.exibir_transacoes(transacoes, step_context)

                await step_context.context.send_activity(
                    MessageFactory.text(
                        "✅ **Extrato completo!**\n\n"
                        "💬 Digite qualquer mensagem para voltar ao menu principal."
                    )
                )

        except Exception as e:
            print(f"[BOT] Erro inesperado na consulta de extrato: {e}")
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Erro Inesperado**\n\n"
                    "Ocorreu um erro inesperado ao consultar o extrato. Tente novamente."
                )
            )

        return await step_context.end_dialog()

    async def exibir_transacoes(self, transacoes, step_context: WaterfallStepContext):
        """
        Exibe as transações de forma organizada
        """
        # Calcula totais
        total_compras = 0
        total_creditos = 0
        
        for transacao in transacoes:
            valor = transacao.get("valor", 0.0)
            tipo = transacao.get("tipoTransacao", "").upper()
            
            if tipo == "COMPRA":
                total_compras += valor
            elif tipo in ["CARGA", "CREDITO"]:
                total_creditos += valor

        # Exibe resumo
        saldo_atual = total_creditos - total_compras
        
        resumo = (
            f"💰 **RESUMO FINANCEIRO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 **Total Créditos:** R$ {total_creditos:.2f}\n"
            f"🛒 **Total Compras:** R$ {total_compras:.2f}\n"
            f"💵 **Saldo Atual:** R$ {saldo_atual:.2f}\n\n"
        )
        
        await step_context.context.send_activity(MessageFactory.text(resumo))

        # Exibe transações individuais (máximo 10 mais recentes)
        transacoes_exibir = transacoes[:10]  # Limita para não sobrecarregar
        
        for i, transacao in enumerate(transacoes_exibir, 1):
            try:
                # Extrai informações da transação
                data_transacao = transacao.get("dataTransacao", "")
                valor = transacao.get("valor", 0.0)
                tipo = transacao.get("tipoTransacao", "UNKNOWN")
                descricao = transacao.get("descricao", "Sem descrição")
                codigo_autorizacao = transacao.get("codigoAutorizacao", "N/A")

                # Formata a data
                data_formatada = self.formatar_data(data_transacao)
                
                # Formata o valor
                valor_formatado = f"R$ {valor:.2f}".replace(".", ",")
                
                # Formata o tipo e emoji
                tipo_emoji = self.get_tipo_emoji(tipo)
                tipo_texto = self.get_tipo_texto(tipo)
                
                # Define cor baseada no tipo (+ ou -)
                sinal = "+" if tipo.upper() in ["CARGA", "CREDITO"] else "-"
                
                # Monta a mensagem da transação
                mensagem_transacao = (
                    f"{tipo_emoji} **TRANSAÇÃO #{i}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"📅 **Data:** {data_formatada}\n"
                    f"🏷️ **Tipo:** {tipo_texto}\n"
                    f"💰 **Valor:** {sinal}{valor_formatado}\n"
                    f"📝 **Descrição:** {descricao}\n"
                    f"🔑 **Autorização:** {codigo_autorizacao[:8]}...\n\n"
                )

                await step_context.context.send_activity(
                    MessageFactory.text(mensagem_transacao)
                )
                
            except Exception as e:
                print(f"[BOT] Erro ao exibir transação: {e}")
                # Se der erro, exibe versão simplificada
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"💳 **Transação #{i}:** {transacao.get('tipoTransacao', 'N/A')} - "
                        f"R$ {transacao.get('valor', 0.0):.2f}"
                    )
                )

        # Se há mais transações, informa
        if len(transacoes) > 10:
            await step_context.context.send_activity(
                MessageFactory.text(
                    f"ℹ️ **Exibindo as 10 transações mais recentes.**\n"
                    f"Total de {len(transacoes)} transações no histórico."
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

    def get_tipo_emoji(self, tipo: str) -> str:
        """
        Retorna emoji baseado no tipo de transação
        """
        tipo_emojis = {
            "COMPRA": "🛒",
            "CARGA": "💳",
            "CREDITO": "💰",
            "ESTORNO": "↩️"
        }
        return tipo_emojis.get(tipo.upper(), "💸")

    def get_tipo_texto(self, tipo: str) -> str:
        """
        Retorna texto amigável para o tipo de transação
        """
        tipo_textos = {
            "COMPRA": "Compra",
            "CARGA": "Recarga de Crédito",
            "CREDITO": "Crédito",
            "ESTORNO": "Estorno"
        }
        return tipo_textos.get(tipo.upper(), tipo)