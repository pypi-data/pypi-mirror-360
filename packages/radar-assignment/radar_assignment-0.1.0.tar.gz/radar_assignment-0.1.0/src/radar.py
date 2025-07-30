import re
from asyncio import sleep

from typing import ClassVar, Protocol, Iterator
from dataclasses import dataclass, KW_ONLY, field

from serial import Serial


# Pattern used to ignore messages indicating absence
ABSENCE_PATTERN = re.compile(r"absence")


# Interface to define a processor that converts raw messages into structured data
class Processor[T](Protocol):
    def __call__(self, message: str) -> T:
        """Processes the given message and returns the result."""
        ...


@dataclass(frozen=True)
class Messages:
    # Simple wrapper for a list of raw message strings
    messages: list[str]

    def __iter__(self) -> Iterator[str]:
        return iter(self.messages)

    def __len__(self) -> int:
        return len(self.messages)

    def __str__(self) -> str:
        return "\n".join(f"- {message}" for message in self.messages)


@dataclass
class DataStream:
    # Markers used to identify message types in radar serial output
    REGULAR_MESSAGE_MARKER: ClassVar = "[INFO]"
    SHORT_MESSAGE_MARKER: ClassVar = "[INFO] absence"
    LINES_PER_MESSAGE: ClassVar = 2  # Number of lines per radar message

    port: str
    baudrate: int
    serial: Serial | None = field(init=False, default=None)
    interrupted: bool = field(init=False, default=False)

    def __enter__(self) -> "DataStream":
        # Open serial connection
        assert self.serial is None, "There should be no serial port open yet."

        self.serial = Serial(
            self.port, baudrate=self.baudrate, timeout=Radar.DEFAULT_TIMEOUT
        )

        return self

    def __exit__(self, type, value, traceback) -> bool:
        # Close serial connection and propagate exception if needed
        assert self.serial is not None, "The serial port should be open, but it is not."

        self.serial.close()

        if value is not None:
            raise value

        return True

    def read_messages(self, count: int) -> Messages:
        # Read a specified number of full messages from the radar
        return Messages([self._read_data_message() for _ in range(count)])

    def read_and[T](self, processor: Processor[T], *, count: int) -> list[T]:
        # Read and process a number of messages
        return [processor(message) for message in self.read_messages(count)]

    async def read_continuously_and(self, processor: Processor) -> None:
        # Continuously read and process messages until interrupted
        while not self.interrupted:
            processor(self._read_data_message())
            await sleep(0.5)  # Delay between reads to avoid flooding (0.5 seconds)

    def interrupt(self) -> None:
        # Stop the continuous reading loop
        print("Data stream stopping...")
        self.interrupted = True

    def _read_data_message(self) -> str:
        # Read a single full radar message, ignoring 'absence' messages
        assert self.serial is not None, "The serial port should be open, but it is not."

        lines: list[str] = []
        message_started = False

        while len(lines) < DataStream.LINES_PER_MESSAGE:
            if not self.serial.in_waiting:
                continue

            line = self.serial.readline().decode().strip()

            if (
                message_started
                or line.startswith(DataStream.REGULAR_MESSAGE_MARKER)
                or line.startswith(DataStream.SHORT_MESSAGE_MARKER)
            ) and ABSENCE_PATTERN.search(line) is None:
                lines.append(line)
                message_started = True

            if line.startswith(DataStream.SHORT_MESSAGE_MARKER) and message_started:
                break

        return " ".join(lines)


@dataclass
class Radar:
    # Class to configure and interface with radar hardware
    DEFAULT_TIMEOUT: ClassVar = 1  # Timeout for serial communication in seconds
    DEFAULT_MODE: ClassVar = "macro_only"  # Radar operation mode
    CONFIG_MARKER: ClassVar = "[CONFIG]"  # Used to detect config blocks in response

    _: KW_ONLY
    port: str
    baudrate: int

    _max_range: float | None = field(init=False, default=None)

    def configure(self, *, max_range: float) -> None:
        # Send configuration commands to the radar
        self._max_range = max_range

        with Serial(self.port, self.baudrate, timeout=Radar.DEFAULT_TIMEOUT) as serial:
            self._send(serial, "")
            self._send(serial, f"set_mode {Radar.DEFAULT_MODE}")
            self._send(serial, f"set_max_range {max_range}")
            self._send(serial, "config")
            self._send_esc(serial)
            print(self._read_config(serial))

    def data_stream(self) -> DataStream:
        # Return a stream object to read radar output
        return DataStream(self.port, self.baudrate)

    def max_range(self) -> float:
        # Accessor for the configured max range
        assert self._max_range is not None, (
            "The radar is not yet configured with a max range."
        )

        return self._max_range

    def range_bin_length(self) -> float:
        # Distance represented by each data bin, specific to radar model
        return 0.325861  # This is a fixed value based on radar's internal resolution

    def _send(self, serial: Serial, text: str) -> None:
        # Send a command followed by carriage return
        serial.write((text + "\r").encode())

    def _send_esc(self, serial: Serial) -> None:
        # Send escape character (ESC) to exit config mode
        serial.write(b"\x1b")

    def _read_config(self, serial: Serial) -> str:
        # Read configuration output from radar after setting parameters
        lines = []
        config_section_started = False

        while True:
            if not serial.in_waiting:
                continue

            lines.append(line := serial.readline().decode().strip())

            match (line, config_section_started):
                case Radar.CONFIG_MARKER, True:
                    break
                case Radar.CONFIG_MARKER, False:
                    config_section_started = True

        return "\n".join(lines) + "\n"
