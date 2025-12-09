import json
from pathlib import Path

from src.utils import (
    form_greeting,
    get_card_info,
    get_currency_rates,
    get_operations,
    get_period,
    get_stock_prices,
    get_top,
    get_user_settings,
)


def generate_page_main(date_for_report: str) -> str:
    """принимает строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    возвращает JSON-ответ для страницы ГЛАВНАЯ"""

    BASE_DIR = Path(__file__).resolve().parent.parent
    file_settings = BASE_DIR / "data"/ "user_settings.json"
    user_currencies = get_user_settings(file_settings).get("user_currencies", [])
    user_stocks = get_user_settings(file_settings).get("user_stocks", [])
    file_xlsx = BASE_DIR / "data"/ "operations.xlsx"
    data_period = get_period(date_for_report)
    df = get_operations(file_xlsx, data_period)

    greeting = form_greeting()
    cards = get_card_info(df)
    top_transactions = get_top(df, 5)
    currency_rates = get_currency_rates(user_currencies)
    stock_price = get_stock_prices(user_stocks)

    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_price": stock_price,
    }
    name_f = Path(f"{BASE_DIR}/data/report_file.json")
    result = json.dumps(data, ensure_ascii=False, indent=4)
    return result
