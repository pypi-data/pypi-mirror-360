#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2021-2022, 2025 NXP
#
# SPDX-License-Identifier: MIT


import asyncio
import logging
from importlib import import_module

import fc_server.management.common as _
from fc_server.core.config import Config
from fc_server.plugins.utils.lava import Lava


class LavaManagement(Lava):
    def __init__(self):
        super().__init__()

        self.__framework_plugins = [
            import_module("fc_server.plugins." + framework).Plugin(
                Config.frameworks_config[framework]
            )
            for framework in Config.registered_frameworks
        ]

    async def action(self):
        recover_devices = [
            device["hostname"]
            for device in await self.lava_get_devices()
            if device["hostname"] in Config.managed_resources
            and device["health"] in ("Maintenance",)
        ]

        if Config.default_framework == "lava":
            # reset all frameworks' control on that device
            for framework in self.__framework_plugins:
                if framework.__module__.split(".")[-1] != "lava":
                    await asyncio.gather(
                        *[
                            framework.force_kick_off(device)
                            for device, _ in recover_devices
                        ]
                    )

            # online lava device
            await asyncio.gather(
                *[self.lava_online_devices(device) for device in recover_devices]
            )
        else:
            await asyncio.gather(
                *[self.lava_online_devices(device) for device in recover_devices]
            )

        logging.info("Recover lava devices done.")


if __name__ == "__main__":
    asyncio.run(LavaManagement().action())
