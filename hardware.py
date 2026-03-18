# SPDX-FileCopyrightText: 2026 Cooper Dalrymple (@relic-se)
#
# SPDX-License-Identifier: GPLv3

import analogio
import audiobusio
import board
import busio
import digitalio
import pwmio

import adafruit_debouncer
import relic_tlv320aic3204

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

_pin_btn0 = digitalio.DigitalInOut(_PIN_BTN0)
_pin_btn0.direction = digitalio.Direction.INPUT
_pin_btn0.pull = digitalio.Pull.UP
left_button = adafruit_debouncer.Button(_pin_btn0)

_pin_btn1 = digitalio.DigitalInOut(_PIN_BTN1)
_pin_btn1.direction = digitalio.Direction.INPUT
_pin_btn1.pull = digitalio.Pull.UP
right_button = adafruit_debouncer.Button(_pin_btn1)

_pin_sw0 = digitalio.DigitalInOut(_PIN_SW0)
_pin_sw0.direction = digitalio.Direction.INPUT
_pin_sw0.pull = digitalio.Pull.UP
left_switch = adafruit_debouncer.Debouncer(_pin_sw0)

_pin_sw1 = digitalio.DigitalInOut(_PIN_SW1)
_pin_sw1.direction = digitalio.Direction.INPUT
_pin_sw1.pull = digitalio.Pull.UP
right_switch = adafruit_debouncer.Debouncer(_pin_sw1)

led = pwmio.PWMOut(_PIN_LED)
led.duty_cycle = 0

pot_0 = analogio.AnalogIn(_PIN_POT0)
pot_1 = analogio.AnalogIn(_PIN_POT1)
pot_2 = analogio.AnalogIn(_PIN_POT2)

i2c = busio.I2C(_PIN_SCL, _PIN_SDA)
codec = relic_tlv320aic3204.TLV320AIC3204(
    i2c=i2c,
    mclk=_PIN_MCLK,
    rst=_PIN_RST,
)
i2s = audiobusio.I2SOut(
    bit_clock=_PIN_BCLK,
    word_select=_PIN_WCLK,
    data=_PIN_DOUT,
)

bypass = digitalio.DigitalInOut(_PIN_BYPASS)
bypass.direction = digitalio.Direction.OUTPUT
bypass.value = True

def update() -> None:
    for debouncer in (left_button, right_button, left_switch, right_switch):
        debouncer.update()

def get_pot_values() -> tuple:
    return tuple([adc.value / (2 ** 16 - 1) for adc in (pot_0, pot_1, pot_2)])
