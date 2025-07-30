from RPi import GPIO  # type: ignore

from bluer_ugv.swallow.session.classical.push_button import ClassicalPushButton
from bluer_ugv.swallow.session.classical.keyboard import ClassicalKeyboard
from bluer_ugv.swallow.session.classical.leds import ClassicalLeds
from bluer_ugv.swallow.session.classical.mousepad import ClassicalMousePad
from bluer_ugv.swallow.session.classical.motor.rear import ClassicalRearMotors
from bluer_ugv.swallow.session.classical.motor.steering import ClassicalSteeringMotor
from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint
from bluer_ugv.logger import logger


class ClassicalSession:
    def __init__(self):
        self.leds = ClassicalLeds()

        self.setpoint = ClassicalSetPoint(
            leds=self.leds,
        )

        self.mousepad = ClassicalMousePad(
            leds=self.leds,
            setpoint=self.setpoint,
        )

        self.keyboard = ClassicalKeyboard(
            setpoint=self.setpoint,
        )

        self.push_button = ClassicalPushButton(
            leds=self.leds,
        )

        self.steering = ClassicalSteeringMotor(
            setpoint=self.setpoint,
            leds=self.leds,
        )

        self.rear = ClassicalRearMotors(
            setpoint=self.setpoint,
            leds=self.leds,
        )

        logger.info(f"{self.__class__.__name__}: created...")

    def cleanup(self):
        for thing in [
            self.rear,
            self.steering,
        ]:
            thing.cleanup()

        GPIO.cleanup()

        logger.info(f"{self.__class__.__name__}.cleanup")

    def initialize(self) -> bool:
        try:
            GPIO.setmode(GPIO.BCM)
        except Exception as e:
            logger.error(e)
            return False

        return all(
            thing.initialize()
            for thing in [
                self.push_button,
                self.leds,
                self.steering,
                self.rear,
            ]
        )

    def update(self) -> bool:
        return all(
            thing.update()
            for thing in [
                self.keyboard,
                self.push_button,
                self.steering,
                self.rear,
                self.setpoint,
                self.leds,
            ]
        )
