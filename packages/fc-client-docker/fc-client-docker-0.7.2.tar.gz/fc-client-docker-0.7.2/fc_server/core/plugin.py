# -*- coding: utf-8 -*-
#
# Copyright 2021-2022 NXP
# Copyright 2024-2025 NXP
#
# SPDX-License-Identifier: MIT


from abc import ABC, abstractmethod


class FCPlugin(ABC):
    """
    Base plugin of FC
    Detail framework plugins should realize next interfaces
    `init`, `schedule`, `force_kick_off`, `lock_info`
    """

    def __init__(self):
        super().__init__()
        self.schedule_tick = 0
        self.schedule_interval = 1

    @abstractmethod
    async def init(self, driver):
        pass

    @abstractmethod
    async def schedule(self, driver):
        pass

    @abstractmethod
    async def force_kick_off(self, resource):
        pass

    @abstractmethod
    async def lock_info(self, _):
        pass
