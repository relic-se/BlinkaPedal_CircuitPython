# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

import microcontroller

import programs

try:
    programs.load(save=False)
except OSError:
    # Reset the device in safe mode unable to load program
    microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
    microcontroller.reset()
