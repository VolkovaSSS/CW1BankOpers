from typing import Optional

import pandas as pd
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from requests import RequestException
from dotenv import load_dotenv
import os
import logging


logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(os.getcwd(), "logs", "utils.logs", "w", "utf-8"))
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_period(date_str: str, num_months: int = 0, date_format: str = "%Y-%m-%d %H:%M:%S") -> list:
    """Возвращает период"""
    try:
        date_date = datetime.strptime(date_str, date_format)
    except Exception as ex:
        return []
    if num_months == 0:
        date_start = date_date.replace(day=1, hour=0, minute=0, second=0)
        date_end = date_date.replace(hour=23, minute=59, second=59)
    else:
        date_start = date_date - relativedelta(months=num_months)
        date_end = date_date

    return [date_start.strftime("%Y-%m-%d %H:%M:%S"), date_end.strftime("%Y-%m-%d %H:%M:%S")]


def get_user_settings(file_name: str) -> dict:
    """Возвращает словарь со списками настроек пользователя из файла json"""

    with open(file_name, "r") as file:
        try:
            user_settings = json.load(file)
        except json.JSONDecodeError:
            message = f"Ошибка формата файла: {file_name}"
            print(message)
            return {}
    return user_settings


def get_operations(data_file: str, period: list) -> pd.DataFrame:
    """Вызывает функцию чтения данных (пока только EXCEL)"""

    return read_transactions_excel(data_file, period)


def read_transactions_excel(data_file: str, period: Optional[list] = None) -> pd.DataFrame:
    """Загружает данные об операциях из Excel-файла data_file
    в интервале дат period:
    возвращает DataFrame
    Дата операции; Дата платежа; Номер карты; Статус; Сумма операции; Валюта операции
    Сумма платежа; Валюта платежа; Кэшбэк; Категория; MCC; Описание;
    df['Дата операции'] <= period[1] & df["Дата операции"] >= [period[0]
    Бонусы (включая кэшбэк); Округление на инвесткопилку; Сумма операции с округлением"""

    try:
        df = pd.read_excel(data_file, sheet_name="Отчет по операциям")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
        if period:
            df_filtered = df[(df["Дата операции"] <= period[1]) & (df["Дата операции"] >= period[0])]
            df_sorted = df_filtered.sort_values(by="Дата операции")
        else:
            df_sorted = df.sort_values(by="Дата операции")
        return df_sorted
    except Exception as ex:
        raise Exception(f"Ошибка при чтении файла: {ex}")


def form_greeting() -> str:
    """Формирует приветствие в зависимости от времени суток"""

    hour_num = datetime.now().hour
    if 6 < hour_num <= 11:
        return "Доброе утро"
    elif 11 < hour_num <= 18:
        return "Добрый день"
    elif 18 < hour_num <= 22:
        return "Добрый вечер"
    elif (0 <= hour_num < 6) or (22 < hour_num < 24):
        return "Доброй ночи"


def get_card_info(df: pd.DataFrame) -> list[dict]:
    """Формирует список словарей с данными по картам:
    возвращает список словарей:
    last_digits: str;
    общая сумма расходов total_spent: float;
    кешбэк (1 рубль на каждые 100 рублей) cashback: float"""

    filtered_df = df[df["Сумма платежа"] < 0]
    cards_group = filtered_df.groupby("Номер карты")["Сумма платежа"].sum()
    result = [
        {"last_digits": item[0][-4:], "total_spent": abs(item[1]), "cashback": round(item[1] // (-100), 2)}
        for item in cards_group.items()
    ]
    return result


def get_top_five(df: pd.DataFrame) -> list[dict]:
    """Формирует Топ-5 транзакций по сумме платежа
    возвращает список словарей: date: str вида 21.12.2021,
    amount: float  category: str,  description: str"""

    df_reduced = df[["Дата платежа", "Сумма платежа", "Сумма операции с округлением", "Категория", "Описание"]]
    filtered_df = df_reduced[df_reduced["Сумма платежа"] < 0]
    # filtered_df = df[df["Статус"] == 'FAILED']
    # filtered_df['СуммаМодуль'] = filtered_df['Сумма платежа'].map(lambda p: abs(p))
    top_5 = filtered_df.nlargest(5, "Сумма операции с округлением")
    top_5_list = []
    for index, row in top_5.iterrows():
        top_5_list.append(
            {
                "date": row["Дата платежа"],
                "amount": row["Сумма операции с округлением"],
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    return top_5_list


def get_currency_rates(currencies) -> list[dict]:
    """Получает курсы валют с сайта
    currency: str, rate: float"""

    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    base = "RUB"
    symbols = ",".join([i for i in currencies])
    url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base}"
    headers = {"apikey": API_KEY}
    payload = {}
    return []
    response = requests.get(url, headers=headers, data=payload)
    if response.status_code == 200:
        rates = response.json().get("rates", {})
        res_list = [{"currency": key, "rate": value} for key, value in rates.items()]
        return res_list
    else:
        raise RequestException(response.status_code)


def get_stock_prices(stocks: list) -> list:
    """Получает Стоимость выбранных акций из S&P500 с сайта
    stock: str, price: float"""

    load_dotenv()
    API_KEY_STOCKS = os.getenv("API_KEY")
    prices = []
    return prices
    for stock in stocks:
        try:
            url = f"https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": API_KEY_STOCKS}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "Global Quote" in data:
                price = float(data["Global Quote"]["05. price"])
                prices.append({"stock": stock, "price": price})
        except Exception as e:
            print(f"Ошибка для {stock}: {e}")

    return prices
