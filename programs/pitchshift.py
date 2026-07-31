# SPDX-FileCopyrightText: Copyright (c) 2026 Cooper Dalrymple
#
# SPDX-License-Identifier: GPLv3

from audiodelays import PitchShift

from blinka_pedal import BlinkaPedal
import programs

# Initialize Hardware
pedal = BlinkaPedal()

# Audio Object
effect = PitchShift(
    semitones=0.0,
    mix=1.0,

    **pedal.audiosample_args,
)

# Audio Chain
pedal.audio_out.play(
    effect.play(
        pedal.audio_in
    )
)

toggle = False
momentary = False
while True:
    pedal.update()
    programs.update(pedal)

    pots = pedal.pots
    pedal.mix, pedal.level = pots[:2]

    semitones = pots[2] * 24 - 12
    if not pedal.left_switch.value:
        semitones = round(semitones)
    if not pedal.right_switch.value:
        semitones *= 2
    effect.semitones = semitones

    if pedal.left_button.pressed:
        momentary = True
    elif pedal.left_button.released:
        momentary = False

    if pedal.right_button.pressed:
        toggle = not toggle
    
    pedal.bypass = not momentary and not toggle
    pedal.led = not pedal.bypass
