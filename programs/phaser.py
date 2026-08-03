# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

from audiofilters import Phaser
import synthio

from blinka_pedal import BlinkaPedal
import programs

# Constants
STAGES_INCREMENT = 2

MIN_FREQUENCY = 200
MAX_FREQUENCY = 2000
MIN_DEPTH = 0.25

MIN_RATE = 0.1
MAX_RATE = 8.0

MIN_FEEDBACK = 0.5
MAX_FEEDBACK = 1.0

# Initialize Hardware
pedal = BlinkaPedal(
    mix=1.0,
)

# Audio Objects
lfo = synthio.LFO(
    offset=(MIN_FREQUENCY + MAX_FREQUENCY) / 2,
    scale=0,
    rate=MIN_RATE,
)

effect = Phaser(
    frequency=lfo,
    stages=STAGES_INCREMENT,
    feedback=MIN_FEEDBACK,
    mix=1.0,

    **pedal.audiosample_args,
)

# Audio Chain
pedal.audio_out.play(
    effect.play(
        pedal.audio_in
    )
)

while True:
    pedal.update()
    programs.update(pedal)

    pedal.led = (lfo.value - MIN_FREQUENCY) / (MAX_FREQUENCY - MIN_FREQUENCY) * (not pedal.bypass)

    pots = pedal.pots
    lfo.rate = pots[0] * (MAX_RATE - MIN_RATE) + MIN_RATE
    lfo.scale = (pots[1] * (1 - MIN_DEPTH) + MIN_DEPTH) * (MAX_FREQUENCY - MIN_FREQUENCY) / 2
    effect.feedback = pots[2] * (MAX_FEEDBACK - MIN_FEEDBACK) + MIN_FEEDBACK

    effect.stages = ((int(not pedal.left_switch.value) | (int(not pedal.right_switch.value) << 1)) + 1) * STAGES_INCREMENT

    # TODO: left button?

    if pedal.right_button.pressed:
        pedal.bypass = not pedal.bypass
