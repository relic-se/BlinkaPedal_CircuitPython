# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

from blinka_pedal import BlinkaPedal

# Initialize Hardware
pedal = BlinkaPedal()

# Audio Chain
pedal.audio_out.play(
    pedal.audio_in
)

while True:
    pedal.update()

    if pedal.right_button.released:
        pedal.bypass = not pedal.bypass
        pedal.led = not pedal.bypass

    pedal.mix, pedal.level, _ = pedal.pots

    pedal.codec.adc_loopback = not pedal.left_switch.value
