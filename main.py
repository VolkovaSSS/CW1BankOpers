import os
import pandas as pd

from src.views import generate_page_main
from src.services import investment_bank
from src.reports import spending_by_category
from src.utils import read_transactions_excel

def main():
    """Основная функция проекта"""

    file_xlsx = os.path.join(os.getcwd(), "data", "operations.xlsx")
    print('Привет! Добро пожаловать в программу работы \nс банковскими транзакциями.')

    main_menu = {'1': '1. Страница Главная',
                 '2': '2. Сервис. Инвесткопилка',
                 '3': '3. Отчеты'}
    print('Выберите необходимый пункт меню:')
    for value in main_menu.values():
        print(value)
    num_menu = input()


    if num_menu == '1':
        trans_data = generate_page_main("2021-12-04 15:51:50")
        print(trans_data)
    elif num_menu == '2':
        df = read_transactions_excel(file_xlsx)
        transactions_list = df.to_dict(orient='records')
        investment_bank("2021-11", transactions_list, 50)
    elif num_menu == '3':
        df = pd.read_excel(file_xlsx, sheet_name="Отчет по операциям")
        spending_by_category(df, 'Каршеринг', "2021-12-04 15:51:50")
    else:
        print("Ошибка! Не выбран пункт меню")
        return

if __name__ == '__main__':
    main()