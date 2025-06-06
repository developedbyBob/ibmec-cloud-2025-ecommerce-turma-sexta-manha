# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    ChoicePrompt,
    PromptOptions,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

# Importa os diálogos específicos
from dialogs.consultar_produtos_dialog import ConsultarProdutosDialog
from dialogs.consultar_pedidos_dialog import ConsultarPedidosDialog
from dialogs.extrato_compra_dialog import ExtratoCompraDialog

class MainDialog(ComponentDialog):
    """
    Diálogo principal que apresenta o menu de opções para o usuário
    """
    
    def __init__(self, user_state: UserState):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self.user_state = user_state

        # Adiciona os diálogos específicos para cada funcionalidade
        self.add_dialog(ConsultarProdutosDialog(user_state))
        self.add_dialog(ConsultarPedidosDialog())
        self.add_dialog(ExtratoCompraDialog())

        # Adiciona o diálogo principal (waterfall)
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.prompt_option_step,
                    self.process_option_step,
                    self.restart_step
                ],
            )
        )

        # Adiciona o prompt de escolha
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        # Define o diálogo inicial
        self.initial_dialog_id = WaterfallDialog.__name__

    async def prompt_option_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Apresenta o menu principal de opções para o usuário
        """
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(
                    "🛍️ **IBMEC MALL - Menu Principal**\n\n"
                    "Escolha uma das opções abaixo:"
                ),
                choices=[
                    Choice("🔍 Consultar Produtos"), 
                    Choice("📦 Consultar Pedidos"), 
                    Choice("💳 Extrato de Compras")
                ],
            ),
        )

    async def process_option_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Processa a opção escolhida pelo usuário e inicia o diálogo correspondente
        """
        option = step_context.result.value

        if option == "🔍 Consultar Produtos":
            # Inicia o diálogo de consulta de produtos
            return await step_context.begin_dialog("ConsultarProdutosDialog")
            
        elif option == "📦 Consultar Pedidos":
            # Inicia o diálogo de consulta de pedidos
            return await step_context.begin_dialog("ConsultarPedidosDialog")
            
        elif option == "💳 Extrato de Compras":
            # Inicia o diálogo de extrato de compras
            return await step_context.begin_dialog("ExtratoCompraDialog")

        # Se chegou aqui, algo deu errado
        await step_context.context.send_activity(
            MessageFactory.text("❌ Opção não reconhecida. Tente novamente.")
        )
        return await step_context.end_dialog()

    async def restart_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Após completar uma ação, oferece voltar ao menu principal
        """
        await step_context.context.send_activity(
            MessageFactory.text(
                "✅ Operação concluída!\n\n"
                "💬 Digite qualquer mensagem para voltar ao menu principal."
            )
        )
        
        # Termina este diálogo, o que fará o bot voltar ao início
        return await step_context.end_dialog()