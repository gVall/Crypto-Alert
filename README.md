# Crypto-Alert

Crypto Alert é um projeto de monitoramento e notificação da variação de criptomoedas (podendo ser adaptado para ações). Para as notificações, utilizamos um chatbot do Telegram.

English: Crypto Alert is a project designed to monitor and notify users about cryptocurrency price variations (it can also be adapted for stocks). Notifications are handled via a Telegram chatbot.

Existem dois métodos para a monitoração: a primeira utilizando o Google Finance (Web Scraping) e a segunda via CoinGecko.

English: There are two different methods for monitoring: the first uses Google Finance (Web Scraping) and the second uses the CoinGecko API.

## Google Finance

Em resumo, neste método as moedas são acessadas na página do Google Finance a cada 8 minutos para coletar as informações necessárias: variação e valorização/desvalorização. A extração é feita via HTML com um intervalo de segurança para evitar bloqueios (flood).

English: In summary, this method accesses Google Finance every 8 minutes to collect essential data: price variation and whether the asset gained or lost value. Data is extracted directly from the HTML, with a minimum 8-minute interval to prevent rate limiting or "flooding."

### Código / Code

O código está comentado em PT-BR, mas seu funcionamento é bastante intuitivo.

English: The code is commented in Brazilian Portuguese, but its logic is very intuitive (a translated version may be released later).

A função responsável por coletar as informações é: English: The function responsible for collecting data from the page is:

```python
def check_asset_variation(asset_code: str) -> list:
```
A conversão de string para um valor numérico real funciona neste bloco:
English: The conversion from a string to a numeric value (representing the asset price) happens in this block:

```python
price_div = soup.find("div", class_="YMlKec fxKbKc")
        if price_div:
            current_price_text = price_div.text.strip()

            # Remove símbolos de moeda e espaços
            for simbolo in ['R$', '$', '€', '£']:
                current_price_text = current_price_text.replace(simbolo, '')

            current_price_text = current_price_text.strip()

            # Remove pontos de milhar (exemplo: transforma 13.725,00 em 13725,00)
            # Mantemos apenas o último separador (que é a vírgula decimal)
            partes = current_price_text.split(',')

            if len(partes) > 1:
                # Remove os pontos da parte inteira
                parte_inteira = partes[0].replace('.', '')
                parte_decimal = partes[1]
                current_price_text = f"{parte_inteira}.{parte_decimal}"
            else:
                # Caso não tenha vírgula, apenas remove os pontos
                current_price_text = current_price_text.replace('.', '')
```
A função abaixo é responsável por enviar as mensagens de alerta: 
English: The function below is responsible for sending alert messages to a Telegram chat (requires your own API and Chat keys):

```python
async def enviar_mensagem(mensg):
    bot_token = '{Key bot telegram}'
    chat_id = '{Key chat id telegram}'
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=mensg)
```
No main, os ativos são pesquisados e, caso ocorra uma variação de 10% (valorização ou desvalorização), uma mensagem é enviada.

English: In the main script, the assets are processed. If a price variation of 10% or more (appreciation or devaluation) is detected, a notification is sent via Telegram.

Para gerar um executável do código, basta digitar no terminal:
English: To generate an executable file, simply run the following command in your terminal:

```python
pyinstaller --onefile crypto.py
```

## API Coingecko

A CoinGecko é uma plataforma especializada no monitoramento de criptomoedas e ativos financeiros. A plataforma fornece uma API de consulta com planos pagos e gratuitos (demo). O código desenvolvido a partir desta API permite monitorar uma gama maior de moedas (incluindo aquelas não listadas no Google Finance) e possibilita um volume maior de consultas em intervalos de tempo reduzidos, sem o risco de bloqueios.

English: CoinGecko is a platform specialized in cryptocurrency and financial asset monitoring. It provides an API with both paid and demo (free) plans. By using the official API, this version of the code allows for tracking a wider range of coins (including those not available on Google Finance) and supports a higher frequency of requests within shorter intervals, ensuring better reliability and scalability.

CoinGecko: https://www.coingecko.com/pt-br

### Código / Code

A primeira grande diferença é que todos os ativos da lista do usuário precisam ser validados. Na API da CoinGecko, cada moeda possui um ID único específico; portanto, o primeiro passo do algoritmo é verificar e armazenar o ID correto para garantir que as consultas futuras sejam precisas.

English: The first major difference is that all assets in the user's list must be validated. In the CoinGecko API, every coin is assigned a unique ID. Therefore, the first step is to verify and store the correct ID to ensure that all subsequent data requests are accurate.

```python
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
```
A função para mandar o alerta continua o mesmo do outro programa.
English: The alert function is the same.

Esta é a função principal, responsável pela coleta de dados e pela análise posterior. O diferencial aqui reside na análise: o foco é monitorar as variações anual, semanal e diária. Dessa forma, é possível identificar tendências de mercado e os melhores momentos para investimento.
English: This is the core function, responsible for data collection and subsequent analysis. The main highlight here is the analytical approach: the focus is on monitoring annual, weekly, and daily variations. This allows the user to identify market trends and pinpoint the best potential entry points for investment.

```python
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
```
