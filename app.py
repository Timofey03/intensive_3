import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Загружаем модель
model = joblib.load("lightgbm_model.pkl")

# Загружаем данные
GITHUB_TEST_XLSX_URL = "test.xlsx"
data = pd.read_excel(GITHUB_TEST_XLSX_URL)

# Функция для предсказания
def predict_price():
    selected_date = date_entry.get()
    
    if selected_date:
        try:
            date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
            row = data[data["dt"] == date_obj]
            
            if row.empty:
                result_label.config(text="⚠ Дата отсутствует в данных")
                return
            
            # Формируем входные данные для модели
            features = row.drop(columns=["dt", "Цена на арматуру"]).values
            predicted_price = model.predict(features)[0]

            real_price = row["Цена на арматуру"].values[0]
            weeks_recommendation = int(abs(real_price - predicted_price) // 1000)  # Условная формула рекомендации

            # Обновляем текст на экране
            result_label.config(text=(
                f"📅 Дата: {selected_date}\n"
                f"✔ Реальная цена: {real_price:.2f} руб/т\n"
                f"🔮 Прогноз: {predicted_price:.2f} руб/т\n"
                f"📌 Рекомендация: {weeks_recommendation} недель"
            ))

            # Построение графика
            plot_graph(selected_date, real_price, predicted_price)

        except ValueError:
            result_label.config(text="⚠ Неверный формат даты (должно быть YYYY-MM-DD)")

# Функция построения графика
def plot_graph(selected_date, real_price, predicted_price):
    fig, ax = plt.subplots(figsize=(8, 4))

    # Исторические данные
    ax.plot(data["dt"], data["Цена на арматуру"], label="Реальные значения", marker="o", color="blue")
    
    # Прогноз
    ax.scatter([pd.to_datetime(selected_date)], [predicted_price], color="red", marker="s", label="Прогноз")
    
    ax.set_xlabel("Дата")
    ax.set_ylabel("Цена на арматуру (руб/т)")
    ax.set_title("📈 Сравнение реальных и предсказанных значений")
    ax.legend()
    ax.grid(True)

    # Отображение графика в Tkinter
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Создание GUI
window = tk.Tk()
window.title("Прогноз цен на арматуру")
window.geometry("600x500")

# Заголовок
label = tk.Label(window, text="Прогноз цен на арматуру", font=("Arial", 14))
label.pack(pady=10)

# Поле для выбора даты
date_label = tk.Label(window, text="Выберите дату:")
date_label.pack()

date_entry = ttk.Entry(window)
date_entry.pack()

# Кнопка предсказания
predict_button = tk.Button(window, text="Показать прогноз", command=predict_price)
predict_button.pack(pady=10)

# Результат
result_label = tk.Label(window, text="", font=("Arial", 12), fg="green")
result_label.pack()

# Кнопка построения графика
graph_button = tk.Button(window, text="Построить график", command=lambda: plot_graph(date_entry.get(), 0, 0))
graph_button.pack(pady=10)

window.mainloop()
