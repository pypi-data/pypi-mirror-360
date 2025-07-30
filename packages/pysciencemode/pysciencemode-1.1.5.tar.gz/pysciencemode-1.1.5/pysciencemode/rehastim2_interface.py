"""
Stimulator Interface class used to control the rehamove2.
See ScienceMode2 - Description and protocol for more information.
"""

from typing import Tuple
import time
from .acks import (
    stop_stimulation_ack,
    start_stimulation_ack,
    init_stimulation_ack,
    get_mode_ack,
    rehastim_error,
)
from .utils import (
    signed_int,
    check_stimulation_interval,
    check_inter_pulse_interval,
    check_low_frequency_factor,
    check_unique_channel,
    check_list_channel_order,
    calc_electrode_number,
    packet_construction,
)
from .sciencemode import RehastimGeneric
from .motomed_interface import _Motomed
from .enums import Device
from .channel import Channel


class Rehastim2(RehastimGeneric):
    """
    Class used for the communication with Rehastim2.
    """

    def __init__(self, port: str, show_log: bool = False, with_motomed: bool = False):
        """
        Creates an object stimulator.

        Parameters
        ----------
        port : str
            Port of the computer connected to the Rehastim2.
        show_log: bool
            If True, the log of the communication will be printed.
        with_motomed: bool
            If the motomed is connected to the Rehastim, put this flag to True.
        """
        self.list_channels = None
        self.stimulation_interval = None
        self.inter_pulse_interval = 2
        self.low_frequency_factor = 0
        self.electrode_number = 0
        self.electrode_number_low_frequency = 0

        self.amplitude = []
        self.pulse_width = []
        self.mode = []
        self.muscle = []
        self.given_channels = []
        self.stimulation_started = None
        self.device_type = Device.Rehastim2.value

        super().__init__(port, show_log, with_motomed, device_type=self.device_type)

        if with_motomed:
            self.motomed = _Motomed(self)

        # Connect to Rehastim2
        packet = None
        while packet is None:
            packet = self._get_last_ack(init=True)

        self.send_generic_packet("InitAck", packet=self._init_ack(packet[5]))
        self.stimulation_active = True
        self._start_thread_catch_ack()  # Start the thread which catches rehastim and motomed data

    def set_stimulation_signal(self, list_channels: list):
        """
        Sets or updates the stimulation's parameters.

        Parameters
        ----------
        list_channels: list[channel]
            Contain the channels and their parameters.
        """
        self.amplitude = []
        self.pulse_width = []
        self.mode = []
        self.muscle = []
        self.given_channels = []

        check_list_channel_order(list_channels)

        for i in range(len(list_channels)):
            self.amplitude.append(list_channels[i].get_amplitude())
            self.pulse_width.append(list_channels[i].get_pulse_width())
            self.mode.append(list_channels[i].get_mode())
            self.given_channels.append(list_channels[i].get_no_channel())

    def _send_packet(self, cmd: str) -> str:
        """
        Calls the methode that construct the packet according to the command.

        Parameters
        ----------
        cmd: str
            Command that will be sent.

        Returns
        -------
        In the case of an InitAck, return the string 'InitAck'.
        """

        packet = [-1]
        if cmd == "GetStimulationMode":
            packet = packet_construction(self.packet_count, "GetStimulationMode")
        elif cmd == "InitChannelListMode":
            packet = self._packet_init_stimulation()
        elif cmd == "StartChannelListMode":
            packet = self._packet_start_stimulation()
        elif cmd == "StopChannelListMode":
            packet = packet_construction(self.packet_count, "StopChannelListMode")
        self.motomed_done.set()
        init_ack = self.send_generic_packet(cmd, packet)
        if init_ack:
            return init_ack

    def _calling_ack(self, packet) -> str:
        """
        Processing ack from rehastim

        Parameters
        ----------
        packet:
            Packet which needs to be processed.

        Returns
        -------
        A string which is the message corresponding to the processing of the packet.
        """
        if packet == "InitAck" or packet[6] == 1:
            return "InitAck"
        elif packet[6] == self.Rehastim2Commands["GetStimulationModeAck"].value:
            return get_mode_ack(packet)
        elif packet[6] == self.Rehastim2Commands["InitChannelListModeAck"].value:
            return init_stimulation_ack(packet)
        elif packet[6] == self.Rehastim2Commands["StopChannelListModeAck"].value:
            return stop_stimulation_ack(packet)
        elif packet[6] == self.Rehastim2Commands["StartChannelListModeAck"].value:
            return start_stimulation_ack(packet)
        elif packet[6] == self.Rehastim2Commands["StimulationError"].value:
            return rehastim_error(signed_int(packet[7:8]))
        elif packet[6] == self.Rehastim2Commands["ActualValues"].value:
            raise RuntimeError(
                "Motomed is connected, so put the flag with_motomed to True."
            )
        else:
            raise RuntimeError(f"Error packet : not understood {packet[6]}")

    def _packet_init_stimulation(self) -> bytes:
        """
        Returns the packet for the InitChannelMode.
        """
        coded_inter_pulse_interval = int((self.inter_pulse_interval - 1.5) * 2)
        msb, lsb = self._msb_lsb_main_stim()

        data_stimulation = [
            self.low_frequency_factor,
            self.electrode_number,
            self.electrode_number_low_frequency,
            coded_inter_pulse_interval,
            msb,
            lsb,
            0,
        ]

        packet = packet_construction(
            self.packet_count, "InitChannelListMode", data_stimulation
        )
        return packet

    def _packet_start_stimulation(self) -> bytes:
        """
        Returns the packet for the StartChannelListMode.
        """
        data_stimulation = []
        for i in range(len(self.amplitude)):
            msb, lsb = self._msb_lsb_pulse_stim(self.pulse_width[i])
            data_stimulation.append(self.mode[i])
            data_stimulation.append(msb)
            data_stimulation.append(lsb)
            data_stimulation.append(int(self.amplitude[i]))
        packet = packet_construction(
            self.packet_count, "StartChannelListMode", data_stimulation
        )
        return packet

    def _msb_lsb_main_stim(self) -> Tuple[int, int]:
        """
        Returns the most significant bit (msb) and least significant bit (lsb) corresponding to the main stimulation
        interval.
        Main stimulation interval = [0, 2048] ∙ 0.5 ms + 1 ms
        Main stimulation interval = [1, 1025] ms
        Note that in the current software version the minimum main stimulation interval is 8 ms.
        (ScienceMode2 - Description and Protocol, 4.3 Stimulation Commands, InitChannelListMode)

        Returns
        -------
        (msb, lsb): tuple
            MSB and LSB of main stimulation interval
        """
        lsb = msb = -1
        stimulation_interval_coded = (self.stimulation_interval - 1) / 0.5
        if stimulation_interval_coded <= 255:
            lsb = stimulation_interval_coded
            msb = 0
        elif 256 <= stimulation_interval_coded <= 511:
            lsb = stimulation_interval_coded - 256
            msb = 1
        elif 512 <= stimulation_interval_coded <= 767:
            lsb = stimulation_interval_coded - 512
            msb = 2
        elif 768 <= stimulation_interval_coded <= 1023:
            lsb = stimulation_interval_coded - 768
            msb = 3
        elif 1024 <= stimulation_interval_coded <= 1279:
            lsb = stimulation_interval_coded - 1024
            msb = 4
        elif 1280 <= stimulation_interval_coded <= 1535:
            lsb = stimulation_interval_coded - 1280
            msb = 5
        elif 1536 <= stimulation_interval_coded <= 1791:
            lsb = stimulation_interval_coded - 1536
            msb = 6
        elif 1792 <= stimulation_interval_coded <= 2047:
            lsb = stimulation_interval_coded - 1792
            msb = 7
        elif stimulation_interval_coded == 2048:
            lsb = 0
            msb = 8

        return msb, int(lsb)

    @staticmethod
    def _msb_lsb_pulse_stim(pulse_width: int) -> Tuple[int, int]:
        """
        Returns MSB and LSB corresponding to the pulse width given.
        Range: [0, 500] μs (in current version [20, 500] μs, if (pw < 20) then pw = 20)
        (ScienceMode2 - Description and Protocol, 4.3 Stimulation Commands, StartChannelListMode)

        Parameters
        ----------
        pulse_width: int
            Pulse width of a signal.

        Returns
        -------
        (msb, lsb): tuple
            MSB and LSB of pulse_width.
        """
        msb = lsb = -1
        if pulse_width <= 255:
            lsb = pulse_width
            msb = 0
        elif 256 <= pulse_width <= 500:
            lsb = pulse_width - 256
            msb = 1
        return msb, lsb

    def init_channel(
        self,
        stimulation_interval: int,
        list_channels: list,
        inter_pulse_interval: int = 2,
        low_frequency_factor: int = 0,
    ):
        """
        Initialize the requested channel.
        Can update stimulation interval if one is given.
        Can update list_channels if one is iven.

        stimulation_interval: int
            Period of the main stimulation. [8,1025] ms.
        list_channels: list[Channel]
            List containing the channels and their parameters.
        """
        if self.stimulation_active:
            self.end_stimulation()

        check_stimulation_interval(stimulation_interval)
        for index, channel in enumerate(list_channels):
            if not isinstance(channel, Channel):
                raise TypeError(
                    f"Item at index {index} is not a Channel instance, got {type(channel).__name__} type instead."
                )
        if not list_channels:
            raise ValueError("Please provide at least one channel for stimulation.")
        else:
            self.list_channels = list_channels
        check_unique_channel(list_channels)
        self.stimulation_interval = stimulation_interval

        self.inter_pulse_interval = inter_pulse_interval
        check_inter_pulse_interval(inter_pulse_interval)

        self.low_frequency_factor = low_frequency_factor
        check_low_frequency_factor(low_frequency_factor)

        # Find electrode_number (according to Science_Mode2_Description_Protocol_20121212 p17)
        self.electrode_number = calc_electrode_number(self.list_channels)
        self.electrode_number_low_frequency = calc_electrode_number(
            self.list_channels, enable_low_frequency=True
        )

        self.set_stimulation_signal(self.list_channels)
        self._send_packet("InitChannelListMode")
        self._get_last_ack()

    def start_stimulation(
        self, stimulation_duration: float = None, upd_list_channels: list = None
    ):
        """
        Update a stimulation.
        Warning: only the channel that has been initiated can be updated.

        Parameters
        ----------
        stimulation_duration: float
            Time of the stimulation after the update.
        upd_list_channels: list[channel]
            List of the channels that will be updated
        """

        if upd_list_channels is not None:
            new_electrode_number = calc_electrode_number(upd_list_channels)

            # Verify if the updated channels have been initialised
            if new_electrode_number != self.electrode_number:
                raise RuntimeError(
                    "Error update: all channels have not been initialised"
                )
            self.list_channels = upd_list_channels
            self.set_stimulation_signal(self.list_channels)
        self._send_packet("StartChannelListMode")
        time_start_stim = time.time()

        self._get_last_ack()
        self.stimulation_active = True

        if stimulation_duration is not None:
            if stimulation_duration < time.time() - time_start_stim:
                raise RuntimeError("Asked stimulation duration too short")
            time.sleep(stimulation_duration - (time.time() - time_start_stim))
            self.pause_stimulation()

    def pause_stimulation(self):
        """
        Update a stimulation.
        Warning: only the channel that has been initiated can be updated.
        """
        tmp_amp = self.amplitude
        self.amplitude = [0] * len(self.list_channels)
        self._send_packet("StartChannelListMode")
        self._get_last_ack()
        self.amplitude = tmp_amp

    def end_stimulation(self):
        """
        Stop a stimulation, after calling this method, init_channel must be used if stimulation need to be restarted.
        """
        self._send_packet("StopChannelListMode")
        self._get_last_ack()
        self.packet_count = 0

    def get_motomed_angle(self) -> float:
        """
        Get the angle of the Motomed.

        Returns
        -------
        angle: float
            Angle of the Motomed.
        """
        return self.get_angle()

    def get_motomed_speed(self) -> float:
        """
        Get the angle of the Motomed.

        Returns
        -------
        angle: float
            Angle of the Motomed.
        """
        return self.get_speed()

    def get_motomed_torque(self) -> float:
        """
        Get the angle of the Motomed.

        Returns
        -------
        angle: float
            Angle of the Motomed.
        """
        return self.get_torque()
