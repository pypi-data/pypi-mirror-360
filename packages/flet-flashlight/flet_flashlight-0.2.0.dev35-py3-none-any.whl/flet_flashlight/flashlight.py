import asyncio

import flet as ft

from .exceptions import *

__all__ = ["Flashlight"]


@ft.control("Flashlight")
class Flashlight(ft.Service):
    """
    A control to use FlashLight. Works on iOS and Android. Based on torch_light Flutter widget (https://pub.dev/packages/torch_light).

    Note:
        This control is a non-visual and should be added to `page.services` list before it can be used.
    """

    on = False
    """
    Whether the flashlight is currently turned on.
    """

    on_error: ft.OptionalControlEventHandler["Flashlight"] = None
    """
    Fires when an error occurs.
    
    The `data` property of the event handler argument contains information on the error.
    """

    async def turn_on_async(self):
        """
        Turns the flashlight on.
        """
        r = await self._invoke_method_async("on")
        if r is True:
            self.on = True
        else:  # error occured
            error_type = r.get("error_type")
            error_msg = r.get("error_msg")
            if error_type == "EnableTorchExistentUserException":
                raise FlashlightEnableExistentUserException(error_msg)
            elif error_type == "EnableTorchNotAvailableException":
                raise FlashlightEnableNotAvailableException(error_msg)
            else:
                raise FlashlightEnableException(error_msg)

    def turn_on(self):
        """
        Turns the flashlight on.
        """
        asyncio.create_task(self.turn_on_async())

    async def turn_off_async(self):
        """
        Turns the flashlight off.
        """
        r = await self._invoke_method_async("off")
        if r is True:
            self.on = False
        else:  # error occured
            error_type = r.get("error_type")
            error_msg = r.get("error_msg")
            if error_type == "DisableTorchExistentUserException":
                raise FlashlightDisableExistentUserException(error_msg)
            elif error_type == "DisableTorchNotAvailableException":
                raise FlashlightDisableNotAvailableException(error_msg)
            else:
                raise FlashlightDisableException(error_msg)

    def turn_off(self):
        """
        Turns the flashlight off.
        """
        asyncio.create_task(self.turn_off_async())

    async def toggle_async(self):
        """
        Toggles the flashlight on and off.
        """
        if self.on:
            await self.turn_off_async()
        await self.turn_on_async()

    def toggle(self):
        """
        Toggles the flashlight on and off.
        """
        asyncio.create_task(self.toggle_async())

    async def is_available_async(self):
        """
        Checks if the flashlight is available on the device.
        """
        r = await self._invoke_method_async("is_available")
        if r is bool:
            return r
        else:  # error occured
            error_msg = r.get("error_msg")
            raise FlashlightException(error_msg)
