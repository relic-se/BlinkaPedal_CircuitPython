# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

from blinka_pedal import BlinkaPedal

# Initialize Hardware
pedal = BlinkaPedal(
    mix=1.0,
    level=1.0,
)

# Audio Chain
pedal.audio_out.play(
    pedal.audio_in
)

while True:
    pedal.update()

    if pedal.right_button.released:
        pedal.bypass = not pedal.bypass
        pedal.led = not pedal.bypass
        
    if pedal.left_switch.rose or pedal.left_switch.fell:
        pedal.codec.adc_loopback = not pedal.left_switch.value
