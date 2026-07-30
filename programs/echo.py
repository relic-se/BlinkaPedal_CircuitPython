# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

from audiodelays import Echo
from audiofilters import Filter
import synthio
import time

from hardware import (
    codec, audio_in, audio_out,
    led, left_switch, right_switch, left_button, right_button,
    update, get_pot_values, bypass, is_bypassed, mix
)

# Constants
TAPE_LENGTH    = 100    # ms

MIN_DELAY      = 10     # ms
MAX_DELAY      = 1000   # ms
MAX_EXPRESSION = 500    # ms

LFO_SPEED      = 0.5   # s
LFO_SCALE      = 0.1

MIN_FILTER     = 100    # hz
MAX_FILTER     = 20000  # hz

BUFFER_SIZE    = 2048   # bytes

# Audio Objects
delay_ms = synthio.Math(
    synthio.MathOperation.SCALE_OFFSET,
    0.0,  # Expression Amount
    MAX_EXPRESSION,
    TAPE_LENGTH  # Delay Value
)

delay_lfo = synthio.LFO(
    rate=LFO_SPEED,
    scale=0.0,
)

delay_effect = Echo(
    max_delay_ms=TAPE_LENGTH,
    delay_ms=synthio.Math(
        synthio.MathOperation.SCALE_OFFSET,
        delay_lfo,
        delay_ms,
        delay_ms
    ),
    mix=1.0,
    freq_shift=True,
    
    sample_rate=codec.sample_rate,
    channel_count=audio_in.channel_count,
    buffer_size=BUFFER_SIZE,
    samples_signed=audio_in.samples_signed,
    bits_per_sample=audio_in.bits_per_sample,
)

filter_effect = Filter(
    filter=synthio.Biquad(synthio.FilterMode.LOW_PASS, MAX_FILTER),
    mix=1.0,

    buffer_size=BUFFER_SIZE,
    sample_rate=codec.sample_rate,
    channel_count=audio_in.channel_count,
    bits_per_sample=audio_in.bits_per_sample,
    samples_signed=audio_in.samples_signed,
)

# Audio Chain
audio_out.play(
    filter_effect.play(
        delay_effect.play(
            audio_in
        )
    )
)

led_state = True
infinite = False
timestamp = time.monotonic()
while True:
    update()
    pots = get_pot_values()

    now = time.monotonic()
    if now - timestamp >= delay_effect.delay_ms.value:
        timestamp = now
        led_state = not led_state

    led.duty_cycle = int(pots[2] * (2 ** 16 - 1)) if led_state and not is_bypassed() else 0

    filter_effect.mix = 1.0 * (not left_switch.value)
    delay_lfo.scale = LFO_SCALE * (not right_switch.value)

    if right_button.released:
        bypass()

    # TODO: left button tap tempo
    if left_button.pressed:
        infinite = True
    elif left_button.released:
        infinite = False

    mix(pots[0])
    delay_effect.decay = 1.0 if infinite else pots[1]
    delay_ms.c = pots[2] * (MAX_DELAY - MIN_DELAY) + MIN_DELAY
