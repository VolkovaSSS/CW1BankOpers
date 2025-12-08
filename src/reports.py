import json
import logging
import os
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

from src.utils import get_period

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
BASE_DIR = Path(__file__).resolve().parent.parent
file_handler = logging.FileHandler(BASE_DIR / "logs" / "reports.log", "w", "utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


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
                logger.info(f"запись данных в файл {file_name}")
                with open(name_f, "w", encoding="utf-8") as f:
                    f.write(result)
            except Exception as ex:
                message = f"✗ Ошибка при записи файла: {ex}"
                logger.error(message)
                print(message)

            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category_: str, date: Optional[str] = None) -> str:
    """Возвращает траты по заданной категории
    за последние три месяца (от переданной даты)"""

    logger.info(f"получение данных по категории {category_}")

    if not date:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    period = get_period(date, num_months=3)

    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    filtered_data = transactions[
        (transactions["Дата операции"] <= period[1])
        & (transactions["Дата операции"] >= period[0])
        & (transactions["Категория"] == category_)
        & (transactions["Сумма платежа"] < 0)
    ]
    if filtered_data.empty:
        print(f"По категории {category_} нет данных")
    result = filtered_data.to_json(orient="records", indent=4, force_ascii=False)
    logger.info(f"Данные по категории получены {category_}")
    return result
