import logging
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(BASE_DIR / "logs" / "services.log", "w", "utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Возвращает сумму, которую удалось бы отложить в Инвесткопилку"""

    logger.info("Расчет инвесткопилки")
    if limit == 0:
        total = 0.00
        print(total)
        return round(total, 2)

    month_obj = datetime.strptime(month, "%Y-%m")
    df = pd.DataFrame(transactions)
    if df.empty:
        return 0.00
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    df = df[
        (df["Дата операции"].dt.year == month_obj.year)
        & (df["Дата операции"].dt.month == month_obj.month)
        & (df["Сумма платежа"] < 0)
    ]
    df["Округление на инвесткопилку"] = df["Сумма платежа"].apply(lambda x: ceil(abs(x) / limit) * limit - abs(x))
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    total = round(df["Округление на инвесткопилку"].sum(), 2)
    print(total)
    return round(total, 2)
