import json
import os
from pathlib import Path
import pandas as pd
from src.reports import spending_by_category, save_report


BASE_DIR = Path(__file__).resolve().parent.parent

def test_spending_by_category(test_transactions: pd.DataFrame) -> None:

    result = spending_by_category(pd.DataFrame(test_transactions), "Каршеринг", "2021-12-04 15:51:50")
    expected = """[
    {
        "Дата операции":"23.11.2021 18:15:54",
        "Дата платежа":"23.11.2021",
        "Номер карты":"*5091",
        "Статус":"OK",
        "Сумма операции":-10.33,
        "Сумма платежа":-10.33,
        "Категория":"Каршеринг",
        "Описание":"Ситидрайв",
        "Округление на инвесткопилку":0,
        "Сумма операции с округлением":10.33
    },
    {
        "Дата операции":"15.10.2021 12:10:47",
        "Дата платежа":"15.10.2021",
        "Номер карты":"*7197",
        "Статус":"OK",
        "Сумма операции":-143.41,
        "Сумма платежа":-143.41,
        "Категория":"Каршеринг",
        "Описание":"Ситидрайв",
        "Округление на инвесткопилку":0,
        "Сумма операции с округлением":143.41
    },
    {
        "Дата операции":"14.11.2021 14:26:10",
        "Дата платежа":"14.11.2021",
        "Номер карты":"*5091",
        "Статус":"OK",
        "Сумма операции":-95.09,
        "Сумма платежа":-95.09,
        "Категория":"Каршеринг",
        "Описание":"Ситидрайв",
        "Округление на инвесткопилку":0,
        "Сумма операции с округлением":95.09
    },
    {
        "Дата операции":"30.11.2021 12:34:17",
        "Дата платежа":"30.11.2021",
        "Номер карты":"*7197",
        "Статус":"OK",
        "Сумма операции":-95.09,
        "Сумма платежа":-95.09,
        "Категория":"Каршеринг",
        "Описание":"Ситидрайв",
        "Округление на инвесткопилку":0,
        "Сумма операции с округлением":95.09
    }
]"""
    assert result == expected

def test_spending_by_category_empty(test_transactions: pd.DataFrame) -> None:

    result = spending_by_category(pd.DataFrame(test_transactions), "Авиа", "2021-12-04 15:51:50")
    expected = '[\n\n]'
    assert result == expected


def test_save_report():
    @save_report("test_result.json")
    def simple_json(test_dict: {dict}) -> str:
        return json.dumps(test_dict, ensure_ascii=False)

    simple_json({'Тест': 'Успешный результат теста'})
    file_path = BASE_DIR / "data" / "test_result.json"
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            expected_text = file.read()
        assert "Успешный результат теста" in expected_text
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

