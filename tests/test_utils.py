import os
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from dotenv import load_dotenv

from src.utils import (
    form_greeting,
    get_card_info,
    get_currency_rates,
    get_period,
    get_stock_prices,
    get_top,
    get_user_settings,
    read_transactions_excel,
)

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_STOCKS = os.getenv("API_KEY")


@pytest.fixture
def file_user_settings():
    base_dir = Path(__file__).resolve().parents[1]
    return Path(f"{base_dir}/data/user_settings.json")


@pytest.mark.parametrize(
    "test_date, num_month, expected",
    [
        ("2021-11-04 15:51:50", 0, ["2021-11-01 00:00:00", "2021-11-04 23:59:59"]),
        ("2021-11-04 15:51:50", 3, ["2021-08-04 15:51:50", "2021-11-04 15:51:50"]),
    ],
)
def test_get_period(test_date, num_month, expected) -> None:
    result = get_period(test_date, num_month)
    assert result == expected


def test_get_period_wrong_date() -> None:
    with pytest.raises(Exception):
        get_period("2021/11/04 15:51:50")


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}',
)
def test_get_user_settings_file_correct(mock_data, file_user_settings):
    assert get_user_settings(file_user_settings) == {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }


@patch("builtins.open", new_callable=mock_open, read_data="AAPL, AMZN, GOOGL, MSFT, TSLA")
def test_get_user_settings_file_wrong(mock_data, file_user_settings):
    assert get_user_settings(file_user_settings) == {}


@patch("builtins.open", new_callable=mock_open, read_data="")
def test_get_user_settings_empty(mock_data, file_user_settings):
    assert get_user_settings(file_user_settings) == {}


def test_get_user_settings_no_file():
    """Тест ошибки чтения файла настроек пользователя"""
    with pytest.raises(Exception):
        get_user_settings("../data/no_file.json")


@patch("pandas.read_excel")
def test_read_transactions_excel(mock_read_excel, test_transactions, test_transactions_views) -> None:
    """Тест успешного чтения Excel файла c отбором по периоду"""

    period = ["2021-11-01 00:00:00", "2021-11-28 23:59:59"]
    mock_data = test_transactions
    mock_df = pd.DataFrame(mock_data)
    mock_read_excel.return_value = mock_df
    expected_result = test_transactions_views
    result = read_transactions_excel("../data/transactions_excel.xlsx", period)
    # pd.testing.assert_frame_equal(result.reset_index(drop=True),
    #                               expected_result.reset_index(drop=True))
    for col in expected_result.columns:
        assert expected_result[col].tolist() == result[col].tolist()


def test_read_transactions_excel_no_file() -> None:
    """Тест ошибки чтения файла Excel"""
    with pytest.raises(Exception):
        read_transactions_excel("../data/no_file.xlsx")


@pytest.mark.parametrize(
    "yy, mm, dd, hh, minutes, ss, expected",
    [
        (2025, 4, 22, 3, 0, 0, "Доброй ночи"),
        (2025, 4, 22, 6, 0, 0, "Доброе утро"),
        (2024, 1, 15, 14, 30, 0, "Добрый день"),
        (2024, 1, 15, 19, 30, 0, "Добрый вечер"),
    ],
)
@patch("src.utils.datetime")
def test_form_greeting(mock_datetime, yy, mm, dd, hh, minutes, ss, expected) -> None:

    current_time = datetime(yy, mm, dd, hh, minutes, ss)
    mock_datetime.now.return_value = current_time
    assert form_greeting() == expected


def test_get_card_info(test_transactions: pd.DataFrame) -> None:

    result = get_card_info(pd.DataFrame(test_transactions))
    expected = [
        {"last_digits": "5091", "total_spent": 5617.29, "cashback": 56.0},
        {"last_digits": "7197", "total_spent": 238.5, "cashback": 2.0},
    ]
    assert result == expected


def test_get_card_info_empty() -> None:

    result = get_card_info(pd.DataFrame())
    expected = []
    assert result == expected


def test_get_top(test_transactions: pd.DataFrame) -> None:

    result = get_top(pd.DataFrame(test_transactions), 3)
    expected = [
        {"amount": 5510.8, "category": "Аптеки", "date": "02.11.2021", "description": "Ситидрайв"},
        {"amount": 143.41, "category": "Каршеринг", "date": "15.10.2021", "description": "Ситидрайв"},
        {"amount": 95.09, "category": "Каршеринг", "date": "14.11.2021", "description": "Ситидрайв"},
    ]
    assert result == expected


def test_get_top_empty() -> None:

    result = get_top(pd.DataFrame())
    expected = []
    assert result == expected


@patch("requests.get")
def test_get_currency_rates(mock_get):

    currencies = ["USD", "EUR"]
    mock_get.return_value.json.return_value = {
        "base": "RUB",
        "date": "2025-12-09",
        "rates": {"EUR": 0.011199, "USD": 0.013041},
    }
    mock_get.return_value.status_code = 200
    result = get_currency_rates(currencies)

    expected = [{"currency": "EUR", "rate": 89.29}, {"currency": "USD", "rate": 76.68}]
    assert result == expected


def test_get_get_stock_prices1():

    stocks = ["AAPL", "GOOGL"]
    result = get_stock_prices(stocks)
    print(result)


@patch("requests.get")
def test_get_stock_prices(mock_get):

    stocks = ["AAPL"]
    mock_get.return_value.json.return_value = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "02. open": "278.1300",
            "03. high": "279.6693",
            "04. low": "276.1500",
            "05. price": "277.8900",
            "06. volume": "36406317",
            "07. latest trading day": "2025-12-08",
            "08. previous close": "278.7800",
            "09. change": "-0.8900",
            "10. change percent": "-0.3192%",
        }
    }
    # {'Global Quote': {'01. symbol': 'GOOGL', '02. open': '320.0500',
    #                   '03. high': '320.4400', '04. low': '311.2219',
    #                   '05. price': '313.7200', '06. volume': '33403895',
    #                   '07. latest trading day': '2025-12-08',
    #                   '08. previous close': '321.0551',
    #                   '09. change': '-7.3351',
    #                   '10. change percent': '-2.2847%'}}
    mock_get.return_value.status_code = 200
    result = get_stock_prices(stocks)
    expected = [{"price": 277.89, "stock": "AAPL"}]
    # expected = [{'price': 277.89, 'stock': 'AAPL'}, {'price': 313.72, 'stock': 'GOOGL'}]
    assert result == expected
    mock_get.assert_called_once_with(
        "https://www.alphavantage.co/query",
        params={"function": "GLOBAL_QUOTE", "symbol": "AAPL", "apikey": API_KEY_STOCKS},
        timeout=10,
    )
