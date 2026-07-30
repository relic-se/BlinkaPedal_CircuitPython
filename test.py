# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

import time
import ulab.numpy as np

from hardware import (
    codec, audio_in, audio_out,
    led, left_switch, right_switch, left_button, right_button,
    update, get_pot_values, bypass, is_bypassed, mix
)

# Generate one period of sine wave.
import array
import audiocore
import math
length = codec.sample_rate // 440
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = min(max(int(math.sin(math.pi * 2 * i / length) * (2 ** 15) + 2 ** 15), -38768), 38767)
sine_wave = audiocore.RawSample(sine_wave, sample_rate=codec.sample_rate)
audio_out.play(sine_wave, loop=True)
mix(0.5)

minv, maxv = 0, 1
buffer = array.array("h", [0] * 1024)

led_state = True
timestamp = time.monotonic()
while True:
    audio_in.record(buffer, len(buffer))
    v = np.max(np.array(buffer, dtype=np.int16))
    minv = min(v, minv)
    maxv = max(v, maxv)
    v = (v - minv) / (maxv - minv)
    print("=" * (round(63 * v) + 1))

    update()
    pots = get_pot_values()

    now = time.monotonic()
    if now - timestamp > pots[0] + pots[1]:
        timestamp = now
        led_state = not led_state
    led.duty_cycle = int(pots[2] * (2 ** 16 - 1) * v) * led_state

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

    if right_button.released:
        bypass()
        print("Bypass {}".format(is_bypassed()))
