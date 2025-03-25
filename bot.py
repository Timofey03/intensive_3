import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# 📌 Настроим логирование
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 Загружаем данные
GITHUB_TEST_XLSX_URL = "https://github.com/samoletpanfilov/reinforcement_task/raw/master/data/test.xlsx"
original_data = pd.read_excel(GITHUB_TEST_XLSX_URL)
predicted_data = pd.read_excel("test.xlsx")

original_data["dt"] = pd.to_datetime(original_data["dt"])
predicted_data["dt"] = pd.to_datetime(predicted_data["dt"])

merged_data = original_data[["dt", "Цена на арматуру"]].merge(
    predicted_data[["dt", "predicted_price", "N"]], on="dt", how="inner"
)
data_dict = merged_data.set_index("dt").to_dict("index")

# 📌 Список доступных месяцев
available_months = merged_data["dt"].dt.to_period("M").unique()
available_months = [str(month) for month in available_months]

# 📌 Список доступных дат по месяцам
dates_by_month = {month: merged_data[merged_data["dt"].dt.to_period("M") == month]["dt"].dt.strftime("%d-%m-%Y").tolist() for month in available_months}

# 🔹 Функция обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton(month, callback_data=month)] for month in available_months]
    keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data="cancel")])  # Кнопка для отмены
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📅 Выберите месяц:", reply_markup=reply_markup)

# 🔹 Функция обработки выбора месяца
async def month_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_month = query.data

    # Создаем список доступных дат для выбранного месяца
    available_dates = dates_by_month[selected_month]

    keyboard = [[InlineKeyboardButton(date, callback_data=date)] for date in available_dates]
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_month")])  # Кнопка "Назад"
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(f"📅 Вы выбрали месяц {selected_month}. Выберите дату:", reply_markup=reply_markup)

# 🔹 Функция обработки выбора даты
async def date_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    selected_date = pd.to_datetime(query.data, format="%d-%m-%Y")

    if selected_date not in data_dict:
        await query.message.reply_text("❌ Данные за выбранную дату отсутствуют!")
        return

    real_price = data_dict[selected_date]["Цена на арматуру"]
    predicted_price = data_dict[selected_date]["predicted_price"]
    predicted_weeks = data_dict[selected_date]["N"]

    text = (
        f"📅 Дата: {query.data}\n"
        f"💰 Реальная цена: {real_price:.2f} руб.\n"
        f"📈 Прогноз цены: {predicted_price:.2f} руб.\n"
        f"🛒 Рекомендовано закупить на: {predicted_weeks:.0f} недель."
    )

    await query.message.reply_text(text)
    
    # Отправка графика
    await send_plot(update, context, selected_date)

# 🔹 Функция построения графика
async def send_plot(update: Update, context: CallbackContext, selected_date: pd.Timestamp) -> None:
    y_true = merged_data["Цена на арматуру"]
    y_pred_price = merged_data["predicted_price"]

    plt.figure(figsize=(12, 6))
    plt.plot(merged_data["dt"], y_true, label="Реальная цена", marker="o")
    plt.plot(merged_data["dt"], y_pred_price, label="Прогноз", marker="s", linestyle="dashed")
    plt.axvline(selected_date, color='r', linestyle='--', label="Выбранная дата")
    plt.scatter([selected_date], [data_dict[selected_date]["Цена на арматуру"]], color='blue', s=100, zorder=3)
    plt.scatter([selected_date], [data_dict[selected_date]["predicted_price"]], color='green', s=100, zorder=3)
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.title("📈 Сравнение прогноза и реальных данных")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)

    # Сохранение графика в байтовый поток
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=buf)
    buf.close()

# 🔹 Обработчик кнопки "Назад"
async def back(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    if query.data == "back_month":  # Если нажата кнопка "Назад" на шаге выбора даты
        keyboard = [[InlineKeyboardButton(month, callback_data=month)] for month in available_months]
        keyboard.append([InlineKeyboardButton("❌ Отменить", callback_data="cancel")])  # Кнопка для отмены
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("📅 Выберите месяц:", reply_markup=reply_markup)

    elif query.data == "cancel":  # Если нажата кнопка "Отменить"
        await query.message.reply_text("❌ Операция отменена.")

# 🔹 Запуск бота
def main():
    TOKEN = "8000005967:AAH4nDUrBQ1mJLN1zb0XkBNbOvDS6t0_4mA"  # 🔥 Вставь свой токен

    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(month_button, pattern="^(\d{4}-\d{2})$"))
    application.add_handler(CallbackQueryHandler(date_button, pattern="^\d{2}-\d{2}-\d{4}$"))
    application.add_handler(CallbackQueryHandler(back))  # Добавляем обработчик для кнопки "Назад"

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
