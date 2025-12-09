import json
import pytest
from unittest.mock import patch

from src.views import generate_page_main


@patch("src.views.get_stock_prices")
@patch("src.views.get_currency_rates")
@patch("src.views.get_top")
@patch("src.views.get_card_info")
@patch("src.views.form_greeting")
def test_generate_page_main(mock_greeting, mock_cards, mock_top, mock_currencies, mock_stocks) -> None:

    mock_greeting.return_value = "Доброй ночи"
    mock_cards.return_value = [
        {"last_digits": "5091", "total_spent": 5617.29, "cashback": 56.0},
        {"last_digits": "7197", "total_spent": 238.5, "cashback": 2.0},
    ]
    mock_top.return_value = [
        {"amount": 5510.8, "category": "Аптеки", "date": "02.11.2021", "description": "Ситидрайв"},
        {"amount": 143.41, "category": "Каршеринг", "date": "15.10.2021", "description": "Ситидрайв"}
    ]
    mock_currencies.return_value = [{"currency": "EUR", "rate": 89.29}, {"currency": "USD", "rate": 76.68}]
    mock_stocks.return_value = [{"price": 277.89, "stock": "AAPL"}]
    result = generate_page_main('2021-11-15 10:00:00')
    assert '"greeting": "Доброй ночи"' in result
    assert '"last_digits": "5091"' in result
    assert '"top_transactions":' in result
    assert 'currency_rates":' in result
    assert 'stock_price":' in result





