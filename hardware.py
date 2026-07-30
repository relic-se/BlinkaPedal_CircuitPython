# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

from analogio import AnalogIn
from audiobusio import I2SOut
from audioi2sin import I2SIn
import board
from busio import I2C
import digitalio
from pwmio import PWMOut

from adafruit_debouncer import Button, Debouncer
from relic_tlv320aic3204 import TLV320AIC3204, INPUT_1, IMPEDANCE_40K

_PIN_BTN0 = board.GP10
_PIN_BTN1 = board.GP11

_PIN_SW0 = board.GP12
_PIN_SW1 = board.GP19

_PIN_LED = board.GP22

_PIN_POT0 = board.GP26
_PIN_POT1 = board.GP27
_PIN_POT2 = board.GP28

_PIN_SDA = board.GP20
_PIN_SCL = board.GP21

_PIN_RST = board.GP2
_PIN_MCLK = board.GP3
_PIN_BCLK = board.GP4
_PIN_WCLK = board.GP5
_PIN_DOUT = board.GP6
_PIN_DIN = board.GP7

_PIN_BYPASS = board.GP8

# Setup Controls
led = PWMOut(_PIN_LED)
led.duty_cycle = 0

_pin_btn0 = digitalio.DigitalInOut(_PIN_BTN0)
_pin_btn0.direction = digitalio.Direction.INPUT
_pin_btn0.pull = digitalio.Pull.UP
left_button = Button(_pin_btn0)

_pin_btn1 = digitalio.DigitalInOut(_PIN_BTN1)
_pin_btn1.direction = digitalio.Direction.INPUT
_pin_btn1.pull = digitalio.Pull.UP
right_button = Button(_pin_btn1)

_pin_sw0 = digitalio.DigitalInOut(_PIN_SW0)
_pin_sw0.direction = digitalio.Direction.INPUT
_pin_sw0.pull = digitalio.Pull.UP
left_switch = Debouncer(_pin_sw0)

_pin_sw1 = digitalio.DigitalInOut(_PIN_SW1)
_pin_sw1.direction = digitalio.Direction.INPUT
_pin_sw1.pull = digitalio.Pull.UP
right_switch = Debouncer(_pin_sw1)

pot_0 = AnalogIn(_PIN_POT0)
pot_1 = AnalogIn(_PIN_POT1)
pot_2 = AnalogIn(_PIN_POT2)

def get_pot_values() -> tuple:
    return tuple([adc.value / (2 ** 16 - 1) for adc in (pot_0, pot_1, pot_2)])

# Configure Codec
i2c = I2C(_PIN_SCL, _PIN_SDA)
codec = TLV320AIC3204(
    i2c=i2c,
    mclk=_PIN_MCLK,
    rst=_PIN_RST,
)

# Connect IN1L to Left MICPGA
codec.connect_left_input(INPUT_1, IMPEDANCE_40K)
codec.left_input_gain = 0.0  # dB

# Setup DAC Output
# codec.left_dac_volume = 0.0  # dB
codec.left_dac_enabled = True
# codec.left_dac_muted = False
codec.left_dac_to_left_line_output = True

# Setup ADC Input
codec.left_adc_volume = -12.0  # dB
codec.left_adc_enabled = True
codec.left_adc_muted = False

# Setup Passthrough Input Mixer
codec.left_input_passthrough_enabled = True
# codec.left_input_passthrough_volume = 0.0  # dB
codec.left_input_to_left_line_output = True

# Line Output
codec.left_line_output_enabled = True
codec.left_line_output_muted = False

# True Bypass
_pin_bypass = digitalio.DigitalInOut(_PIN_BYPASS)
_pin_bypass.direction = digitalio.Direction.OUTPUT
# _pin_bypass.value = True

_bypass = True
_mix = 0.0
_level = 1.0
_needs_update = True
def _update_codec(force: bool = False) -> None:
    global _needs_update
    if not force and not _needs_update:
        return
    _needs_update = False

    _pin_bypass.value = _bypass

    codec.left_dac_muted = _bypass or _mix <= 0.01 or _level <= 0.01
    codec.left_dac_volume = -63.5 * (1.0 - min(_mix * 2.0, 1.0) * _level)
    # codec.left_dac_to_left_line_output = not _bypass

    codec.left_input_passthrough_volume = -99.9 if not _bypass and _mix >= 0.99 else (-30.1 * (1.0 - min(2.0 - _mix * 2.0, 1.0) * _level)) * (not _bypass)
    # codec.left_input_to_left_line_output = _bypass or _mix <= 0.99
_update_codec()

def is_bypassed() -> bool:
    return _bypass

def bypass(value: bool|None = None) -> None:
    global _bypass, _needs_update
    value = not _bypass if value is None else value
    if value is not _bypass:
        _bypass = value
        _needs_update = True

def mix(value: float|None) -> None:
    global _mix, _needs_update
    value = min(max(value, 0.0), 1.0)
    if value != _mix:
        _mix = value
        _needs_update = True

def level(value: float) -> None:
    global _level, _needs_update
    value = min(max(value, 0.0), 1.0)
    if value != _level:
        _level = value
        _needs_update = True

# Configure I2S Bus
audio_in = I2SIn(
    bit_clock=_PIN_BCLK,
    word_select=_PIN_WCLK,
    data=_PIN_DIN,
    sample_rate=44100,
    bit_depth=16,
    samples_signed=True,
    mono=True,
)
audio_out = I2SOut(
    bit_clock=_PIN_BCLK,
    word_select=_PIN_WCLK,
    data=_PIN_DOUT,
    external_clock=True,
)

def update() -> None:
    _update_codec()
    
    for debouncer in (left_button, right_button, left_switch, right_switch):
        debouncer.update()
