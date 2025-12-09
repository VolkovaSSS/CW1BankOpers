import os

import pandas as pd
from datetime import datetime

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import read_transactions_excel
from src.views import generate_page_main


def main():
    """Основная функция проекта"""

    file_xlsx = os.path.join(os.getcwd(), "data", "operations.xlsx")
    print("Привет! Добро пожаловать в программу работы \nс банковскими транзакциями.")

    main_menu = {"1": "1. Страница Главная", "2": "2. Сервис. Инвесткопилка", "3": "3. Отчеты"}
    print("Выберите необходимый пункт меню:")
    for value in main_menu.values():
        print(value)
    num_menu = input()

    if num_menu == "1":
        user_date = input("Введите дату выборки в формате: ГГГГ-ММ-ДД-ЧЧ:ММ:СС")
        try:
            date_obj = datetime.strptime(user_date, "%Y-%m-%d %H:%M:%S")
            print(f"Формируем отчёт по дату{date_obj}")
        except ValueError:
            print("Ошибка! Неверный формат даты.")
            return
        trans_data = generate_page_main(user_date)
        print(trans_data)
    elif num_menu == "2":
        user_round = int(input("введите округление целое число(10, 50, 100 и т.д.)"))
        user_date = input("Введите месяц выборки в формате: ГГГГ-ММ")
        try:
            date_obj = datetime.strptime(user_date, "%Y-%m")
            print(f"Возможные накопления в инвесткопилке в месяце: {date_obj.month}-{date_obj.year}")
        except ValueError:
            print("Ошибка! Неверный формат даты.")
            return
        df = read_transactions_excel(file_xlsx)
        transactions_list = df.to_dict(orient="records")
        investment_bank(user_date, transactions_list, user_round)
    elif num_menu == "3":
        user_category = input("введите категорию для выборки в отчёт")
        user_date = input("Введите дату окончания выборки в формате: ГГГГ-ММ-ДД-ЧЧ:ММ:СС")
        try:
            date_obj = datetime.strptime(user_date, "%Y-%m-%d %H:%M:%S")
            print(f"Формируем отчёт по {user_category} по дату{date_obj}")
        except ValueError:
            print("Ошибка! Неверный формат даты.")
            return
        df = pd.read_excel(file_xlsx, sheet_name="Отчет по операциям")
        spending_by_category(df, user_category, user_date)
    else:
        print("Ошибка! Не выбран пункт меню")
        return


if __name__ == "__main__":
    main()
