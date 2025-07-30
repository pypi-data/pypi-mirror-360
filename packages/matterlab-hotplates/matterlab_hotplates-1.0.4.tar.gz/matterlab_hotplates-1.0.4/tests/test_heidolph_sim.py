import os
import pytest

from matterlab_hotplates.heidolph_hotplate import HeidolphHotplate


@pytest.fixture
def mock_serial(mocker):
    mock_serial = mocker.patch("matterlab_serial_device.serial_device.serial.Serial")
    mock_serial_instance = mock_serial.return_value
    yield mock_serial_instance


@pytest.fixture
def hotplate_fixture(mock_serial):
    port = "/dev/ttyUSB0" if os.name == "posix" else "COM1"
    return HeidolphHotplate(com_port=port)


def test_write_hotplate(hotplate_fixture, mocker):
    mock_write = mocker.patch.object(hotplate_fixture, "write")
    hotplate_fixture._write_hotplate("test")
    mock_write.assert_called_once_with("test\r\n")


def test_query_hotplate(hotplate_fixture, mocker):
    mock_query = mocker.patch.object(hotplate_fixture, "query")
    hotplate_fixture._query_hotplate("test")
    mock_query.assert_called_once_with(write_command="test\r\n", remove_from_end=2, read_delay=0.5)


@pytest.mark.parametrize(
    "temp, switch_cmd, switch_status, log_message",
    [
        (0, HeidolphHotplate._heat_stop, False, "Stop heating."),
        (100, HeidolphHotplate._heat_start, True, "Start heating."),
        (200, HeidolphHotplate._heat_start, True, "Start heating."),
    ],
)
def test_set_temp(hotplate_fixture, mocker, temp, switch_cmd, log_message, switch_status):
    mock_write = mocker.patch.object(hotplate_fixture, "_write_hotplate")
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture.temp = temp
    assert hotplate_fixture.target_temp == temp
    assert hotplate_fixture._heat_switch == switch_status

    # Define the expected call sequence for _write_hotplate
    expected_write_calls = [mocker.call(f"{hotplate_fixture._temp_set} {temp:.1f}"), mocker.call(switch_cmd)]
    mock_write.assert_has_calls(expected_write_calls, any_order=False)

    # Define the expected call sequence for logger.info
    expected_logger_calls = [
        mocker.call(f"Target temperature set to {temp:.1f}."),
        mocker.call(log_message),
    ]
    mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


def test_set_temp_raises_type_error(hotplate_fixture):
    with pytest.raises(TypeError, match="Temperature must be float or int!"):
        hotplate_fixture.temp = "invalid"


@pytest.mark.parametrize(
    "temp, expected_error_message",
    [(-10, "Temperature out of range: min 0, max 200!"), (250, "Temperature out of range: min 0, max 200!")],
)
def test_set_temp_raises_value_error(hotplate_fixture, temp, expected_error_message):
    with pytest.raises(ValueError, match=expected_error_message):
        hotplate_fixture.temp = temp


@pytest.mark.parametrize(
    "temp, query_cmd",
    [
        (50, HeidolphHotplate._temp_query),
        (100, HeidolphHotplate._temp_query),
    ],
)
def test_get_temp(hotplate_fixture, mocker, temp, query_cmd):
    mock_query = mocker.patch.object(hotplate_fixture, "_query_hotplate", return_value=str(temp))
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    assert hotplate_fixture.temp == temp
    mock_query.assert_called_once_with(hotplate_fixture._temp_query)
    mock_logger.assert_called_once_with(f"Temperature reading on probe is {temp:.1f}.")


@pytest.mark.parametrize(
    "heat_switch, switch_cmd, log_msg",
    [(True, HeidolphHotplate._heat_start, "Start heating."), (False, HeidolphHotplate._heat_stop, "Stop heating.")],
)
def test_set_heat_switch(hotplate_fixture, mocker, heat_switch, switch_cmd, log_msg):
    mock_write = mocker.patch.object(hotplate_fixture, "_write_hotplate")
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture._heat_switch = heat_switch
    assert hotplate_fixture._heat_switch_status == heat_switch

    mock_write.assert_called_once_with(switch_cmd)
    mock_logger.assert_called_once_with(log_msg)


@pytest.mark.parametrize("heat_switch_status", [True, False])
def test_get_heat_switch(hotplate_fixture, mocker, heat_switch_status):
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture._heat_switch_status = heat_switch_status
    assert hotplate_fixture._heat_switch == heat_switch_status
    mock_logger.assert_called_once_with(f"Heat switch is {heat_switch_status}.")


@pytest.mark.parametrize(
    "rpm, switch_cmd, switch_status, log_message",
    [
        (0, HeidolphHotplate._stir_stop, False, "Stop stirring."),
    ],
)
def test_set_rpm_off(hotplate_fixture, mocker, rpm, switch_cmd, log_message, switch_status):
    mock_write = mocker.patch.object(hotplate_fixture, "_write_hotplate")
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture.rpm = rpm
    assert hotplate_fixture.target_rpm == rpm
    assert hotplate_fixture._stir_switch == switch_status

    # Define the expected call sequence for _write_hotplate
    mock_write.assert_called_once_with(switch_cmd)

    # Define the expected call sequence for logger.info
    expected_logger_calls = [
        mocker.call(f"Target rpm set to {rpm}."),
        mocker.call(log_message),
    ]
    mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


@pytest.mark.parametrize(
    "rpm, switch_cmd, switch_status, log_message",
    [
        (200, HeidolphHotplate._stir_start, True, "Start stirring."),
        (1000, HeidolphHotplate._stir_start, True, "Start stirring."),
        (1400, HeidolphHotplate._stir_start, True, "Start stirring."),
    ],
)
def test_set_rpm(hotplate_fixture, mocker, rpm, switch_cmd, log_message, switch_status):
    mock_write = mocker.patch.object(hotplate_fixture, "_write_hotplate")
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture.rpm = rpm
    assert hotplate_fixture.target_rpm == rpm
    assert hotplate_fixture._stir_switch == switch_status

    # Define the expected call sequence for _write_hotplate
    expected_write_calls = [mocker.call(f"{hotplate_fixture._rpm_set} {rpm}"), mocker.call(switch_cmd)]
    mock_write.assert_has_calls(expected_write_calls, any_order=False)

    # Define the expected call sequence for logger.info
    expected_logger_calls = [
        mocker.call(f"Target rpm set to {rpm}."),
        mocker.call(log_message),
    ]
    mock_logger.assert_has_calls(expected_logger_calls, any_order=False)


def test_set_rpm_raises_type_error(hotplate_fixture):
    with pytest.raises(TypeError, match="rpm must be an integer"):
        hotplate_fixture.rpm = "invalid"


@pytest.mark.parametrize(
    "rpm, expected_error_message",
    [(50, "RPM out of range: min 100, max 1400!"), (1500, "RPM out of range: min 100, max 1400!")],
)
def test_set_rpm_raises_value_error(hotplate_fixture, rpm, expected_error_message):
    with pytest.raises(ValueError, match=expected_error_message):
        hotplate_fixture.rpm = rpm


@pytest.mark.parametrize("rpm", [50, 100, 500, 1400, 1600])
def test_get_rpm(hotplate_fixture, mocker, rpm):
    mock_query = mocker.patch.object(hotplate_fixture, "_query_hotplate", return_value=str(rpm))
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    assert hotplate_fixture.rpm == rpm
    mock_query.assert_called_with(hotplate_fixture._rpm_query)
    mock_logger.assert_called_once_with(f"RPM reading is {rpm}.")


@pytest.mark.parametrize(
    "stir_switch, switch_cmd, log_msg",
    [(True, HeidolphHotplate._stir_start, "Start stirring."), (False, HeidolphHotplate._stir_stop, "Stop stirring.")],
)
def test_set_stir_switch(hotplate_fixture, mocker, stir_switch, switch_cmd, log_msg):
    mock_write = mocker.patch.object(hotplate_fixture, "_write_hotplate")
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture._stir_switch = stir_switch
    assert hotplate_fixture._stir_switch_status == stir_switch

    mock_write.assert_called_once_with(switch_cmd)
    mock_logger.assert_called_once_with(log_msg)


@pytest.mark.parametrize("stir_switch_status", [True, False])
def test_get_stir_switch(hotplate_fixture, mocker, stir_switch_status):
    mock_logger = mocker.patch.object(hotplate_fixture.logger, "info")

    hotplate_fixture._stir_switch_status = stir_switch_status
    assert hotplate_fixture._stir_switch == stir_switch_status
    mock_logger.assert_called_once_with(f"Stir switch is {stir_switch_status}.")
