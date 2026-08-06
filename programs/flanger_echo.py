# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

from audiodelays import Echo
import synthio

from blinka_pedal import BlinkaPedal
import programs

# Constants
MIN_DELAY    = 0.5  # ms
MAX_DELAY    = 4  # ms (must be int)

MIN_RATE     = 0.5  # hz
MAX_RATE     = 4.0  # hz

MIN_DECAY = 0.25
MAX_DECAY = 0.75

# Initialize Hardware
pedal = BlinkaPedal()
pedal.update()

# Audio Objects
lfo = synthio.LFO(
    rate=MIN_RATE,
    scale=0.0,
    offset=MIN_DELAY,
)

effect = Echo(
    freq_shift=True,
    max_delay_ms=MAX_DELAY,
    delay_ms=synthio.Math(
        synthio.MathOperation.CONSTRAINED_LERP,
        MIN_DELAY,
        MAX_DELAY,
        lfo := synthio.LFO(),
    ),
    decay=(MIN_DECAY if pedal.left_switch.value else MAX_DECAY),
    mix=0.5,
    **pedal.audiosample_args,
)

# Audio Chain
pedal.play(
    effect.play(
        pedal.audio_in
    )
)

infinite = False
while True:
    pedal.update()
    programs.update(pedal)

    pots = pedal.pots
    effect.delay_ms.a = pots[0] * (MAX_DELAY - MIN_DELAY) + MIN_DELAY
    lfo.scale = lfo.offset = pots[1] / 2
    lfo.rate = pots[2] * (MAX_RATE - MIN_RATE) + MIN_RATE

    effect.decay = 1 if infinite else (MIN_DECAY if pedal.left_switch.value else MAX_DECAY)

    if pedal.left_button.pressed:
        infinite = True
    elif pedal.left_button.released:
        infinite = False

    if pedal.right_button.released:
        pedal.bypass = not pedal.bypass
        effect.mix = not pedal.bypass
    
    pedal.led = lfo.value * (not pedal.bypass)
