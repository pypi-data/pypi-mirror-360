import os
import pytest

from matterlab_balances import SartoriusBalance


@pytest.fixture
def mock_serial(mocker):
    mock_serial = mocker.patch("matterlab_serial_device.serial_device.serial.Serial")
    mock_serial_instance = mock_serial.return_value
    yield mock_serial_instance


@pytest.fixture
def balance_fixture(mock_serial):
    port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"
    return SartoriusBalance(com_port=port)


# Test _weigh method
@pytest.mark.parametrize(
    "query_return_value, expected_stable, expected_weight",
    [
        ("0.123", True, 0.123),
        ("- 0.123", True, -0.123),
    ],
)
def test_weigh_stable_reading(balance_fixture, mocker, query_return_value, expected_stable, expected_weight):
    mocker.patch.object(balance_fixture, "query", return_value=f"x {query_return_value} {balance_fixture.units}")
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    stable, weight = balance_fixture._weigh()
    assert stable == expected_stable
    assert weight == expected_weight

    mock_logger.assert_called_once_with(f"Stable: {expected_stable}, Weight: {expected_weight} {balance_fixture.units}.")


@pytest.mark.parametrize(
    "query_return_value, expected_stable, expected_weight",
    [
        ("0.123", False, 0.123),
        ("- 0.123", False, -0.123),
    ],
)
def test_weigh_unstable_reading(balance_fixture, mocker, query_return_value, expected_stable, expected_weight):
    mocker.patch.object(balance_fixture, "query", return_value=f"x {query_return_value}")
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    stable, weight = balance_fixture._weigh()
    assert stable == expected_stable
    assert weight == expected_weight

    mock_logger.assert_called_once_with(f"Stable: {expected_stable}, Weight: {expected_weight} {balance_fixture.units}.")


# Test _weigh_stable method
def test_weigh_stable_immediately(balance_fixture, mocker):
    # _weigh returns a stable weight immediately
    mocker.patch.object(balance_fixture, "query", return_value=f"x 0.123 {balance_fixture.units}")
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    weight = balance_fixture._weigh_stable()
    assert weight == 0.123

    mock_logger.assert_called_once_with(f"Stable: {True}, Weight: {0.123} {balance_fixture.units}.")


def test_weigh_stable_within_max_tries(balance_fixture, mocker):
    max_tries = 3

    # _weigh returns unstable weights first, then a stable weight
    side_effects = ["x 0.123", "x 0.123", f"x 0.123 {balance_fixture.units}"]
    mocker.patch.object(balance_fixture, "query", side_effect=side_effects)
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    weight = balance_fixture._weigh_stable(max_tries=max_tries, wait_time=0.1)

    # Assert weight is correct
    assert weight == 0.123

    # Assert query was called 3 times
    assert balance_fixture.query.call_count == max_tries

    # Assert logger was called
    expected_logger_calls = [
        mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
        mocker.call("Weight not stable, waiting for 0.1 seconds."),
        mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
        mocker.call("Weight not stable, waiting for 0.1 seconds."),
        mocker.call(f"Stable: {True}, Weight: {0.123} {balance_fixture.units}."),
    ]
    mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


def test_weigh_stable_exceeding_max_tries(balance_fixture, mocker):
    # _weigh returns unstable weights for max_tries and then a stable weight
    max_tries = 3
    side_effects = ["x 0.123"] * max_tries + [f"x 0.123 {balance_fixture.units}"]
    mocker.patch.object(balance_fixture, "query", side_effect=side_effects)
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    # Assert that an IOError is raised after max_tries
    with pytest.raises(IOError, match="Could not get a stable balance reading."):
        balance_fixture._weigh_stable(max_tries=max_tries, wait_time=0.1)

    # Assert query was called 3 times
    assert balance_fixture.query.call_count == max_tries

    # Assert logger was called
    expected_logger_calls = [
        mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
        mocker.call("Weight not stable, waiting for 0.1 seconds."),
        mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
        mocker.call("Weight not stable, waiting for 0.1 seconds."),
        mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
        mocker.call("Weight not stable, waiting for 0.1 seconds."),
    ]
    mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


def test_weigh_stable_timeout(balance_fixture, mocker):
    max_tries = 3

    mocker.patch.object(balance_fixture, "query", return_value="x 0.123")
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    with pytest.raises(IOError, match="Could not get a stable balance reading."):
        balance_fixture._weigh_stable(max_tries=max_tries, wait_time=0.1)

        # Assert logger was called
        expected_logger_calls = [
            mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
            mocker.call("Weight not stable, waiting for 0.1 seconds."),
            mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
            mocker.call("Weight not stable, waiting for 0.1 seconds."),
            mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
            mocker.call("Weight not stable, waiting for 0.1 seconds."),
        ]
        mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


# Test weigh method
def test_weigh_method_unstable(balance_fixture, mocker):
    mocker.patch.object(balance_fixture, "query", return_value="x 0.123")
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    weight = balance_fixture.weigh(stable=False)
    assert weight == 0.123

    # Assert logger was called
    expected_logger_calls = [
        mocker.call(f"Stable: {False}, Weight: {0.123} {balance_fixture.units}."),
        mocker.call(f"Balance reading: {weight} {balance_fixture.units}."),
    ]
    mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


def test_weigh_method_stable(balance_fixture, mocker):
    mocker.patch.object(balance_fixture, "_weigh_stable", return_value=0.123)
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    weight = balance_fixture.weigh(stable=True)
    assert weight == 0.123

    mock_logger.assert_called_once_with(f"Balance reading, stable: {weight} {balance_fixture.units}.")


# Test _tare method
def test_tare(balance_fixture, mocker):
    mocker.patch.object(balance_fixture, "write")
    balance_fixture._tare()
    balance_fixture.write.assert_called_once_with("\x1bT\r\n")


# Test _tare_stable method
def test_tare_stable_immediately(balance_fixture, mocker):
    # _tare immediately results in stable tare
    mocker.patch.object(balance_fixture, "_weigh_stable", return_value=0.0)
    mocker.patch.object(balance_fixture, "_tare")
    result = balance_fixture._tare_stable()
    assert result is True
    balance_fixture._tare.assert_called_once()


def test_tare_stable_within_max_tries(balance_fixture, mocker):
    # _tare results in stable tare within max_tries
    side_effects = [0.5, 0.5, 0.0]
    mocker.patch.object(balance_fixture, "_weigh_stable", side_effect=side_effects)
    mocker.patch.object(balance_fixture, "_tare")
    result = balance_fixture._tare_stable(max_tries=3, wait_time=0.1, tolerance=0.01)
    assert result is True
    assert balance_fixture._tare.call_count == 3


def test_tare_stable_timeout(balance_fixture, mocker):
    max_tries = 3

    # _tare does not result in stable tare within max_tries
    side_effects = [0.5] * max_tries
    mocker.patch.object(balance_fixture, "_weigh_stable", side_effect=side_effects)
    mocker.patch.object(balance_fixture, "_tare")

    with pytest.raises(IOError, match="Could not get the balance to tare reliably."):
        balance_fixture._tare_stable(max_tries=max_tries, wait_time=0.1, tolerance=0.01)

    assert balance_fixture._tare.call_count == max_tries + 1


def test_tare_stable_exceeding_max_tries(balance_fixture, mocker):
    # _tare exceeds max_tries but eventually results in stable tare
    max_tries = 3
    side_effects = [0.5] * max_tries + [0.0]
    mocker.patch.object(balance_fixture, "_weigh_stable", side_effect=side_effects)
    mocker.patch.object(balance_fixture, "_tare")

    with pytest.raises(IOError, match="Could not get the balance to tare reliably."):
        balance_fixture._tare_stable(max_tries=max_tries, wait_time=0.1, tolerance=0.01)

    assert balance_fixture._tare.call_count == max_tries + 1


@pytest.mark.parametrize(
    "stable, kwargs, expected_method, expected_calls",
    [
        (False, {}, "_tare", 1),
        (True, {}, "_tare_stable", 1),
        (True, {"max_tries": 5, "wait_time": 2, "tolerance": 0.05}, "_tare_stable", 1),
    ],
)
def test_tare_method(balance_fixture, mocker, stable, kwargs, expected_method, expected_calls):
    mock_method = mocker.patch.object(balance_fixture, expected_method)
    mock_logger = mocker.patch.object(balance_fixture.logger, "info")

    balance_fixture.tare(stable=stable, **kwargs)

    assert mock_method.call_count == expected_calls

    if kwargs:
        mock_method.assert_called_once_with(**kwargs)
    else:
        mock_method.assert_called_once()

    mock_logger.assert_called_once_with("Balance tared.")
