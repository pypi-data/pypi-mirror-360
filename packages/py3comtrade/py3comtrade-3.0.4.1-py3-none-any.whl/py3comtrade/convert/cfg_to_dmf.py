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
from py3comtrade.model import Analog, AnalogChannel, ChannelIdx, Configure, DMF
from py3comtrade.model.bus import Bus
from py3comtrade.model.primary_equipments import ACVBranch
from py3comtrade.model.type import AnalogFlag, AnalogType, PhaseCode

def split_channel_name(name: str) -> tuple[str, str]:
    return name.split("_")



def cfg_to_dmf(config: Configure) -> DMF:
    dmf = DMF()
    dmf.station_name = config.header.station_name
    dmf.rec_dev_name = config.header.recorder_name
    if analog_num := len(config.analogs)//4==0:
        for i in range(0,analog_num,4):
            a = config.analogs[i]
            b = config.analogs[i + 1]
            c = config.analogs[i + 2]
            n = config.analogs[i + 3]
            # TODO: 判断通道的类型，电压、电流、直流
            # TODO: 获取通道对应的一次设备名称，如果不存在就新建，存在返回对应的对象。
            if a.name in ["电压","Ua"]:
                bus = Bus()
                bus.idx = len(dmf.buses) if dmf.buses else 0
                bus.name = a.ccbm if a.ccbm else a.name
                bus.v_rtg = 220
                bus.acv_chn = ACVBranch(ua_idx=a.idx_cfg, ub_idx=b.idx_cfg, uc_idx=c.idx_cfg, un_idx=n.idx_cfg)
                bus.analog_chn.append(ChannelIdx(idx_cfg=a.idx_cfg))
                bus.analog_chn.append(ChannelIdx(idx_cfg=b.idx_cfg))
                bus.analog_chn.append(ChannelIdx(idx_cfg=c.idx_cfg))
                bus.analog_chn.append(ChannelIdx(idx_cfg=n.idx_cfg))
                dmf.buses.append(bus)

    for analog in config.analogs:
        pass


if __name__ == '__main__':
    file_path = r'/tests/data/hjz.cfg'
    from py3comtrade.reader.config_reader import config_reader
    cfg = config_reader(file_path)
    dmf = cfg_to_dmf(cfg)
