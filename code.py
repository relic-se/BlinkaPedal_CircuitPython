# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

import time

from hardware import (
    codec, i2s, bypass,
    led, left_switch, right_switch, left_button, right_button,
    update, get_pot_values
)

# Setup DAC Output
codec.dac_volume = 0.0  # dB
codec.dac_enabled = True
codec.dac_muted = False

# Line Output
codec.dac_to_line_output = True
codec.line_output_enabled = True
codec.line_output_muted = False

# Disable Bypass
bypass.value = False

# Generate one period of sine wave.
import array
import audiocore
import math
length = codec.sample_rate // 440
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = min(max(int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15), -38768), 38767)
sine_wave = audiocore.RawSample(sine_wave, sample_rate=codec.sample_rate)
i2s.play(sine_wave, loop=True)

led_state = True
timestamp = time.monotonic()
while True:
    update()
    pots = get_pot_values()

    now = time.monotonic()
    if now - timestamp > pots[0] + pots[1]:
        timestamp = now
        led_state = not led_state
    led.duty_cycle = int(pots[2] * (2 ** 16 - 1)) if led_state else 0

    for i, switch in enumerate([left_switch, right_switch]):
        if switch.fell:
            print(f"SW{i} On")
        elif switch.rose:
            print(f"SW{i} Off")

    for i, button in enumerate([left_button, right_button]):
        if button.pressed:
            print(f"BTN{i} Pressed")
        elif button.long_press:
            print(f"BTN{i} Long Press")
        elif button.released:
            print(f"BTN{i} Released")
