# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

from audiofilters import Distortion, Filter, DistortionMode
import synthio

from hardware import (
    codec, audio_in, audio_out,
    led, left_switch, right_switch, left_button, right_button,
    update, get_pot_values, bypass, is_bypassed, mix, level
)

# Constants
MIN_FILTER = 120
MAX_FILTER = 12000

BOOST_GAIN = 24

MODES = (
    DistortionMode.CLIP,
    DistortionMode.OVERDRIVE,
    DistortionMode.WAVESHAPE,
    DistortionMode.LOFI,
)

# Audio Objects
distortion_effect = Distortion(
    drive=0.0,
    mix=1.0,
    sample_rate=codec.sample_rate,
    channel_count=audio_in.channel_count,
    soft_clip=True,
)

filter_effect = Filter(
    filter=synthio.Biquad(synthio.FilterMode.LOW_PASS, MAX_FILTER),
    sample_rate=codec.sample_rate,
    channel_count=audio_in.channel_count,
)

# Audio Chain
audio_out.play(
    filter_effect.play(
        distortion_effect.play(
            audio_in
        )
    )
)

mix(1.0)

boost = False
while True:
    update()
    pots = get_pot_values()

    led.duty_cycle = int((2 ** 16 - 1) * (not is_bypassed()) / (1 + (not boost) * 3))

    filter_effect.filter.frequency = pots[0] * (MAX_FILTER - MIN_FILTER) + MIN_FILTER
    level(pots[1])
    distortion_effect.drive = pots[2]

    distortion_effect.mode = MODES[int(not left_switch.value) + (int(not right_switch.value) << 1)]

    if left_button.released:
        boost = not boost
        distortion_effect.pre_gain = 12.0 * boost

    if right_button.released:
        bypass()
    