# -*- coding: utf-8 -*-
"""
Telegram-бот для розрахунку накладних.

Як користуватись у Telegram (після запуску бота):
    Коля
    Какао 2
    160 26
    Жл 42

Бот сам знайде ціну кожного товару у прайсі, порахує суму по рядку
і загальну суму, і надішле готовий текст накладної у тому ж форматі,
що ви використовуєте зараз — просто скопіюйте його у папку "Збережені".

---------------------------------------------------------------------------
НАЛАШТУВАННЯ (зробити один раз):

1. Встановіть бібліотеку:
       pip install python-telegram-bot --upgrade

2. Створіть бота через @BotFather у Telegram:
   - Напишіть @BotFather команду /newbot
   - Дайте боту ім'я та юзернейм
   - BotFather видасть токен виду: 123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   - Вставте цей токен нижче замість "ВАШ_ТОКЕН_СЮДИ"

3. Заповніть/перевірте прайс-лист нижче (розділ PRICES) — 
   якщо ціна товару зміниться, правте тільки тут.

4. Запустіть файл:
       python invoice_bot.py

5. Напишіть своєму боту в Telegram що завгодно — і він відповість.
---------------------------------------------------------------------------
"""

import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ===================== НАЛАШТУВАННЯ =====================

BOT_TOKEN = "8755907348:AAEHMwALFKPWaOA6c2XMJbOn3hoFwJc0pKo"

# Прайс-лист: назва товару (як його писати в повідомленні) -> ціна за одиницю
# Щоб додати новий товар — просто допишіть рядок за зразком: "назва": ціна,
# Щоб змінити ціну — поміняйте число після двокрапки.
PRICES = {
    # старі позиції
    "какао": 31,
    "160": 18,
    "грибна": 60,
    "80": 60,
    "250": 44,
    "170": 31,
    "400": 250,
    "200": 150,
    "магнетік": 64,
    "жл": 12,
    "пчм": 7,
    "пчг": 12,
    "зерно": 490,
    "мак" : 110,

    # Мівіна
    "мівіна куряча 80": 9,
    "мівіна грибна 80": 10.5,
    "мівіна куряча 160": 19,

    # 10 овочів (у дужках вказано, скільки шт у блоці — просто для довідки)
    "10 овочів 60": 12,     # блок 20 шт
    "10 овочів 170": 31,    # блок 8 шт
    "10 овочів 250": 44,    # блок 7 шт

    # Якобс розчиний
    "якось розчинний 120": 120,
    "якось розчинний 200": 150,
    "якось розчинний 400": 250,
}

# ===================== ЛОГІКА БОТА =====================

logging.basicConfig(level=logging.INFO)


def format_number(n: float) -> str:
    """Показує число без зайвих нулів (31, але 10.5 лишається 10.5)."""
    if float(n).is_integer():
        return str(int(n))
    return str(n).rstrip("0").rstrip(".")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    if not lines:
        return

    # Перший рядок - ім'я клієнта, якщо в ньому немає цифр
    client_name = None
    item_lines = lines
    if not re.search(r"\d", lines[0]):
        client_name = lines[0]
        item_lines = lines[1:]

    result_lines = []
    total = 0.0
    errors = []

    for line in item_lines:
        # Формат: "Назва Кількість" (можлива кома як десятковий роздільник)
        match = re.match(r"^(.+?)\s+([\d.,]+)$", line)
        if not match:
            errors.append(f'Не зрозумів рядок: "{line}"')
            continue

        raw_name, qty_str = match.groups()
        name_key = raw_name.strip().lower()
        qty = float(qty_str.replace(",", "."))

        if name_key not in PRICES:
            errors.append(f'Немає в прайсі: "{raw_name.strip()}" — вкажіть ціну вручну')
            continue

        price = PRICES[name_key]
        sum_line = price * qty
        total += sum_line

        result_lines.append(
            f"{raw_name.strip()} {format_number(qty)}х{format_number(price)}={format_number(sum_line)}"
        )

    reply_parts = []
    if client_name:
        reply_parts.append(client_name)
    reply_parts.extend(result_lines)
    if result_lines:
        reply_parts.append(f"Сума {format_number(total)}")

    if errors:
        reply_parts.append("")
        reply_parts.append("⚠️ " + "\n⚠️ ".join(errors))

    await update.message.reply_text("\n".join(reply_parts) if reply_parts else "Не вдалось розпізнати накладну.")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущено. Натисніть Ctrl+C щоб зупинити.")
    app.run_polling()


if __name__ == "__main__":
    main()
