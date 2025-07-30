import time
from pysciencemode import Rehastim2 as St
from pysciencemode import Channel as Ch
from pysciencemode import Modes, Device


def init_rehastim():
    # Create a list of channels

    list_channels = []

    # Create all channels possible
    channel_1 = Ch(
        mode=Modes.SINGLE,
        no_channel=1,
        amplitude=10,
        pulse_width=100,
        name="Biceps",
        device_type=Device.Rehastim2,
    )
    channel_2 = Ch(
        mode=Modes.SINGLE,
        no_channel=2,
        amplitude=8,
        pulse_width=100,
        name="delt_ant",
        device_type=Device.Rehastim2,
    )
    channel_3 = Ch(
        mode=Modes.SINGLE,
        no_channel=3,
        amplitude=8,
        pulse_width=100,
        name="Triceps",
        device_type=Device.Rehastim2,
    )
    channel_4 = Ch(
        mode=Modes.SINGLE,
        no_channel=4,
        amplitude=9,
        pulse_width=100,
        name="delt_post",
        device_type=Device.Rehastim2,
    )

    # Choose which channel will be used
    list_channels.append(channel_1)
    list_channels.append(channel_2)
    list_channels.append(channel_3)
    list_channels.append(channel_4)

    # Create our object Stimulator
    stimulator = St(
        port="/dev/ttyYSB0", show_log=True, with_motomed=True
    )  # Enter the port on which the stimulator is connected
    stimulator.init_channel(
        stimulation_interval=20, list_channels=list_channels, low_frequency_factor=0
    )

    return stimulator, list_channels


if __name__ == "__main__":
    stimulator, list_channels = init_rehastim()
    motomed = stimulator.motomed

    list_channels[0].set_amplitude(10)
    list_channels[1].set_amplitude(10)
    list_channels[2].set_amplitude(10)
    list_channels[3].set_amplitude(10)

    motomed.start_basic_training(arm_training=True)
    stimulator.start_stimulation(upd_list_channels=list_channels)

    motomed.set_speed(20)
    bic_delt_stim = False
    tric_delt_stim = False
    while 1:
        angle_crank = motomed.get_angle()
        if (10 <= angle_crank < 20 or 180 <= angle_crank < 220) and (
            tric_delt_stim or bic_delt_stim
        ):
            stimulator.pause_stimulation()
            tric_delt_stim, bic_delt_stim = False, False
            print("angle crank", angle_crank)
            print("stimulation_state", (tric_delt_stim or bic_delt_stim))

        if 20 <= angle_crank < 180 and not tric_delt_stim:
            list_channels[0].set_amplitude(0)
            list_channels[1].set_amplitude(7)
            list_channels[2].set_amplitude(15)
            list_channels[3].set_amplitude(0)
            stimulator.start_stimulation(upd_list_channels=list_channels)
            tric_delt_stim = True
            bic_delt_stim = False
            print("angle crank", angle_crank)
            print("stimulation_state", tric_delt_stim)

        if (220 <= angle_crank < 360 or 0 <= angle_crank < 10) and not bic_delt_stim:
            list_channels[0].set_amplitude(15)
            list_channels[1].set_amplitude(0)
            list_channels[2].set_amplitude(0)
            list_channels[3].set_amplitude(7)
            stimulator.start_stimulation(upd_list_channels=list_channels)
            bic_delt_stim = True
            tric_delt_stim = False
            print("angle crank", angle_crank)
            print("stimulation_state", bic_delt_stim)

        time.sleep(0.01)
