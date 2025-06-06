#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Configurações do Bot """

    # Porta onde o bot vai rodar (padrão do Bot Framework)
    PORT = 3978
    
    # ID e senha do bot (quando deployar no Azure, essas variáveis serão configuradas automaticamente)
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    
    # URL da sua API (CORRIGIDA com a URL real do Azure)
    URL_PREFIX = os.environ.get("URL_PREFIX", "https://ibmec-ecommerce-app-gydeg9hye0eabpbf.brazilsouth-01.azurewebsites.net")