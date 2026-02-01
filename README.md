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

Em breve será postado...
Coming soon
