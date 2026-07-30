# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

from hardware import (
    codec, audio_in, audio_out,
    led, right_button, left_switch,
    update, get_pot_values, bypass, is_bypassed, mix, level
)

# Audio Chain
audio_out.play(
    audio_in
)

while True:
    update()
    pots = get_pot_values()

    if right_button.released:
        bypass()

    led.duty_cycle = (2 ** 16 - 1) * (not is_bypassed())

    mix(pots[0])
    level(pots[1])

    codec.adc_loopback = not left_switch.value
