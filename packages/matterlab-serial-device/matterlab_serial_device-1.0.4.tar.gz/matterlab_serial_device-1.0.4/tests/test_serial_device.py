import os
import pytest
import serial

from matterlab_serial_device import SerialDevice, open_close
from matterlab_serial_device.serial_device import (
    SERIAL_PARITY,
    SERIAL_BYTESIZE,
    SERIAL_STOPBITS,
)

# ATTN: Better tests could be written with the hypothesis library. Leaving for later.

PORT = "/dev/ttyUSB0" if os.name == "posix" else "COM1"


@pytest.fixture
def mock_serial(mocker):
    """


    Args:
      mocker:

    Returns:

    """
    mock_serial = mocker.patch("matterlab_serial_device.serial_device.serial.Serial", autospec=True)
    mock_serial_instance = mock_serial.return_value
    mock_serial_instance.com_port = PORT  # Set the expected return value
    yield mock_serial_instance


@pytest.fixture
def device_fixture(mock_serial):
    """


    Args:
      mock_serial:

    Returns:

    """
    serial_device = SerialDevice(com_port=PORT)
    yield serial_device


def test_init_defaults(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    # Test class attributes
    assert device_fixture.default_eol == b"\r\n"

    # Test default instance attributes
    assert device_fixture.com_port == PORT
    assert device_fixture.encoding == "utf-8"
    assert device_fixture.baudrate == 9600
    assert device_fixture.parity == serial.PARITY_NONE
    assert device_fixture.bytesize == serial.EIGHTBITS
    assert device_fixture.timeout is None
    assert device_fixture.stopbits == serial.STOPBITS_ONE

    # Test that the mocked Serial class was called with the correct arguments
    assert device_fixture.device.com_port == PORT

    # Test that the COM port was closed after device initialization in SerialDevice._init_device()
    mock_serial.close.assert_called_once()


def test_init_bytesize(mock_serial):
    """


    Args:
      mock_serial:

    Returns:

    """
    for key, value in SERIAL_BYTESIZE.items():
        serial_device = SerialDevice(com_port=PORT, bytesize=key)
        assert serial_device.bytesize == value


def test_init_parity(mock_serial):
    """


    Args:
      mock_serial:

    Returns:

    """
    for key, value in SERIAL_PARITY.items():
        serial_device = SerialDevice(com_port=PORT, parity=key)
        assert serial_device.parity == value


def test_init_stopbits(mock_serial):
    """


    Args:
      mock_serial:

    Returns:

    """
    for key, value in SERIAL_STOPBITS.items():
        serial_device = SerialDevice(com_port=PORT, stopbits=key)
        assert serial_device.stopbits == value


def test_open_device_comm(mocker, mock_serial, device_fixture):
    """


    Args:
      mocker:
      mock_serial:
      device_fixture:

    Returns:

    """
    device_fixture.open_device_comm()

    # Define the expected call sequence
    expected_calls = [mocker.call.close(), mocker.call.close(), mocker.call.open()]

    # Check that the calls were made in the specified order
    mock_serial.assert_has_calls(expected_calls, any_order=False)


def test_close_device_comm(mocker, mock_serial, device_fixture):
    """


    Args:
      mocker:
      mock_serial:
      device_fixture:

    Returns:

    """
    device_fixture.close_device_comm()

    # Define the expected call sequence
    expected_calls = [mocker.call.close(), mocker.call.close()]

    # Check that the calls were made in the specified order
    mock_serial.assert_has_calls(expected_calls, any_order=False)


def test_open_close(mocker, mock_serial, device_fixture):
    """


    Args:
      mocker:
      mock_serial:
      device_fixture:

    Returns:

    """

    class DummyDevice(SerialDevice):
        """ """

        @open_close
        def _dummy_method(self):
            """ """
            pass

    dummy_device = DummyDevice(com_port=PORT)
    dummy_device._dummy_method()

    # Define the expected call sequence
    expected_calls = [
        mocker.call.close(),
        mocker.call.close(),
        mocker.call.open(),
        mocker.call.close(),
    ]

    # Check that the calls were made in the specified order
    mock_serial.assert_has_calls(expected_calls, any_order=False)


def test_encode(device_fixture):
    """


    Args:
      device_fixture:

    Returns:

    """
    assert device_fixture._encode("test") == b"test"
    assert device_fixture._encode(b"test") == b"test"
    assert device_fixture._encode(bytearray(b"test")) == b"test"
    with pytest.raises(TypeError):
        device_fixture._encode(123)


def test_write(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    device_fixture.write("test")
    device_fixture.device.write.assert_called_once_with(b"test")


def test_read(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    for return_bytes in [True, False]:
        mock_serial.read_until.return_value = b"test"
        response = device_fixture.read(return_bytes=return_bytes)

        if return_bytes:
            assert response == b"test"
        else:
            assert response == "test"

        device_fixture.device.read_until.assert_called_once_with(expected=b"\r\n", size=None)
        mock_serial.reset_mock()  # Reset call counter at end of loop


def test_read_bytes_default(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    expected_response = b"test"
    mock_serial.read_until.return_value = expected_response

    response = device_fixture.read_bytes()

    assert response == expected_response
    device_fixture.device.read_until.assert_called_once_with(expected=b"\r\n", size=None)


def test_read_bytes_until(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    for read_until in [b"end", "end"]:
        device_fixture.read_bytes(read_until=read_until)

        mock_serial.read_until.assert_called_once_with(expected=b"end", size=None)
        mock_serial.reset_mock()  # Reset call counter at end of loop


def test_read_bytes_num_bytes(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    device_fixture.read_bytes(num_bytes=10)

    mock_serial.read_until.assert_called_once_with(expected=b"\r\n", size=10)


def test_read_bytes_remove_from_start(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    mock_serial.read_until.return_value = b"test\r\n"
    expected_response = b"test\r\n"[2:]

    response = device_fixture.read_bytes(remove_from_start=2)

    assert response == expected_response
    mock_serial.read_until.assert_called_once()


def test_read_bytes_remove_from_end(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    mock_serial.read_until.return_value = b"test12"
    expected_response = b"test"

    response = device_fixture.read_bytes(remove_from_end=2)

    assert response == expected_response
    mock_serial.read_until.assert_called_once()

    with pytest.raises(ValueError):
        device_fixture.read_bytes(remove_from_end=-1)


def test_read_bytes_remove_from_start_and_end(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    mock_serial.read_until.return_value = b"test\r\n"
    expected_response = b"st"

    response = device_fixture.read_bytes(remove_from_start=2, remove_from_end=2)

    assert response == expected_response
    mock_serial.read_until.assert_called_once_with(expected=b"\r\n", size=None)

    with pytest.raises(IndexError):
        mock_serial.read_until.return_value = b"123456"
        device_fixture.read_bytes(remove_from_start=3, remove_from_end=3)

    with pytest.raises(IndexError):
        mock_serial.read_until.return_value = b"123456789"
        device_fixture.read_bytes(remove_from_start=6, remove_from_end=7)


def test_query(mock_serial, device_fixture):
    """


    Args:
      mock_serial:
      device_fixture:

    Returns:

    """
    for command in ["test", b"test", bytearray("test", "utf-8")]:
        mock_serial.read_until.return_value = b"test"
        response = device_fixture.query(command)

        assert response == "test"
        device_fixture.device.write.assert_called_once_with(b"test")
        device_fixture.device.read_until.assert_called_once_with(expected=b"\r\n", size=None)
        mock_serial.reset_mock()
