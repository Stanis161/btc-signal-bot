import telebot
import os
import requests
import time
import threading

bot = telebot.TeleBot(os.environ['TELEGRAM_BOT_TOKEN'])
CHAT_ID = os.environ['CHAT_ID']

last_trend = None

def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url).json()
        return float(response.get("bitcoin", {}).get("usd", 0.0))
    except Exception as e:
        print(f"[ERROR] Не удалось получить цену BTC: {e}")
        return 0.0

def detect_trend(current, previous):
    if current > previous * 1.003:
        return "LONG"
    elif current < previous * 0.997:
        return "SHORT"
    else:
        return "NEUTRAL"

def trend_checker():
    global last_trend
    previous_price = get_btc_price()
    time.sleep(10)

    while True:
        current_price = get_btc_price()
        trend = detect_trend(current_price, previous_price)

        print(f"[LOG] Цена BTC: {current_price} | Тренд: {trend}")

        if trend != last_trend and trend != "NEUTRAL" and current_price > 0:
            last_trend = trend

            if trend == "LONG":
                msg = f"""⚡️ BTC Сигнал: ВХОД В ЛОНГ

Цена: ${current_price}
Причина: рост > 0.3%
TP: {round(current_price * 1.02, 2)}
SL: {round(current_price * 0.99, 2)}
"""
            elif trend == "SHORT":
                msg = f"""⚠️ BTC Сигнал: ВХОД В ШОРТ

Цена: ${current_price}
Причина: падение > 0.3%
TP: {round(current_price * 0.98, 2)}
SL: {round(current_price * 1.01, 2)}
"""

            bot.send_message(CHAT_ID, msg)

        previous_price = current_price
        time.sleep(60)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я онлайн и жду смены тренда по BTC.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

threading.Thread(target=trend_checker, daemon=True).start()
bot.polling()
