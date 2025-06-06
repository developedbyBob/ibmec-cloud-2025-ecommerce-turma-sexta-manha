# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
    MemoryStorage,
    ConversationState,
    UserState
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig
from dialogs.main_dialog import MainDialog
from bots.dialog_bot import DialogBot

# Carrega as configurações
CONFIG = DefaultConfig()

# Cria o adaptador do bot
# Esse adaptador é responsável por conectar o bot com o Microsoft Bot Framework
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Função para tratar erros do bot
async def on_error(context: TurnContext, error: Exception):
    # Loga o erro no console
    print(f"\n [on_turn_error] erro não tratado: {error}", file=sys.stderr)
    traceback.print_exc()

    # Envia mensagem de erro para o usuário
    await context.send_activity("O bot encontrou um erro ou bug.")
    await context.send_activity(
        "Para continuar usando este bot, por favor reporte o problema."
    )
    
    # Se estivermos no emulador, envia informações detalhadas do erro
    if context.activity.channel_id == "emulator":
        # Cria uma atividade de trace com detalhes do erro
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Envia o trace para o emulador
        await context.send_activity(trace_activity)

# Configura o tratamento de erros
ADAPTER.on_turn_error = on_error

# Cria o armazenamento em memória e os estados
MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
USER_STATE = UserState(MEMORY)

# Cria o diálogo principal e o bot
DIALOG = MainDialog(USER_STATE)
BOT = DialogBot(CONVERSATION_STATE, USER_STATE, DIALOG)

# Função que processa as mensagens recebidas
async def messages(req: Request) -> Response:
    # Processa mensagens vindas do Microsoft Bot Framework
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)

# Cria a aplicação web
APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

# Inicia o servidor do bot
if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
        print(f"Bot iniciado na porta {CONFIG.PORT}")
    except Exception as error:
        raise error