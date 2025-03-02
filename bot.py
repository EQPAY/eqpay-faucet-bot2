import telebot
import sqlite3
import time
import os

# === НАСТРОЙКИ ===
TOKEN = "7993600705:AAEmh3z9P6CF2I9CotUZMFdcK1kQ2c_Znvg"  # Замени на реальный токен от BotFather

bot = telebot.TeleBot(TOKEN)

# === БАЗА ДАННЫХ ===
conn = sqlite3.connect('faucet.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    eqpay_address TEXT,
    last_claim INTEGER
)
""")
conn.commit()

# === НАСТРОЙКИ FAUCET ===
CLAIM_AMOUNT = 0.1  # Количество EQPAY за раз
CLAIM_INTERVAL = 3600  # Раз в час (3600 секунд)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Привет! Отправь мне свой EQPAY-адрес для получения монет.")

@bot.message_handler(func=lambda message: len(message.text) > 25)
def set_address(message):
    user_id = message.chat.id
    eqpay_address = message.text.strip()

    cursor.execute("INSERT OR REPLACE INTO users (id, eqpay_address, last_claim) VALUES (?, ?, ?)",
                   (user_id, eqpay_address, 0))
    conn.commit()
    bot.send_message(user_id, f"Ваш EQPAY-адрес сохранен: {eqpay_address}\nИспользуйте /claim для получения монет.")

@bot.message_handler(commands=['claim'])
def claim(message):
    user_id = message.chat.id
    cursor.execute("SELECT eqpay_address, last_claim FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        bot.send_message(user_id, "Вы не указали EQPAY-адрес! Отправьте его мне сообщением.")
        return

    eqpay_address, last_claim = user
    current_time = int(time.time())

    if current_time - last_claim < CLAIM_INTERVAL:
        bot.send_message(user_id, "Вы можете получить монеты только раз в час! ⏳")
        return

    # Здесь должна быть отправка EQPAY (через API или бота-кошелька)
    bot.send_message(user_id, f"Вы получили {CLAIM_AMOUNT} EQPAY! 💰")

    cursor.execute("UPDATE users SET last_claim = ? WHERE id = ?", (current_time, user_id))
    conn.commit()

bot.polling()
