# SPDX-FileCopyrightText: Copyright (c) 2024 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

import synthio
import ulab.numpy as np

from hardware import (
    codec, audio_in, audio_out,
    led, left_switch, right_switch, left_button, right_button,
    update, get_pot_values, bypass, is_bypassed, mix, level
)
mix(0.0)

# Constants
MIN_SPEED = 0.1
MAX_SPEED = 20.0

SPEED_MOD = (
    1.0,
    -0.5,
    3.0,
    -0.75
)

SAMPLE_SIZE = 1024
SAMPLE_VOLUME = 32767
waveforms = (
    np.concatenate(( # Triangle
        np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, num=SAMPLE_SIZE//2, dtype=np.int16),
        np.linspace(SAMPLE_VOLUME, -SAMPLE_VOLUME, num=SAMPLE_SIZE//2, dtype=np.int16)
    )),
    np.array(np.sin(np.linspace(0, 2 * np.pi, SAMPLE_SIZE, endpoint=False)) * SAMPLE_VOLUME, dtype=np.int16), # Sine
    np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, SAMPLE_SIZE, endpoint=False, dtype=np.int16), # Ramp Up
    np.linspace(-SAMPLE_VOLUME, SAMPLE_VOLUME, SAMPLE_SIZE, endpoint=False, dtype=np.int16), # Ramp Down
    np.concatenate(( # Square
        np.full(SAMPLE_SIZE//2, SAMPLE_VOLUME, dtype=np.int16),
        np.full(SAMPLE_SIZE//2, -SAMPLE_VOLUME, dtype=np.int16)
    )),
)
waveform = -1

# Synth and LFO
synth = synthio.Synthesizer(
    sample_rate=codec.sample_rate,
    channel_count=audio_in.channel_count,
)

lfo = synthio.Math(
    synthio.MathOperation.SCALE_OFFSET,
    synthio.LFO(
        waveform=np.zeros(SAMPLE_SIZE, dtype=np.int16),
        rate=MIN_SPEED,
        scale=0.5,
        offset=-0.5,
    ),
    0.0,  # Depth
    1.0  # Level
)
synth.blocks.append(lfo)  # Use synth to update LFO

# Audio Chain
audio_out.play(synth)  # No audio will actually happen

# Assign controls
def set_waveform(index: int):
    global waveform
    if index != waveform:
        waveform = index % len(waveforms)
        # waveform must be updated by element
        for i in range(SAMPLE_SIZE):
            lfo.a.waveform[i] = waveforms[waveform][i]
set_waveform(0)

double = False
while True:
    update()

    pots = get_pot_values()
    lfo.a.rate = (pots[0] * (MAX_SPEED - MIN_SPEED) + MIN_SPEED) * (1 + SPEED_MOD[(not left_switch.value) + (not right_switch.value) * 2] * double)
    set_waveform(round(pots[1] * (len(waveforms) - 1)))
    lfo.b = pots[2]  # depth

    led.duty_cycle = int((2 ** 16 - 1) * lfo.value) * (not is_bypassed())
    level(lfo.value)

    if left_button.pressed:
        double = True
    elif left_button.released:
        double = False

    if right_button.released:
        bypass()
