import time
from typing import Dict, Optional, Union
from logging import Logger, getLogger

import serial

SERIAL_PARITY: Dict = {
    "none": serial.PARITY_NONE,
    "odd": serial.PARITY_ODD,
    "even": serial.PARITY_EVEN,
    "mark": serial.PARITY_MARK,
    "space": serial.PARITY_SPACE,
}

SERIAL_BYTESIZE: Dict = {
    5: serial.FIVEBITS,
    6: serial.SIXBITS,
    7: serial.SEVENBITS,
    8: serial.EIGHTBITS,
}

SERIAL_STOPBITS: Dict = {
    1: serial.STOPBITS_ONE,
    1.5: serial.STOPBITS_ONE_POINT_FIVE,
    2: serial.STOPBITS_TWO,
}

SERIAL_FACTORY: Dict = {
    "parity": SERIAL_PARITY,
    "bytesize": SERIAL_BYTESIZE,
    "stopbits": SERIAL_STOPBITS,
}


def open_close(func):
    """
    Decorator for managing the opening and closing of the COM port of the device.
    Closes communication first in case it is open (otherwise will raise error com_port is already open)
    Opens communication before sending/receiving commands, then closes in case of communication errors.

    Args:
      func: Function being wrapped

    Returns:
        wrapper: Wrapped function
    """

    def wrapper(self, *args, **kwargs):
        """
        Wrapper function for managing the opening and closing of the COM port of the device.

        Args:
            self: Instance of the SerialDevice (or child) class whose method is being wrapped
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            func_return: Return value(s) of the wrapped function
        """
        self.close_device_comm()  # This is done to avoid opening a com_port that is already open
        self.open_device_comm()
        func_return = func(self, *args, **kwargs)
        self.close_device_comm()
        return func_return

    return wrapper


class SerialDevice:
    category = "SerialDevice"
    ui_fields  = ("com_port", "baudrate", "bytesize", "parity", "stopbits", "timeout", "encoding")
    """ """

    default_eol: bytes = b"\r\n"

    def __init__(
        self,
        com_port: str,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "none",
        stopbits: int = 1,
        timeout: Optional[float] = None,
        encoding: str = "utf-8",
        # rs485: bool = False,
        logger: Optional[Logger] = None,
        **kwargs,
    ) -> None:
        """
        SerialDevice is a class for using serial communication with lab instruments. It will be used as a base class for
        other devices.

        If using the RS485 communication protocol, set rs485 to True. Them com_port corresponds to the address.

        Args:
            com_port: comunication port of the device, e.g., "COM1" for Windows, or "/dev/ttyS0" or "/dev/ttySUSB0" for Linux
            baudrate: baudrate of the device
            bytesize: number of data bits
            parity: parity of the device
            stopbits: number of stop bits
            timeout: time to wait for a response from the device
            encoding: encoding of the device
            rs485: if using RS485 communication protocol
            logger: logger to use
            **kwargs: additional keyword arguments for the serial.Serial class

        Returns:
            None
        """
        # ATTN
        # rs485 in SerialDevice is not actually useful since we are not using any advanced settings of RS485 communication
        # if rs485 and (int(com_port) <= 0 or int(com_port) > 255):
        #     raise ValueError("RS485 address must be between 1 and 255.")

        self.com_port: str = com_port
        self.baudrate: int = baudrate
        self.bytesize: int = SERIAL_BYTESIZE[bytesize]
        self.parity: str = SERIAL_PARITY[parity]
        self.stopbits: int = SERIAL_STOPBITS[stopbits]
        self.timeout: float = timeout
        self.encoding: str = encoding
        # ATTN
        # same as above
        # self.rs485: bool = rs485

        self._init_device()
        self.logger = logger if logger is not None else getLogger()

        settings = {
            "com_port": self.com_port,
            "baudrate": self.baudrate,
            "parity": self.parity,
            "bytesize": self.bytesize,
            "timeout": self.timeout,
            "stopbits": self.stopbits,
            # "rs485": self.rs485,
            "encoding": self.encoding,
            **kwargs,
        }

        self.logger.debug(f"Created SerialDevice with settings: {settings}")

    def _init_device(self, **kwargs) -> None:
        """
        Initialize serial communication with a device.

        Args:
            **kwargs: additional keyword arguments

        Returns:
            None
        """
        # ATTN: How would Serial class be initialized for RS485?
        self.device = serial.Serial(
            port=self.com_port,
            baudrate=self.baudrate,
            parity=self.parity,
            bytesize=self.bytesize,
            timeout=self.timeout,
            stopbits=self.stopbits,
            **kwargs,
        )
        self.close_device_comm()

    def open_device_comm(self) -> None:
        """
        Closes communication with the device to free the port, then opens communication with the device.
        DO NOT start the device electronically!

        Returns:
            None
        """
        self.device.close()
        self.device.open()

    def close_device_comm(self) -> None:
        """
        Closes communication with the device.
        DO NOT shut down the device electronically!

        Returns:
            None
        """
        self.device.close()

    @staticmethod
    def _encode(command: Union[str, bytes, bytearray]) -> bytes:
        """
        Encodes the commands to bytes.

        Args:
          command: command to write

        Returns:
            command: command encoded as bytes

        Raises:
            TypeError: If the command type is not str, bytes, or bytearray
        """
        if isinstance(command, str):
            command: bytes = command.encode()
        elif isinstance(command, bytearray):
            command: bytes = bytes(command)
        elif isinstance(command, bytes):
            pass
        else:
            raise TypeError("'command' type must be either  str, bytes, or bytearray.")
        return command

    def write(self, command: Union[str, bytes, bytearray]) -> None:
        """
        Writes the command in bytes to the device

        Args:
          command: command to write

        Returns:
            None
        """
        command_bytes: bytes = self._encode(command)
        self.device.write(command_bytes)

    def read(self, return_bytes: bool = False, **kwargs) -> Union[str, bytes]:
        """
        Reads the response from the device until the end-of-line (EOL) character.

        Args:
          return_bytes: Whether to return the response as bytes or as a string (Default value = False)
          **kwargs: Additional keyword arguments for the read_bytes method

        Returns:
            device response, not including the EOL
        """
        response: bytes = self.read_bytes(**kwargs)

        if not return_bytes:
            response: str = response.decode(self.encoding)

        return response

    def read_bytes(
        self,
        read_until: Optional[Union[str, bytes]] = None,
        num_bytes: int = None,
        remove_from_start: int = 0,
        remove_from_end: Optional[int] = None,
    ) -> bytes:
        # TODO: Clean up docstring
        """
        Reads the response from the device until EOL (b'\r\n')
        num_bytes: max number of bytes
        :return: decoded string, not including the EOL

        Args:
          read_until: Character(s) until which to read the response. If None, then the default EOL is used. (Default value = None)
          num_bytes: Number of bytes to read. If None, then read until read_until. (Default value = None)
          remove_from_start: Number of bytes to remove from the start of the response. (Default value = 0)
          remove_from_end: Number of bytes to remove from the end of the response. (Default value = None)

        Returns:
            Device response in bytes with the specified bytes removed from the start and end

        Raises:
            ValueError: If remove_from_end is a negative integer
            IndexError: If remove_from_start is greater than the length of the full response minus remove_from_end
        """
        if remove_from_end is not None and remove_from_end < 0:
            raise ValueError("remove_from_end must be a positive integer.")

        read_until: Union[str, bytes] = read_until if read_until else self.default_eol
        command_bytes: bytes = self._encode(read_until)
        full_response: bytes = self.device.read_until(expected=command_bytes, size=num_bytes)

        # ATTN: I don't remember why we have this if statement... Why not default remove_from_end to 0?
        if not remove_from_end:
            response = full_response[remove_from_start:]
        else:
            if remove_from_start >= len(full_response) - remove_from_end:
                raise IndexError("End index is less than start index.")

            response = full_response[remove_from_start:-remove_from_end]

        return response

    def query(
        self,
        write_command: Union[str, bytes, bytearray],
        read_delay: float = 0.5,
        return_bytes: bool = False,
        **kwargs,
    ) -> Union[str, bytes]:
        """
        Send command to the device, wait for read_delay seconds, then read the response.

        Args:
          write_command: Command to write
          read_delay: Time to wait before reading the response (Default value = 0.5)
          return_bytes: True to return bytes without decoding to str
          **kwargs: Additional keyword arguments for the read method

        Returns:
            Device response string
        """
        self.write(write_command)
        time.sleep(read_delay)
        return self.read(return_bytes, **kwargs)
