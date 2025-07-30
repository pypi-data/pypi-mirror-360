import keyboard

from bluer_sbc.session.functions import reply_to_bash

from bluer_ugv.swallow.session.classical.setpoint import ClassicalSetPoint
from bluer_ugv.logger import logger

bash_keys = {
    "i": "exit",
    "o": "shutdown",
    "p": "reboot",
    "u": "update",
}

BLUER_UGV_STEERING_SETPOINT = 50


class ClassicalKeyboard:
    def __init__(
        self,
        setpoint: ClassicalSetPoint,
    ):
        logger.info(
            "{}: {}".format(
                self.__class__.__name__,
                ", ".join(
                    [f"{key}:{action}" for key, action in bash_keys.items()],
                ),
            )
        )

        self.setpoint = setpoint

    def update(self) -> bool:
        for key, event in bash_keys.items():
            if keyboard.is_pressed(key):
                reply_to_bash(event)
                return False

        if keyboard.is_pressed(" "):
            self.setpoint.stop()

        if keyboard.is_pressed("x"):
            self.setpoint.start()

        if keyboard.is_pressed("a"):
            self.setpoint.put(
                what="steering",
                value=BLUER_UGV_STEERING_SETPOINT,
            )
        elif keyboard.is_pressed("d"):
            self.setpoint.put(
                what="steering",
                value=-BLUER_UGV_STEERING_SETPOINT,
            )
        else:
            self.setpoint.put(
                what="steering",
                value=0,
                log=False,
            )

        if keyboard.is_pressed("s"):
            self.setpoint.put(
                what="speed",
                value=self.setpoint.get(what="speed") - 10,
            )

        if keyboard.is_pressed("w"):
            self.setpoint.put(
                what="speed",
                value=self.setpoint.get(what="speed") + 10,
            )

        return True
