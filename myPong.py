import os, sys, io
import M5
from M5 import *
import time
from hardware import I2C
from hardware import Pin
from hat import MiniEncoderCHat

# Глобальные переменные
line = None
circle = None
imageCircle = None

line_start_x = None
circle_y_limit = None
circle_x_position = None
line_end_x = None
circle_x_direction = None
circle_y_position = None
circle_y_direction = None
circle_x_limit = None
line_length = None

i2c_bus = None
encoder_hat = None
bumpLineCounter = 0
speed = 0.005
acceleration = 0.5
lineSpeed = 4
images = ["res/img/1.png", "res/img/2.png", "res/img/3.png"]


# Движение линий
def update_line_position():
    global line_start_x, line_end_x, line_length, encoder_hat
    rotary_value = encoder_hat.get_rotary_increments()
    line_start_x = line_start_x + (rotary_value * lineSpeed)

    # Ограничиваем область движения линии
    line_start_x = max(0, min(line_start_x, 130 - line_length))
    line_end_x = line_start_x + line_length

    line.setPoints(x0=line_start_x, y0=230, x1=line_end_x, y1=230)
    time.sleep(0.001)


# Движение круга
def update_circle_position():
    global circle_y_limit, circle_x_position, circle_x_direction, circle_y_position, circle_y_direction, circle_x_limit, bumpLineCounter, speed
    # Определение лимита по оси Y
    underLine = line_start_x <= circle_x_position <= line_end_x
    if (underLine and circle_y_position >= circle_y_limit):
        bumpLineCounter += 1
        print(bumpLineCounter)
        if ((bumpLineCounter % 6) == 5):
            speed *= acceleration
            print(speed)
            imageCircle = Widgets.Image(images[0], 0, 0, scale_x=1, scale_y=1)
            imageCircle.setVisible(True)
            time.sleep(1)
            imageCircle.setVisible(False)
    circle_y_limit = 225 if underLine else 250

    # Меняем направление движения по оси X
    if circle_x_position >= circle_x_limit or circle_x_position <= 0:
        circle_x_direction *= -1

    # Меняем направление движения по оси Y
    if circle_y_position >= circle_y_limit or circle_y_position <= 0:
        circle_y_direction *= -1

    circle_x_position += circle_x_direction
    circle_y_position += circle_y_direction

    circle.setCursor(x=circle_x_position, y=circle_y_position)


# Проверка на проигрыш
def check_if_circle_lost():
    global circle_x_position, circle_y_position, speed, imageCircle

    if circle_y_position >= 232:
        for _ in range(4):
            circle_x_position += circle_x_direction
            circle_y_position += circle_y_direction
            circle.setCursor(x=circle_x_position, y=circle_y_position)
            time.sleep(0.2)

        for _ in range(30):
            circle_x_position += circle_x_direction
            circle_y_position += circle_y_direction
            circle.setCursor(x=circle_x_position, y=circle_y_position)
            time.sleep(0.005)

        imageCircle = Widgets.Image(images[1], 0, 0, scale_x=1, scale_y=1)
        # M5.Lcd.show(images[1], 0, 0, 0, 0)
        imageCircle.setVisible(True)
        time.sleep(1)
        imageCircle.setVisible(False)

        time.sleep(1)
        circle_x_position, circle_y_position = 10, 10
        speed *= 2


# Инициализация
def setup():
    global line, circle, line_start_x, circle_y_limit, circle_x_position, imageCircle
    global line_end_x, circle_x_direction, circle_y_position
    global circle_y_direction, circle_x_limit, line_length, i2c_bus, encoder_hat

    M5.begin()
    line = Widgets.Line(45, 231, 95, 231, 0xffffff)
    circle = Widgets.Circle(46, 136, 4, 0xffffff, 0xffffff)

    circle_x_position = 10
    circle_y_position = 10
    circle_x_limit = 130
    circle_y_limit = 225
    circle_x_direction = 1
    circle_y_direction = 1
    line_start_x = 50
    line_end_x = 100
    line_length = 50
    line.setPoints(x0=line_start_x, y0=230, x1=line_end_x, y1=230)

    i2c_bus = I2C(1, scl=Pin(26), sda=Pin(0), freq=100000)
    encoder_hat = MiniEncoderCHat(i2c_bus, 0x42)
    encoder_hat.reset_rotary_value()


def game:
    global encoder_hat, speed
    M5.update()
    try:
        if encoder_hat.get_button_status():
            speed *= 0.8
        time.sleep(speed)
        update_circle_position()
        if encoder_hat.get_rotary_status():
            update_line_position()
        check_if_circle_lost()
    except (Exception, KeyboardInterrupt) as e:
        print(e)


# Основной цикл
def loop():
    game()
    if BtnA.isPressed():
        Power.powerOff()


if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg

            print_error_msg(e)
    except ImportError:
        print("please update to latest firmware")