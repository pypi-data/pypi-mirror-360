import logging
from typing import Any, List, Optional

from pyobs.interfaces import IMotion
from pyobs.interfaces.IMode import IMode
from pyobs.modules import Module
from pyobs.utils.enums import MotionStatus

from pyobs_zaber.zaberdriver import ZaberDriver


class ZaberModeSelector(Module, IMode, IMotion):
    """Class for the Selection of Modus with a linear Motor (e.g. Spectroscopy or Photometry)."""

    __module__ = "pyobs_zaber.ZaberModeSelector"

    def __init__(
        self,
        modes: dict,
        **kwargs: Any,
    ):
        """Creates a new ZaberModeSelector.
        Args:
            modes: dictionary of available modes in the form {name: position}
        """
        Module.__init__(self, **kwargs)

        # check
        if self.comm is None:
            logging.warning("No comm module given!")

        self.driver = ZaberDriver(**kwargs)
        self.modes = modes
        self.current_mode = 'undefined'

    async def list_modes(self, **kwargs: Any) -> List[str]:
        """List available modes.

        Returns:
            List of available modes.
        """
        return list(self.modes.keys())

    async def set_mode(self, mode: str, **kwargs) -> None:
        """Set the current mode.

        Args:
            mode: Name of mode to set.

        Raises:
            ValueError: If an invalid mode was given.
            MoveError: If mode selector cannot be moved.
        """
        available_modes = await self.list_modes()
        if mode in available_modes:
            if self.current_mode == mode:
                logging.info("Mode %s already selected.", mode)
            else:
                logging.info("Moving mode selector ...")
                await self.driver.move_to(self.modes[mode])
                logging.info("Mode %s ready.", mode)
                self.current_mode = mode
        else:
            logging.warning("Unknown mode %s. Available modes are: %s", mode, available_modes)

    async def get_mode(self, **kwargs: Any) -> str:
        """Get currently set mode.

        Returns:
            Name of currently set mode.
        """
        return self.current_mode

    async def init(self, **kwargs: Any) -> None:
        """Initialize device.

        Raises:
            InitError: If device could not be initialized.
        """
        await self.driver.home()

    async def park(self, **kwargs: Any) -> None:
        """Park device.

        Raises:
            ParkError: If device could not be parked.
        """
        await self.driver.home()

    async def get_motion_status(self, device: Optional[str] = None, **kwargs: Any) -> MotionStatus:
        """Returns current motion status.

        Args:
            device: Name of device to get status for, or None.

        Returns:
            A string from the Status enumerator.
        """
        logging.error("Not implemented")
        return MotionStatus.ERROR

    async def stop_motion(self, device: Optional[str] = None, **kwargs: Any) -> None:
        """Stop the motion.

        Args:
            device: Name of device to stop, or None for all.
        """
        logging.error("Not implemented")

    async def is_ready(self, **kwargs: Any) -> bool:
        """Returns the device is "ready", whatever that means for the specific device.

        Returns:
            Whether device is ready
        """
        return True
