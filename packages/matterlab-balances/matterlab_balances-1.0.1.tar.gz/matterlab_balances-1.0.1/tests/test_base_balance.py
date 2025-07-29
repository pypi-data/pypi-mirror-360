import pytest
from matterlab_balances import Balance


class MockBalance(Balance):
    def weigh(self, stable: bool = True) -> float:
        return 42.0

    def tare(self, stable: bool = True):
        pass


def test_balance_abstract_methods():
    with pytest.raises(TypeError):
        Balance()  # This should raise TypeError because Balance has abstract methods


def test_mock_balance_instantiation():
    mock_balance = MockBalance()
    assert isinstance(mock_balance, Balance)


def test_mock_balance_weigh():
    mock_balance = MockBalance()
    weight = mock_balance.weigh()
    assert weight == 42.0


def test_mock_balance_tare():
    mock_balance = MockBalance()
    # Since tare() method does nothing, just ensure it can be called without error
    mock_balance.tare()
