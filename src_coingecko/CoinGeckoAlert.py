import requests
import asyncio
import time
from telegram import Bot
from difflib import get_close_matches

# Lista de nomes de activos que serão pesquisados
moedas_nomes = [
    "Bitcoin", "Celestia", "Tron", "VeChain", "Mantra",
    "Immutable X", "Akash Network", "Artificial Superintelligence Alliance",
    "Arweave", "Eigenlayer", "Geodnet", "Helium", "Bonk", "LayerZero", "JasmyCoin", "Flare", "Trust Wallet",
    "Algorand", "Toncoin", "Hedera", "Stacks", "XDC Network", "Pyth Network", "SKALE", "Civic", "Celer Network", "Sei",
    "0x Protocol", "Audius",
    "Storj", "Hathor", "Reserve Rights", "Livepeer", "Immutable", "UMA", "XRP", "Litecoin", "Chainlink", "Stellar",
    "Tezos", "The Graph", "NEXO"
]


# Função que carrega todos os ids de moedas presentes na API do CoinGecko
def carregar_ids_validos():
    url = f"https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Falha ao carregar a lista de moedas.")
    return response.json()


# Armazena todos os ids
todos = carregar_ids_validos()


# Nem sempre o nome da moeda no site da coingecko corresponde com o id da API do site. Para evitar possíveis erros todos os nomes passam por uma verificação,
# retornando o id correto.
def lista_ids(nomes):
    ativos_id = []
    for i in nomes:
        for j in todos:
            if i == j['name']:
                ativos_id.append(j['id'])
    return ativos_id


ativos_id = lista_ids(moedas_nomes)


# Função para envio no Telegram
async def enviar_mensagem(mensg):
    bot_token = 'Bot telegram token'
    chat_id = 'token chat telegram'
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=mensg)


# Utilizando 3 chaves demo CoinGecko (para evitar a falta de crédito)
api_key3 = 'Key api demo'
api_key1 = 'Other key api demo'
api_key2 = 'Other key api demo'
lista_keys = [api_key1, api_key2, api_key3]


def direcao(valor):
    return "valorizou" if valor > 0 else "desvalorizou"


async def verificar_ativos(apiK):
    for ticker in ativos_id:
        # Usando a API pública + chave como parâmetro
        url = (
            f"https://api.coingecko.com/api/v3/coins/{ticker}"
            f"?localization=false&tickers=false&market_data=true&community_data=false"
            f"&developer_data=false&sparkline=false"
            f"&x_cg_demo_api_key={apiK}"  # <- chave via query param!
        )

        try:
            # Coleta e divide todas as informações importantes relacionada a moeda pesquisada
            response = requests.get(url)

            data = response.json()
            market_data = data.get("market_data", {})
            current_price = market_data.get("current_price", {}).get("usd")
            change_1y = market_data.get("price_change_percentage_1y_in_currency", {}).get("usd")
            change_7d = market_data.get("price_change_percentage_7d_in_currency", {}).get("usd")
            change_24h = market_data.get("price_change_percentage_24h_in_currency", {}).get("usd")

            print(
                f"{ticker.upper()}: ${current_price:.2f} | 1y: {change_1y:.2f}% | 7d: {change_7d:.2f}% | 24h: {change_24h:.2f}%")

            # Caso tenha informação de um ano atrás se faz uma maior filtragem: avalia a avaliação a 30 dias, depois de 7 dias e a mudança em 24 horas.
            # Para 1 ano verifica se variou mais de 30%, para 7 dias 15% e para 24 horas maior ou igual a 10%
            if change_1y is not None:
                if abs(change_1y) > 30 and abs(change_7d) > 15 and abs(change_24h) >= 10:
                    mensagem = (
                        f"🚨 ALERTA COINGECKO 🚨\n"
                        f"{ticker.upper()}\n"
                        f"Preço atual: ${current_price: }\n"
                        f"Variação em 1 ano: {change_1y:.2f}% ({direcao(change_1y)})\n"
                        f"Variação em 7 dias: {change_7d:.2f}% ({direcao(change_7d)})\n"
                        f"Variação em 24h: {change_24h:.2f}% ({direcao(change_24h)})\n"
                        f"⚠️ Todos os critérios foram atendidos!"
                    )
                    await enviar_mensagem(mensagem)

            # Caso não tenha informação sobre a variação de um ano apenas foca na análise de uma semana e de 24 horas
            elif change_7d is not None and change_24h is not None:
                if abs(change_7d) > 15 and abs(change_24h) >= 10:
                    mensagem = (
                        f"🚨 ALERTA COINGECKO 🚨\n"
                        f"{ticker.upper()}\n"
                        f"Preço atual: ${current_price:}\n"
                        f"Variação em 7 dias: {change_7d:.2f}% ({direcao(change_7d)})\n"
                        f"Variação em 24h: {change_24h:.2f}% ({direcao(change_24h)})\n"
                        f"⚠️ Todos os critérios foram atendidos (sem dados anuais)!"
                    )
                    await enviar_mensagem(mensagem)


        except Exception as e:
            print(f"❌ Erro com {ticker}: {e}")

        # Delay entre as requisições
        time.sleep(5)


# O main executa as principais funções do código e também, através de flags, altera a chave que será utilizada para não utilizar todos os créditos de uma vez e distribuir o trabalho
async def main():
    flag = 0
    index = 0

    while True:
        await verificar_ativos(lista_keys[index])
        await asyncio.sleep(900)  # 15 minutos
        flag = flag + 1

        if flag == 15:
            index = index + 1
            flag = 0

        if index > 3:
            index = 0

asyncio.run(main())
