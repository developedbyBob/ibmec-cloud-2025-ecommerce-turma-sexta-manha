# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import StatePropertyAccessor, TurnContext
from botbuilder.dialogs import Dialog, DialogSet, DialogTurnStatus

class DialogHelper:
    """
    Classe auxiliar para executar diálogos
    """
    
    @staticmethod
    async def run_dialog(
        dialog: Dialog, turn_context: TurnContext, accessor: StatePropertyAccessor
    ):
        """
        Executa um diálogo específico
        """
        dialog_set = DialogSet(accessor)
        dialog_set.add(dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        results = await dialog_context.continue_dialog()
        
        # Se não há diálogo ativo, inicia um novo
        if results.status == DialogTurnStatus.Empty:
            await dialog_context.begin_dialog(dialog.id)