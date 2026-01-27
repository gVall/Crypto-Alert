from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from telegram import Bot
import time
import asyncio
import re

# Mantém no máximo os 2 últimos preços de cada ativo
historico_valores = {}

def check_asset_variation(asset_code: str) -> list:
    """
    Coleta status, variação percentual e preço atual do ativo.
    """
    url = f"https://www.google.com/finance/quote/{asset_code}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        container = soup.find("div", class_="enJeMd")

        if not container:
            return [asset_code, "❌ Container não encontrado", "N/A", "N/A"]

        # Variação percentual
        percent_span = None
        for span in container.find_all("span"):
            if span.text.strip().endswith('%'):
                percent_span = span
                break

        variation = percent_span.text.strip() if percent_span else "N/A"

        # Status com base nas setas
        paths = container.find_all("path")
        all_d = [p.get("d") for p in paths]

        down_path = "M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"
        up_path = "M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"

        if up_path in all_d:
            status = "📈 Valorização"
        elif down_path in all_d:
            status = "📉 Desvalorização"
        else:
            status = "❓ Direção não identificada"

        # Preço atual
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

            try:
                current_price = float(current_price_text)
            except:
                current_price = None
        else:
            current_price = None

        return [asset_code, status, variation, current_price]

    except Exception as e:
        return [asset_code, f"Erro: {e}", "N/A", "N/A"]

    finally:
        driver.quit()

async def enviar_mensagem(mensg):
    bot_token = ''
    chat_id = ''
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=mensg)

async def main():
    ativos = ["DOGE-BRL", "ADA-BRL", "ETH-BRL", "SOLZ:NASDAQ", "TRX-BRL", "LINK-BRL", 'XLM-BRL', 'ZRX-BRL', 'KMD-SBD', 'MOVE:NASDAQ', 'TRX-BRL',
              ]

    while True:
        for ativo in ativos:
            value = check_asset_variation(ativo)
            asset_code, status, percent, current_price = value

            # Mantém só os 2 últimos valores
            if asset_code not in historico_valores:
                historico_valores[asset_code] = []

            if isinstance(current_price, float):
                historico_valores[asset_code].append(current_price)
                if len(historico_valores[asset_code]) > 2:
                    historico_valores[asset_code].pop(0)  # Remove o mais antigo

            # Cálculo da variação de preço
            price_variation = "N/A"
            price_variation_percent = "N/A"
            if len(historico_valores[asset_code]) == 2:
                old_price, new_price = historico_valores[asset_code]
                price_diff = new_price - old_price
                price_variation_percent = (price_diff / old_price) * 100 if old_price != 0 else 0
                price_variation = round(price_diff, 4)
                price_variation_percent = round(price_variation_percent, 2)

            print(
                f"{asset_code} -> {status}: {percent} | Preço: {current_price} | Δ {price_variation} ({price_variation_percent}%)")

            # 🔴 PRIMEIRO: ALERTA BASEADO NA VARIAÇÃO DE 24 HORAS (do site)
            percent_clean = percent.replace("%", "").replace(",", ".").replace("−", "-")
            try:
                percent_float = float(percent_clean)
            except ValueError:
                percent_float = 0.0

            if "Desvalorização" in status:
                if percent_float >= 10.0:
                    await enviar_mensagem(f"[ALERTA 24H] Desvalorizou! {asset_code} -> {status}: {percent}")
            elif "Valorização" in status:
                if percent_float >= 10.0:
                    await enviar_mensagem(f"[ALERTA 24H] Valorizou! {asset_code} -> {status}: {percent}")

            # 🔴 SEGUNDO: ALERTA BASEADO NA VARIAÇÃO ENTRE AS DUAS ÚLTIMAS COLETAS (15 MINUTOS)
            if len(historico_valores[asset_code]) == 2:
                if abs(price_variation_percent) >= 10.0:
                    mensagem = (
                        f"[ALERTA 15 MIN] {asset_code} variou mais de 10% em 15 minutos!\n"
                        f"Δ: {price_variation} ({price_variation_percent}%)\n"
                        f"Preço Atual: {current_price}\n"
                        f"Variação 24h (site): {percent}"
                    )
                    await enviar_mensagem(mensagem)

        await asyncio.sleep(500)

asyncio.run(main())
