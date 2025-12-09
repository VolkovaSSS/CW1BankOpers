from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from src.services import investment_bank



def test_investment_bank(test_transactions: list[dict]) -> None:

    result = investment_bank("2021-11", test_transactions, 50)
    expected = 88.69
    assert result == expected

def test_investment_bank_empty(test_transactions: pd.DataFrame) -> None:

    result = investment_bank("2025-11", test_transactions, 50)
    expected = 0
    assert result == expected

