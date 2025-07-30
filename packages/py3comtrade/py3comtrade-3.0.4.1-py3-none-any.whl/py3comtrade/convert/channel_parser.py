#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (c) [2019] [name of copyright holder]
#  [py3comtrade] is licensed under Mulan PSL v2.
#  You can use this software according to the terms and conditions of the Mulan
#  PSL v2.
#  You may obtain a copy of Mulan PSL v2 at:
#           http://license.coscl.org.cn/MulanPSL2
#  THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY
#  KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#  NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
#  See the Mulan PSL v2 for more details.
from typing import Union

from py3comtrade.model import Analog, Digital
from py3comtrade.model.type import PhaseCode


class ChannelParser:
    """
    通道属性解析器
    """
    def __init__(self, channel: Union[Analog, Digital]):
        self.name = channel.name
        self.phase = channel.phase
        self.ccbm = channel.ccbm

    def is_phase(self)-> bool:
        if self.phase is None or self.phase == PhaseCode.NO_PHASE:
            return False
        return True

    def is_ccbm(self)-> bool:
        if self.ccbm is None or self.ccbm == "":
            return False
        else:
            self.ccbm.strip("_")
        return  True

    def split_name(self)-> tuple[str, str]:
        pass
