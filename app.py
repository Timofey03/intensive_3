import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.metrics import mean_absolute_error, mean_squared_error

GITHUB_TEST_XLSX_URL = "https://github.com/samoletpanfilov/reinforcement_task/raw/master/data/test.xlsx"
original_data = pd.read_excel(GITHUB_TEST_XLSX_URL)
predicted_data = pd.read_excel("test.xlsx")

original_data["dt"] = pd.to_datetime(original_data["dt"])
predicted_data["dt"] = pd.to_datetime(predicted_data["dt"])

merged_data = original_data[["dt", "Цена на арматуру"]].merge(
    predicted_data[["dt", "predicted_price", "N"]], on="dt", how="inner"
)

data_dict = merged_data.set_index("dt").to_dict("index")


def calculate_metrics():
    """Функция расчета метрик и вывода данных по выбранной дате"""
    selected_date = date_var.get()

    if not selected_date:
        messagebox.showerror("Ошибка", "Выберите дату!")
        return

    selected_date = pd.to_datetime(selected_date)

    if selected_date not in data_dict:
        messagebox.showerror("Ошибка", "Данные за выбранную дату отсутствуют!")
        return

    real_price = data_dict[selected_date]["Цена на арматуру"]
    predicted_price = data_dict[selected_date]["predicted_price"]
    predicted_weeks = data_dict[selected_date]["N"]

    real_price_label.config(text=f"Реальная цена: {real_price:.2f} руб.")
    predicted_price_label.config(text=f"Прогноз цены: {predicted_price:.2f} руб.")
    predicted_weeks_label.config(text=f"Рекомендованное количество недель для закупки: {predicted_weeks:.0f} недель")

    # Расчет метрик
    y_true = merged_data["Цена на арматуру"]
    y_pred_price = merged_data["predicted_price"]
    
    mae = mean_absolute_error(y_true, y_pred_price)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred_price))
    mape = np.mean(np.abs((y_true - y_pred_price) / y_true)) * 100

    mae_label.config(text=f"MAE: {mae:.2f}")
    rmse_label.config(text=f"RMSE: {rmse:.2f}")
    mape_label.config(text=f"MAPE: {mape:.2f}%")

    plt.figure(figsize=(12, 6))
    plt.plot(merged_data["dt"], y_true, label="Реальная цена", marker="o")
    plt.plot(merged_data["dt"], y_pred_price, label="Прогноз", marker="s", linestyle="dashed")
    plt.axvline(selected_date, color='r', linestyle='--', label="Выбранная дата")
    plt.scatter([selected_date], [real_price], color='blue', s=100, zorder=3, label="Выбранная реальная цена")
    plt.scatter([selected_date], [predicted_price], color='green', s=100, zorder=3, label="Выбранный прогноз цены")
    plt.xlabel("Дата")
    plt.ylabel("Цена")
    plt.title("📈 Сравнение прогноза и реальных данных")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.show()


root = tk.Tk()
root.title("Прогноз цены на арматуру")
root.geometry("500x450")

# Виджет выбора даты
tk.Label(root, text="Выберите дату:").pack(pady=5)
date_var = tk.StringVar()
date_combobox = ttk.Combobox(root, textvariable=date_var, values=merged_data["dt"].astype(str).tolist())
date_combobox.pack(pady=5)

# Кнопка расчета
calculate_btn = tk.Button(root, text="Показать данные", command=calculate_metrics)
calculate_btn.pack(pady=10)

# Метки для вывода результатов
real_price_label = tk.Label(root, text="Реальная цена: -")
real_price_label.pack(pady=5)

predicted_price_label = tk.Label(root, text="Прогноз цены: -")
predicted_price_label.pack(pady=5)

predicted_weeks_label = tk.Label(root, text="Рекомендованное количество недель: -")
predicted_weeks_label.pack(pady=5)

mae_label = tk.Label(root, text="MAE: -")
mae_label.pack(pady=5)

rmse_label = tk.Label(root, text="RMSE: -")
rmse_label.pack(pady=5)

mape_label = tk.Label(root, text="MAPE: -")
mape_label.pack(pady=5)

root.mainloop()
