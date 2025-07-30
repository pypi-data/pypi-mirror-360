from contextlib import asynccontextmanager
from typing import Any

from zaber_motion import Units
from zaber_motion.ascii import Connection, Axis, Device


@asynccontextmanager
async def zaber_device(port) -> Device:
    async with Connection.open_serial_port_async(port) as connection:
        await connection.enable_alerts_async()
        devices = await connection.detect_devices_async()
        yield devices[0]


@asynccontextmanager
async def zaber_axis(port) -> Axis:
    async with zaber_device(port) as device:
        yield device.get_axis(1)


class ZaberDriver:
    """Wrapper for zaber_motion."""

    __module__ = "pyobs_zaber.ZaberDriver"

    def __init__(
        self,
        port: str = "/dev/ttyUSB1",
        speed: float = 10000,
        acceleration: float = 800,
        length_unit=Units.ANGLE_DEGREES,
        speed_unit=Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
        acceleration_unit=Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
        system_led: bool = False,
        **kwargs: Any,
    ):
        """Creates a new ZaberDriver.
        Args:
            port: USB port of the motor, usually "/dev/ttyUSB0"
            speed: velocity of the selector movement
            length_unit: unit of the length, must be from zaber-motion.Units
            speed_unit: unit of the velocity, must be from zaber-motion.Units
            system_led: whether the motor LED is active or not
        """
        self.port = port
        self.speed = speed
        self.acceleration = acceleration
        self.length_unit = length_unit
        self.speed_unit = speed_unit
        self.acceleration_unit = acceleration_unit
        self.system_led = system_led

    async def open(self) -> None:
        await self.enable_led(self.system_led)

    async def home(self) -> None:
        async with zaber_axis(self.port) as axis:
            await axis.home_async()

    async def move_by(self, length, speed=None) -> None:
        """
        Move Zaber motor by a given value.
        Args:
            length: value by which the motor moves
            speed: velocity at which the motor moves
        """
        if speed is None:
            speed = self.speed

        # move
        async with zaber_axis(self.port) as axis:
            await axis.move_relative_async(
                length,
                self.length_unit,
                velocity=speed,
                velocity_unit=self.speed_unit,
                acceleration=self.acceleration,
                acceleration_unit=self.acceleration_unit,
            )

    async def get_position(self) -> float:
        """
        Get the current position of the Zaber motor.
        """
        async with zaber_axis(self.port) as axis:
            return await axis.get_position_async(unit=self.length_unit)

    async def move_to(self, position) -> None:
        """
        Move Zaber motor to a given position.
        Args:
            position: value to which the motor moves
        """
        async with zaber_axis(self.port) as axis:
            await axis.move_absolute_async(
                position,
                self.length_unit,
                velocity=self.speed,
                velocity_unit=self.speed_unit,
                acceleration=self.acceleration,
                acceleration_unit=self.acceleration_unit,
            )

    async def enable_led(self, status: bool) -> None:
        """
        Turn on the motor's status LED.
        Args:
            status: True -> LED on, False -> LED off
        """
        async with zaber_device(self.port) as device:
            device.settings.set("system.led.enable", float(status))

    async def stop(self):
        """Stop motion."""
        async with zaber_axis(self.port) as axis:
            await axis.stop_async()
