from serial import Serial
from modbus_tk.modbus_rtu import RtuMaster
from modbus_tk.defines import WRITE_SINGLE_COIL, WRITE_MULTIPLE_COILS, READ_COILS
from typing import Union, Dict
from pathlib import Path
from matterlab_serial_device import SerialDevice, open_close
from matterlab_relays.base_relay import Relay


class JYdaqRelay(Relay, SerialDevice):
    category="Relay"
    ui_fields  = ("com_port", "address","channel")
    def __init__(self,
                 com_port: str,
                 address: int,
                 channel: int = None,
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
        assert 0 <= channel <= 7, "JYDAO relay channel must be in [0,7]!"

        SerialDevice.__init__(self,
                              com_port = com_port,
                              encoding = encoding,
                              baudrate = baudrate,
                              parity = parity,
                              bytesize = bytesize,
                              stopbits = stopbits,
                              timeout = timeout,
                              **kwargs
                              )
        Relay.__init__(self)
        self.channel = channel
        self.address = address

    @open_close
    def _add_rtu_master(self):
        """
        create modbus rtu master object
        :return:
        """
        self.relay_rtu_master = RtuMaster(self.device)
        self.relay_rtu_master.set_timeout(0.5)
        self.relay_rtu_master.set_verbose(True)

    @open_close
    def set_relay(self, channel: int, open_channel: bool):
        """
        write single coil to set the channel of relay to open/close
        :param channel: channel number to set
        :param open_channel: True/1 for open, False/0 for close
        :return:
        """
        self.relay_rtu_master.execute(self.address,
                                      function_code=WRITE_SINGLE_COIL,
                                      starting_address=channel,
                                      output_value=int(open_channel))

    @open_close
    def set_multiple_relays(self, open_channel: Union[list, tuple]):
        """
        set multiple relays with single execution, starting from relay0
        :param open_channel: list/tuple of bool or int[0,1], indicating status of relays to set to
        :return:
        """
        statuses_int = [int(x) for x in open_channel]
        self.relay_rtu_master.execute(self.address,
                                      function_code=WRITE_MULTIPLE_COILS,
                                      starting_address=0,
                                      output_value=statuses_int)

    @open_close
    def query_multiple_relays(self) -> list:
        """
        query open_channel of all relay [0,7]
        :return: list of status in bool, True for open, False for closed
        """
        open_channel = self.relay_rtu_master.execute(self.address,
                                                  function_code=READ_COILS,
                                                  starting_address=0,
                                                  quantity_of_x=8)
        return [bool(x) for x in open_channel]

    def query_relay(self, channel: int) -> bool:
        """
        query a single channel status
        :param channel: channel number to query
        :return: relay is open (True) or closed (False)
        """
        # assert self.settings.channel_min <= channel <= self.settings.channel_max, "Channel out of range!"
        return self.query_multiple_relays()[channel]


    @property
    def on(self) -> bool:
        """
        concrete method to return if a relay channel is set to normal_open or normal_close
        :return:
        """
        return self.query_relay(channel= self.channel_num)

    @on.setter
    def on(self, open_channel: bool):
        """
        concrete method to set a relay channel to normal_open or normal_close
        :param open_channel:
        :return:
        """
        self.set_relay(channel= self.channel_num, open_channel= open_channel)