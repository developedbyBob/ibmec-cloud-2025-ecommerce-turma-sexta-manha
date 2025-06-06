from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext
from botbuilder.core import MessageFactory
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.dialogs import DialogTurnStatus, DialogTurnResult
from botbuilder.schema import (
    ActionTypes,
    HeroCard,
    CardAction,
    CardImage,
)
from botbuilder.core import CardFactory, UserState
from api.product_api import ProductAPI
from dialogs.comprar_produto_dialog import ComprarProdutoDialog

class ConsultarProdutosDialog(ComponentDialog):
    """
    Diálogo para consultar produtos
    Permite buscar produtos por nome e exibi-los em cards interativos
    """
    
    def __init__(self, user_state: UserState):
        super(ConsultarProdutosDialog, self).__init__("ConsultarProdutosDialog")

        # Adiciona os prompts necessários
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(TextPrompt("opcaoEscolha"))

        # Adiciona o diálogo de compra
        self.add_dialog(ComprarProdutoDialog(user_state))

        # Adiciona o fluxo principal (waterfall)
        self.add_dialog(
            WaterfallDialog(
                "consultarProdutoWaterfall",
                [
                    self.escolher_opcao_step,
                    self.processar_escolha_step,
                    self.product_name_search_step,
                    self.aguardar_acao_step
                ],
            )
        )

        # Define o diálogo inicial
        self.initial_dialog_id = "consultarProdutoWaterfall"
    
    async def escolher_opcao_step(self, step_context: WaterfallStepContext):
        """
        Oferece opções: ver todos os produtos ou buscar por nome
        """
        prompt_message = MessageFactory.text(
            "🔍 **Consulta de Produtos**\n\n"
            "Como você gostaria de buscar?\n\n"
            "• Digite **'todos'** para ver todos os produtos\n"
            "• Digite **o nome** do produto que você procura\n"
            "• Digite **'voltar'** para retornar ao menu principal"
        )

        prompt_options = PromptOptions(
            prompt=prompt_message,
            retry_prompt=MessageFactory.text(
                "❌ Por favor, digite 'todos', o nome de um produto, ou 'voltar'."
            ),
        )
        
        return await step_context.prompt(TextPrompt.__name__, prompt_options)

    async def processar_escolha_step(self, step_context: WaterfallStepContext):
        """
        Processa a escolha do usuário
        """
        escolha = step_context.result.lower().strip()
        
        # Armazena a escolha para o próximo step
        step_context.values["escolha"] = escolha
        
        if escolha == "voltar":
            await step_context.context.send_activity(
                MessageFactory.text("↩️ Voltando ao menu principal...")
            )
            return await step_context.end_dialog()
        
        # Continua para o próximo step (busca)
        return await step_context.next(escolha)

    async def product_name_search_step(self, step_context: WaterfallStepContext):
        """
        Busca os produtos na API e exibe os resultados
        """
        escolha = step_context.values["escolha"]
        produto_api = ProductAPI()

        # Testa conexão primeiro
        if not produto_api.test_connection():
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Erro de Conexão**\n\n"
                    "Não foi possível conectar com o sistema de produtos. "
                    "Tente novamente em alguns instantes."
                )
            )
            return await step_context.end_dialog()

        try:
            # Busca produtos baseado na escolha
            if escolha == "todos":
                await step_context.context.send_activity(
                    MessageFactory.text("🔄 Buscando todos os produtos disponíveis...")
                )
                produtos = produto_api.get_products()
            else:
                await step_context.context.send_activity(
                    MessageFactory.text(f"🔄 Buscando produtos com '{escolha}'...")
                )
                produtos = produto_api.search_product(escolha)

            # Verifica se encontrou produtos
            if produtos is None:
                await step_context.context.send_activity(
                    MessageFactory.text(
                        "❌ **Erro na Busca**\n\n"
                        "Ocorreu um erro ao buscar produtos. Tente novamente."
                    )
                )
                return await step_context.end_dialog()

            elif len(produtos) == 0:
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"😔 **Nenhum produto encontrado**\n\n"
                        f"Não encontramos produtos {'disponíveis' if escolha == 'todos' else f'com o nome \"{escolha}\"'}.\n\n"
                        f"💡 **Dicas:**\n"
                        f"• Tente usar palavras-chave diferentes\n"
                        f"• Verifique a ortografia\n"
                        f"• Use termos mais gerais (ex: 'notebook' em vez de 'notebook gamer')"
                    )
                )
                return await step_context.end_dialog()

            else:
                # Exibe os produtos encontrados
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"✅ **{len(produtos)} produto(s) encontrado(s)!**\n\n"
                        f"📱 Clique em **'Comprar'** para adquirir o produto desejado:"
                    )
                )
                
                # Exibe cada produto como um card
                await self.show_products_as_cards(produtos, step_context)

                # Continua aguardando a ação do usuário
                return DialogTurnResult(
                    status=DialogTurnStatus.Waiting,
                    result=step_context.result,
                )

        except Exception as e:
            print(f"[BOT] Erro inesperado na busca de produtos: {e}")
            await step_context.context.send_activity(
                MessageFactory.text(
                    "❌ **Erro Inesperado**\n\n"
                    "Ocorreu um erro inesperado. Tente novamente."
                )
            )
            return await step_context.end_dialog()

    async def aguardar_acao_step(self, step_context: WaterfallStepContext):
        """
        Aguarda o usuário clicar em um botão de ação (Comprar)
        """
        # Verifica se o usuário clicou em algum botão
        if hasattr(step_context.context.activity, 'value') and step_context.context.activity.value:
            result_action = step_context.context.activity.value

            if result_action.get("acao") == "comprar":
                product_id = result_action.get("productId")
                product_name = result_action.get("productName", "produto")

                await step_context.context.send_activity(
                    MessageFactory.text(f"🛒 Iniciando compra do produto: **{product_name}**")
                )

                # Inicia o diálogo de compra passando as informações do produto
                return await step_context.begin_dialog(
                    "ComprarProdutoDialog", 
                    {
                        "productId": product_id,
                        "productName": product_name,
                        "productInfo": result_action
                    }
                )

        # Se não há ação válida, termina o diálogo
        await step_context.context.send_activity(
            MessageFactory.text(
                "ℹ️ Consulta de produtos finalizada.\n\n"
                "💬 Digite qualquer mensagem para voltar ao menu principal."
            )
        )
        return await step_context.end_dialog()

    async def show_products_as_cards(self, produtos, step_context: WaterfallStepContext):
        """
        Exibe os produtos como cards interativos
        """
        for produto in produtos:
            try:
                # Monta as informações do produto
                product_name = produto.get("productName", "Produto sem nome")
                price = produto.get("price", 0.0)
                description = produto.get("productDescription", "Sem descrição")
                product_id = produto.get("id", "")
                images = produto.get("imageUrl", [])

                # Formata o preço
                price_formatted = f"R$ {price:.2f}".replace(".", ",")

                # Prepara as imagens (usa a primeira ou uma imagem padrão)
                card_images = []
                if images and len(images) > 0:
                    # Usa a primeira imagem
                    card_images = [CardImage(url=images[0])]
                else:
                    # Imagem padrão se não houver imagem
                    card_images = [CardImage(url="https://via.placeholder.com/300x200?text=Produto")]

                # Monta o card do produto
                card = CardFactory.hero_card(
                    HeroCard(
                        title=product_name,
                        subtitle=f"💰 {price_formatted}",
                        text=description[:100] + "..." if len(description) > 100 else description,
                        images=card_images,
                        buttons=[
                            CardAction(
                                type=ActionTypes.post_back,
                                title=f"🛒 Comprar {product_name[:20]}{'...' if len(product_name) > 20 else ''}",
                                value={
                                    "acao": "comprar", 
                                    "productId": product_id,
                                    "productName": product_name,
                                    "price": price,
                                    "description": description
                                },
                            )
                        ],
                    )
                )

                # Envia o card
                await step_context.context.send_activity(MessageFactory.attachment(card))
                
            except Exception as e:
                print(f"[BOT] Erro ao criar card para produto: {e}")
                # Se der erro no card, envia como texto simples
                await step_context.context.send_activity(
                    MessageFactory.text(
                        f"🛍️ **{product_name}**\n"
                        f"💰 {price_formatted}\n"
                        f"📝 {description}\n"
                        f"🆔 ID: {product_id}"
                    )
                )