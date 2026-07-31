# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

from audiofilters import Distortion, Filter, DistortionMode
import synthio

from blinka_pedal import BlinkaPedal
import programs

# Constants
MIN_FILTER = 600
MAX_FILTER = 12000

BOOST_GAIN = 24

MODES = (
    DistortionMode.CLIP,
    DistortionMode.OVERDRIVE,
    DistortionMode.WAVESHAPE,
    DistortionMode.LOFI,
)

# Initialize Hardware
pedal = BlinkaPedal()
pedal.mix = 1.0

# Audio Objects
distortion_effect = Distortion(
    drive=0.0,
    mix=1.0,
    soft_clip=True,
    **pedal.audiosample_args,
)

filter_effect = Filter(
    filter=synthio.Biquad(synthio.FilterMode.LOW_PASS, MAX_FILTER),
    **pedal.audiosample_args,
)

# Audio Chain
pedal.audio_out.play(
    filter_effect.play(
        distortion_effect.play(
            pedal.audio_in
        )
    )
)

boost = False
while True:
    pedal.update()
    programs.update(pedal)

    pedal.led = (not pedal.bypass) / (1 + (not boost) * 3)

    pots = pedal.pots
    filter_effect.filter.frequency = pots[0] * (MAX_FILTER - MIN_FILTER) + MIN_FILTER
    pedal.level = pots[1]
    distortion_effect.drive = pots[2]

    mode_index = int(not pedal.left_switch.value) | (int(not pedal.right_switch.value) << 1)
    distortion_effect.mode = MODES[mode_index]

    if pedal.left_button.pressed:
        boost = not boost
        distortion_effect.pre_gain = BOOST_GAIN * boost

    if pedal.right_button.pressed:
        pedal.bypass = not pedal.bypass
