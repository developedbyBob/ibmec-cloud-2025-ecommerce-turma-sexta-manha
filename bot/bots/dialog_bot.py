# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper

class DialogBot(ActivityHandler):
    """
    Bot principal que gerencia as conversas usando diálogos
    """

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
    ):
        # Validação dos parâmetros obrigatórios
        if conversation_state is None:
            raise TypeError(
                "[DialogBot]: conversation_state é obrigatório mas None foi fornecido"
            )
        if user_state is None:
            raise TypeError(
                "[DialogBot]: user_state é obrigatório mas None foi fornecido"
            )
        if dialog is None:
            raise Exception("[DialogBot]: dialog é obrigatório")

        # Armazena os estados e o diálogo
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog

    async def on_turn(self, turn_context: TurnContext):
        """
        Processa cada mensagem/interação do usuário
        """
        await super().on_turn(turn_context)
        
        # Salva os estados após cada interação
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Processa mensagens de texto do usuário
        """
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"),
        )

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """
        Executa quando alguém se conecta ao bot pela primeira vez
        """
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"🛍️ Seja bem-vindo(a) ao **IBMEC MALL**! "
                    f"\n\nSou seu assistente virtual e posso te ajudar com:"
                    f"\n• 🔍 Consultar produtos"
                    f"\n• 🛒 Fazer compras"
                    f"\n• 📦 Verificar pedidos"
                    f"\n• 💳 Ver extrato de compras"
                    f"\n\nDigite qualquer mensagem para começar!"
                )