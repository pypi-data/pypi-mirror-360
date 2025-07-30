from pathlib import Path
from struct import pack
from matterlab_serial_device import SerialDevice, open_close
from matterlab_relays.base_relay import Relay
from typing import Optional
import time

class CE221ARelay(Relay, SerialDevice):
    category="Relay"
    ui_fields  = ("com_port", "channel")
    def __init__(self,
                 com_port: str,
                 channel: int,
                 encoding: str = "utf-8",
                 baudrate: int = 9600,
                 timeout: float = 1.0,
                 parity: str = "none",
                 bytesize: int = 8,
                 stopbits: int = 1,
                 **kwargs
                 ):
        """
                :param com_port: COM port of the pump connected to, example: "COM1", "/tty/USB0"
                :param address: RS485 address of relay
                :param channel: channel number to instantiate,
                                    None to allow multi channel operation (not implemented in base_relay)
                :return:
        """
        SerialDevice.__init__(self,
                              com_port = com_port,
                              encoding=encoding,
                              baudrate=baudrate,
                              timeout=timeout,
                              parity=parity,
                              bytesize=bytesize,
                              stopbits=stopbits,
                              **kwargs)
        Relay.__init__(self)
        self.channel = channel

    def _generate_execution_command(self, channel: int, open_channel: bool):
        if open_channel:
            open_cmd = 1
        else:
            open_cmd = 2

        commands = [0x55, 0x56, 0x00, 0x00, 0x00, channel, open_cmd]
        commands.append(sum(commands) & 0xFF)
        return bytes(commands)

    @open_close
    def set_relay(self, channel: int, open_channel: bool):
        command_bytes = self._generate_execution_command(channel=channel, open_channel=open_channel)
        self.write(command_bytes)
        time.sleep(0.5)

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, open_channel: bool):
        self.set_relay(channel = self.channel, open_channel = open_channel)
        self._on = open_channel
