import pandas as pd
from typing import Any, Callable, Optional
from functools import wraps
import json
from datetime import datetime
import os
from src.utils import get_period


def save_report(report_file: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Сохраняет результата выполнения функции в файл"""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            name_f = report_file
            if not name_f:
                date_str = datetime.now().strftime("%Y%m%d")
                file_name = f"{func.__name__}_{date_str}.json"
                name_f = os.path.join(os.getcwd(), "data", file_name)
            try:
                with open(name_f, "w", encoding="utf-8") as f:
                    f.write(result)
                # with open(name_f, 'w') as file:
                #     json.dump(result, file, indent=4)
                # result.to_json(name_f, orient="records", indent=4, lines=True, force_ascii=False)
            except Exception as ex:
                print(f"✗ Ошибка при записи файла: {ex}")

            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category_: str, date: Optional[str] = None) -> json:
    """Возвращает траты по заданной категории
    за последние три месяца (от переданной даты)"""

    if not date:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    period = get_period(date, num_months=3)
    print(type(transactions))

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_data = transactions[
        (transactions["Дата операции"] <= period[1])
        & (transactions["Дата операции"] >= period[0])
        & (transactions["Категория"] == category_)
        & (transactions["Сумма платежа"] < 0)
    ]

    result = filtered_data.to_json(orient="records", indent=4, force_ascii=False)
    return result
