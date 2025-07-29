import math
from pathlib import Path
from typing import List, Tuple

import rrdtool
from brasciichart import *

from GmMonitorix import (
    IMG_FORMAT, THEME_BLACK, XAXIS_CFG,
    Params, GraphSize,
    lstrip_column, min_max_last_avg, merge, pic_url, zip_plots, ceil_scaled,
    setup_riglim_pic, get_rig_lim, setup_riglim_plt, floor_scaled,
)


def fs_cgi(params: Params, db_dir: Path, out_dir: Path, cfg: dict) -> str:
    rrd = str(db_dir / 'fs.rrd')
    cfg_fs = cfg.get('fs')
    fs_list = cfg_fs.get('list')
    descs = {k.strip(): v.strip()
             for k, v in cfg_fs.get('desc').items()}
    text = ''
    for n, fs_paths in fs_list.items():
        fs_paths = list(map(lambda p: p.strip(),
                            fs_paths.strip().split(',')))
        text += fsN_cgi(params, out_dir, cfg,
                        rrd, n, fs_paths[0:8], descs)
    return text


def fsN_cgi(params: Params, out_dir: Path, cfg: dict,
            rrd: str, n: int, paths: list, descs: dict) -> str:
    xport = [
        # Filesystem usage
        f'DEF:fs0={rrd}:fs{n}_use0:AVERAGE',
        f'DEF:fs1={rrd}:fs{n}_use1:AVERAGE',
        f'DEF:fs2={rrd}:fs{n}_use2:AVERAGE',
        f'DEF:fs3={rrd}:fs{n}_use3:AVERAGE',
        f'DEF:fs4={rrd}:fs{n}_use4:AVERAGE',
        f'DEF:fs5={rrd}:fs{n}_use5:AVERAGE',
        f'DEF:fs6={rrd}:fs{n}_use6:AVERAGE',
        f'DEF:fs7={rrd}:fs{n}_use7:AVERAGE',
        'XPORT:fs0:fs0',  # 0
        'XPORT:fs1:fs1',
        'XPORT:fs2:fs2',
        'XPORT:fs3:fs3',
        'XPORT:fs4:fs4',
        'XPORT:fs5:fs5',
        'XPORT:fs6:fs6',
        'XPORT:fs7:fs7',
        # Disk I/O activity
        f'DEF:ioa0={rrd}:fs{n}_ioa0:AVERAGE',
        f'DEF:ioa1={rrd}:fs{n}_ioa1:AVERAGE',
        f'DEF:ioa2={rrd}:fs{n}_ioa2:AVERAGE',
        f'DEF:ioa3={rrd}:fs{n}_ioa3:AVERAGE',
        f'DEF:ioa4={rrd}:fs{n}_ioa4:AVERAGE',
        f'DEF:ioa5={rrd}:fs{n}_ioa5:AVERAGE',
        f'DEF:ioa6={rrd}:fs{n}_ioa6:AVERAGE',
        f'DEF:ioa7={rrd}:fs{n}_ioa7:AVERAGE',
        'XPORT:ioa0:ioa0',  # 8
        'XPORT:ioa1:ioa1',
        'XPORT:ioa2:ioa2',
        'XPORT:ioa3:ioa3',
        'XPORT:ioa4:ioa4',
        'XPORT:ioa5:ioa5',
        'XPORT:ioa6:ioa6',
        'XPORT:ioa7:ioa7',
        # Inode usage
        f'DEF:ino0={rrd}:fs{n}_ino0:AVERAGE',
        f'DEF:ino1={rrd}:fs{n}_ino1:AVERAGE',
        f'DEF:ino2={rrd}:fs{n}_ino2:AVERAGE',
        f'DEF:ino3={rrd}:fs{n}_ino3:AVERAGE',
        f'DEF:ino4={rrd}:fs{n}_ino4:AVERAGE',
        f'DEF:ino5={rrd}:fs{n}_ino5:AVERAGE',
        f'DEF:ino6={rrd}:fs{n}_ino6:AVERAGE',
        f'DEF:ino7={rrd}:fs{n}_ino7:AVERAGE',
        'XPORT:ino0:ino0',  # 16
        'XPORT:ino1:ino1',
        'XPORT:ino2:ino2',
        'XPORT:ino3:ino3',
        'XPORT:ino4:ino4',
        'XPORT:ino5:ino5',
        'XPORT:ino6:ino6',
        'XPORT:ino7:ino7',
        # Time spent in I/O activity
        f'DEF:tim0={rrd}:fs{n}_tim0:AVERAGE',
        f'DEF:tim1={rrd}:fs{n}_tim1:AVERAGE',
        f'DEF:tim2={rrd}:fs{n}_tim2:AVERAGE',
        f'DEF:tim3={rrd}:fs{n}_tim3:AVERAGE',
        f'DEF:tim4={rrd}:fs{n}_tim4:AVERAGE',
        f'DEF:tim5={rrd}:fs{n}_tim5:AVERAGE',
        f'DEF:tim6={rrd}:fs{n}_tim6:AVERAGE',
        f'DEF:tim7={rrd}:fs{n}_tim7:AVERAGE',
        'XPORT:tim0:tim0',  # 24, ms
        'XPORT:tim1:tim1',
        'XPORT:tim2:tim2',
        'XPORT:tim3:tim3',
        'XPORT:tim4:tim4',
        'XPORT:tim5:tim5',
        'XPORT:tim6:tim6',
        'XPORT:tim7:tim7',
    ]
    # --maxrows - is for an equality Max-values in graph and plot
    # https://oss.oetiker.ch/rrdtool/doc/rrdxport.en.html
    # > This works like the -w|--width parameter of rrdgraph. In fact it is
    # > exactly the same, but the parameter was renamed to describe its
    # > purpose in this module.
    # noinspection PyArgumentList
    data = rrdtool.xport('--start', f'-{params.when}',
                         '--step', '60',
                         '--maxrows', GraphSize.medium[0].split('=')[1],
                         *xport)
    data_lists = list(zip(*data['data']))
    xfrom = data['meta']['start']
    xto = data['meta']['end']

    usage_title = f'{cfg.get("graphs").get("_fs1")}'
    usage, usage_width = _usage_plt(
        params, f'{usage_title} (Percent, %)',
        cfg, xfrom=xfrom, xto=xto,
        paths=paths, descs=descs,
        usage=[list(data_lists[s]) for s in range(len(paths))])

    ioa_title = f'{cfg.get("graphs").get("_fs2")}'
    ioa, _ = _io_activity_plt(
        params, f'{ioa_title} (R+W/s)', cfg,
        xfrom=xfrom, xto=xto,
        paths=paths, descs=descs,
        io_activity=[list(data_lists[s + 8]) for s in range(len(paths))])

    usage_ioa = zip_plots(usage, usage_width, ioa)
    usage_ioa = '\n'.join(usage_ioa)

    inode_title = f'{cfg.get("graphs").get("_fs3")}'
    inode, inode_width = _inode_plt(
        params, f'{inode_title} (Percent, %)', cfg,
        xfrom=xfrom, xto=xto,
        paths=paths, descs=descs,
        inode=[list(data_lists[s + 16]) for s in range(len(paths))])

    # Support FreeBSD, OpenBSD, NetBSD "Disk data activity"
    tim_title = f'{cfg.get("graphs").get("_fs4")}'
    tim, _ = _time_plt(
        params, f'{tim_title} (msecs)', cfg,
        xfrom=xfrom, xto=xto,
        paths=paths, descs=descs,
        tim_ms=[list(data_lists[s + 24]) for s in range(len(paths))])

    inode_tim = zip_plots(inode, inode_width, tim)
    inode_tim = '\n'.join(inode_tim)

    pics_use_ioa = '\n'
    pics_ino_tim = '\n'
    if params.picUrls:
        usage_pic = _usage_pic(params, f'{usage_title}  ({params.when})',
                               cfg, out_dir, rrd, n, paths, descs)
        ioa_pic = _io_activity_pic(params, f'{ioa_title}  ({params.when})',
                                   cfg, out_dir, rrd, n, paths, descs)
        pics_use_ioa = ''.join((pic_url(usage_pic, usage_title),
                                pic_url(ioa_pic, ioa_title)))

        inode_pic = _inode_pic(params, f'{inode_title}  ({params.when})',
                               cfg, out_dir, rrd, n, paths, descs)
        tim_pic = _time_pic(params, f'{tim_title}  ({params.when})',
                            cfg, out_dir, rrd, n, paths, descs)
        pics_ino_tim = ''.join((pic_url(inode_pic, inode_title),
                                pic_url(tim_pic, tim_title)))
    return (f'{pics_use_ioa}'
            f'```{usage_title}, {ioa_title}\n'
            f'{usage_ioa}\n'
            f'```\n'
            f'{pics_ino_tim}'
            f'```{inode_title}, {tim_title}\n'
            f'{inode_tim}\n'
            f'```\n'
            f'')


LINE_COLORS = ['#EEEE44', '#44EEEE', '#44EE44', '#4444EE',
               '#448844', '#5F04B4', '#EE44EE', '#FFA500']
PLOT_COLORS = [lightyellow, lightcyan, lightgreen, lightblue,
               green, magenta, lightmagenta, yellow]


def _usage_pic(params: Params, title: str, conf: dict,
               out_dir: Path, rrd, n,
               paths: list, descs: dict) -> Path:
    graphv = [
        f'DEF:fs0={rrd}:fs{n}_use0:AVERAGE',
        f'DEF:fs1={rrd}:fs{n}_use1:AVERAGE',
        f'DEF:fs2={rrd}:fs{n}_use2:AVERAGE',
        f'DEF:fs3={rrd}:fs{n}_use3:AVERAGE',
        f'DEF:fs4={rrd}:fs{n}_use4:AVERAGE',
        f'DEF:fs5={rrd}:fs{n}_use5:AVERAGE',
        f'DEF:fs6={rrd}:fs{n}_use6:AVERAGE',
        f'DEF:fs7={rrd}:fs{n}_use7:AVERAGE',
    ]
    colorN = 0
    for pn, p in enumerate(paths):
        desc = f'{descs.get(p, p)}'
        if p == '/':
            color = '#EE4444'
        elif p == 'swap':
            color = '#CCCCCC'
        elif p == '/boot':
            color = '#666666'
        else:
            color = LINE_COLORS[colorN]
            colorN += 1
        graphv += (
            f'LINE2:fs{pn}{color}:{desc[0:23]:<23}',
            f'GPRINT:fs{pn}:LAST:Cur\\: %4.1lf%%',
            f'GPRINT:fs{pn}:MIN: Min\\: %4.1lf%%',
            f'GPRINT:fs{pn}:MAX: Max\\: %4.1lf%%\\n'
        )
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('fs'), 0))
    pic = out_dir / f'fs{n}_use.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Percent (%)',
                   *riglim,
                   *GraphSize.medium,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _usage_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        paths: list, descs: dict, usage: list
) -> Tuple[List[str], int]:
    legend = []
    for use in usage:
        legend.append(min_max_last_avg(use))
    colors = []
    colorN = 0
    for p in paths:
        if p == '/':
            colors.append(lightred)
        elif p == 'swap':
            colors.append(white)
        elif p == '/boot':
            colors.append(lightgray)
        else:
            colors.append(PLOT_COLORS[colorN])
            colorN += 1

    cfg = {'colors': colors, 'offset': 2, 'trim': False,
           'format': '{:>3.0f}% ', 'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim(conf.get('fs'), 0),
                              floor_scaled(min(map(lambda t: t[0], legend))),
                              ceil_scaled(max(map(lambda t: t[1], legend))))
    merge(riglim, cfg)
    merge(GraphSize.medium_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot(usage, cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    legend = [(f'{min_:3.0f}', f'{max_:3.0f}', f'{last:3.0f}', _)
              for min_, max_, last, _ in legend]
    min_len = max(map(lambda t: len(t[0]), legend))
    max_len = max(map(lambda t: len(t[1]), legend))
    last_len = max(map(lambda t: len(t[2]), legend))
    values_width = min_len + max_len + last_len + 3 * 5  # 3 * ' xxx:'
    for n, p in enumerate(paths):
        desc = f'{descs.get(p, p)[0:width - values_width]}'
        plt.append(
            f'{colors[n]}{desc}{reset}'
            + (f' Cur:{legend[n][2]:>{last_len}}'
               f' Min:{legend[n][0]:>{min_len}}'
               f' Max:{legend[n][1]:>{max_len}}').rjust(width - len(desc))
        )
    return plt, width


def _io_activity_pic(params: Params, title: str, conf: dict,
                     out_dir: Path, rrd, n,
                     paths: list, descs: dict) -> Path:
    graphv = [
        f'DEF:ioa0={rrd}:fs{n}_ioa0:AVERAGE',
        f'DEF:ioa1={rrd}:fs{n}_ioa1:AVERAGE',
        f'DEF:ioa2={rrd}:fs{n}_ioa2:AVERAGE',
        f'DEF:ioa3={rrd}:fs{n}_ioa3:AVERAGE',
        f'DEF:ioa4={rrd}:fs{n}_ioa4:AVERAGE',
        f'DEF:ioa5={rrd}:fs{n}_ioa5:AVERAGE',
        f'DEF:ioa6={rrd}:fs{n}_ioa6:AVERAGE',
        f'DEF:ioa7={rrd}:fs{n}_ioa7:AVERAGE',
    ]
    colorN = 0
    for pn, p in enumerate(paths):
        desc = f'{descs.get(p, p)}'
        if p == '/':
            color = '#EE4444'
        elif p == 'swap':
            color = '#CCCCCC'
        elif p == '/boot':
            color = '#666666'
        else:
            color = LINE_COLORS[colorN]
            colorN += 1
        graphv += (
            f'LINE2:ioa{pn}{color}:{desc[0:23]:<23}',
            f'GPRINT:ioa{pn}:LAST:Cur\\: %4.0lf',
            f'GPRINT:ioa{pn}:MIN: Min\\: %4.0lf',
            f'GPRINT:ioa{pn}:MAX: Max\\: %4.0lf\\n'
        )
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('fs'), 1))
    pic = out_dir / f'fs{n}_ioa.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Reads+Writes/s',
                   *riglim,
                   *GraphSize.medium,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _io_activity_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        paths: list, descs: dict, io_activity: list
) -> Tuple[List[str], int]:
    legend = []
    for ioa in io_activity:
        legend.append(min_max_last_avg(ioa))
    colors = []
    colorN = 0
    for p in paths:
        if p == '/':
            colors.append(lightred)
        elif p == 'swap':
            colors.append(white)
        elif p == '/boot':
            colors.append(lightgray)
        else:
            colors.append(PLOT_COLORS[colorN])
            colorN += 1

    cfg = {'colors': colors, 'offset': 2, 'trim': False,
           'format': '{:>5.0f} ', 'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim(conf.get('fs'), 1),
                              floor_scaled(min(map(lambda t: t[0], legend))),
                              ceil_scaled(max(map(lambda t: t[1], legend))))
    merge(riglim, cfg)
    merge(GraphSize.medium_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot(io_activity, cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    f = '.0f'
    legend = [(f'{min_:{f}}', f'{max_:{f}}', f'{last:{f}}', _)
              for min_, max_, last, _ in legend]
    min_len = max(map(lambda t: len(t[0]), legend))
    max_len = max(map(lambda t: len(t[1]), legend))
    last_len = max(map(lambda t: len(t[2]), legend))
    values_width = min_len + max_len + last_len + 3 * 5  # 3 * ' xxx:'
    for n, p in enumerate(paths):
        desc = f'{descs.get(p, p)[0:width - values_width]}'
        plt.append(
            f'{colors[n]}{desc}{reset}'
            + (f' Cur:{legend[n][2]:>{last_len}}'
               f' Min:{legend[n][0]:>{min_len}}'
               f' Max:{legend[n][1]:>{max_len}}').rjust(width - len(desc))
        )
    return plt, width


def _inode_pic(params: Params, title: str, conf: dict,
               out_dir: Path, rrd, n,
               paths: list, descs: dict) -> Path:
    graphv = [
        f'DEF:ino0={rrd}:fs{n}_ino0:AVERAGE',
        f'DEF:ino1={rrd}:fs{n}_ino1:AVERAGE',
        f'DEF:ino2={rrd}:fs{n}_ino2:AVERAGE',
        f'DEF:ino3={rrd}:fs{n}_ino3:AVERAGE',
        f'DEF:ino4={rrd}:fs{n}_ino4:AVERAGE',
        f'DEF:ino5={rrd}:fs{n}_ino5:AVERAGE',
        f'DEF:ino6={rrd}:fs{n}_ino6:AVERAGE',
        f'DEF:ino7={rrd}:fs{n}_ino7:AVERAGE',
    ]
    colorN = 0
    for pn, p in enumerate(paths):
        desc = f'{descs.get(p, p)}'
        if p == '/':
            color = '#EE4444'
        elif p == 'swap':
            color = '#CCCCCC'
        elif p == '/boot':
            color = '#666666'
        else:
            color = LINE_COLORS[colorN]
            colorN += 1
        graphv += (
            f'LINE2:ino{pn}{color}:{desc[0:23]:<23}',
            f'GPRINT:ino{pn}:LAST:Cur\\: %4.1lf%%',
            f'GPRINT:ino{pn}:MIN: Min\\: %4.1lf%%',
            f'GPRINT:ino{pn}:MAX: Max\\: %4.1lf%%\\n'
        )
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('fs'), 2))
    pic = out_dir / f'fs{n}_ino.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   # TODO: Use config rigid n limits
                   f'--upper-limit=100',
                   '--vertical-label=Percent (%)',
                   *riglim,
                   *GraphSize.medium,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _inode_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        paths: list, descs: dict, inode: list
) -> Tuple[List[str], int]:
    legend = []
    for ino in inode:
        legend.append(min_max_last_avg(ino))
    colors = []
    colorN = 0
    for p in paths:
        if p == '/':
            colors.append(lightred)
        elif p == 'swap':
            colors.append(white)
        elif p == '/boot':
            colors.append(lightgray)
        else:
            colors.append(PLOT_COLORS[colorN])
            colorN += 1

    cfg = {'colors': colors, 'offset': 2, 'trim': False,
           'format': '{:>3.0f}% ', 'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim(conf.get('fs'), 2),
                              floor_scaled(min(map(lambda t: t[0], legend))),
                              ceil_scaled(max(map(lambda t: t[1], legend))))
    merge(riglim, cfg)
    merge(GraphSize.medium_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot(inode, cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    legend = [(f'{min_:3.0f}', f'{max_:3.0f}', f'{last:3.0f}', _)
              for min_, max_, last, _ in legend]
    min_len = max(map(lambda t: len(t[0]), legend))
    max_len = max(map(lambda t: len(t[1]), legend))
    last_len = max(map(lambda t: len(t[2]), legend))
    values_width = min_len + max_len + last_len + 3 * 5  # 3 * ' xxx:'
    for n, p in enumerate(paths):
        desc = f'{descs.get(p, p)[0:width - values_width]}'
        plt.append(
            f'{colors[n]}{desc}{reset}'
            + (f' Cur:{legend[n][2]:>{last_len}}'
               f' Min:{legend[n][0]:>{min_len}}'
               f' Max:{legend[n][1]:>{max_len}}').rjust(width - len(desc))
        )
    return plt, width


def _time_pic(params: Params, title: str, conf: dict,
              out_dir: Path, rrd, n,
              paths: list, descs: dict) -> Path:
    graphv = [
        f'DEF:tim0={rrd}:fs{n}_tim0:AVERAGE',
        f'DEF:tim1={rrd}:fs{n}_tim1:AVERAGE',
        f'DEF:tim2={rrd}:fs{n}_tim2:AVERAGE',
        f'DEF:tim3={rrd}:fs{n}_tim3:AVERAGE',
        f'DEF:tim4={rrd}:fs{n}_tim4:AVERAGE',
        f'DEF:tim5={rrd}:fs{n}_tim5:AVERAGE',
        f'DEF:tim6={rrd}:fs{n}_tim6:AVERAGE',
        f'DEF:tim7={rrd}:fs{n}_tim7:AVERAGE',
        'CDEF:stim0=tim0,1000,/',
        'CDEF:stim1=tim1,1000,/',
        'CDEF:stim2=tim2,1000,/',
        'CDEF:stim3=tim3,1000,/',
        'CDEF:stim4=tim4,1000,/',
        'CDEF:stim5=tim5,1000,/',
        'CDEF:stim6=tim6,1000,/',
        'CDEF:stim7=tim7,1000,/',
    ]
    colorN = 0
    for pn, p in enumerate(paths):
        desc = f'{descs.get(p, p)}'
        if p == '/':
            color = '#EE4444'
        elif p == 'swap':
            color = '#CCCCCC'
        elif p == '/boot':
            color = '#666666'
        else:
            color = LINE_COLORS[colorN]
            colorN += 1
        graphv += (
            f'LINE2:tim{pn}{color}:{desc[0:23]:<23}',
            f'GPRINT:stim{pn}:LAST:Cur\\: %4.1lfs',
            f'GPRINT:stim{pn}:MIN:Min\\: %4.1lfs',
            f'GPRINT:stim{pn}:MAX:Max\\: %4.1lfs\\n'
        )
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('fs'), 3))
    pic = out_dir / f'fs{n}_tim.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Milliseconds',
                   *riglim,
                   *GraphSize.medium,
                   *graphv,
                   *THEME_BLACK)
    return pic


def lbl_msecs(msecs):
    return '' if msecs is None \
        else '0' if math.ceil(msecs) == 0 \
        else f'{(msecs / 1000):.1f}k' if msecs > 100 \
        else f'{msecs:.0f}'


def _time_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        paths: list, descs: dict, tim_ms: list
) -> Tuple[List[str], int]:
    legend = []
    for tim in tim_ms:
        legend.append(min_max_last_avg(tim))
    colors = []
    colorN = 0
    for p in paths:
        if p == '/':
            colors.append(lightred)
        elif p == 'swap':
            colors.append(white)
        elif p == '/boot':
            colors.append(lightgray)
        else:
            colors.append(PLOT_COLORS[colorN])
            colorN += 1

    cfg = {'colors': colors, 'offset': 2, 'trim': False,
           'format': '{:>6} ', 'format_func': lbl_msecs,
           'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim(conf.get('fs'), 3),
                              floor_scaled(min(map(lambda t: t[0], legend))),
                              ceil_scaled(max(map(lambda t: t[1], legend))))
    merge(riglim, cfg)
    merge(GraphSize.medium_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot(tim_ms, cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    legend = [(lbl_msecs(min_), lbl_msecs(max_), lbl_msecs(last), _)
              for min_, max_, last, _ in legend]
    min_len = max(map(lambda t: len(t[0]), legend))
    max_len = max(map(lambda t: len(t[1]), legend))
    last_len = max(map(lambda t: len(t[2]), legend))
    values_width = min_len + max_len + last_len + 3 * 5  # 3 * ' xxx:'
    for n, p in enumerate(paths):
        desc = f'{descs.get(p, p)[0:width - values_width]}'
        plt.append(
            f'{colors[n]}{desc}{reset}'
            + (f' Cur:{legend[n][2]:>{last_len}}'
               f' Min:{legend[n][0]:>{min_len}}'
               f' Max:{legend[n][1]:>{max_len}}').rjust(width - len(desc))
        )
    return plt, width
