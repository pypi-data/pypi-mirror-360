from pathlib import Path
from typing import Tuple, List

import rrdtool
from brasciichart import *

from . import (
    IMG_FORMAT, THEME_BLACK, XAXIS_CFG,
    GraphSize, Params,
    pic_url, min_max_last_avg, merge, lstrip_column, ceil_scaled,
    zip_plots, setup_riglim_pic, setup_riglim_plt,
    get_rig_lim, floor_scaled,
)


def icecast_cgi(params: Params, db_dir: Path, out_dir: Path, cfg: dict) -> str:
    rrd = str(db_dir / 'icecast.rrd')
    cfg_ic = cfg.get('icecast')
    urls = cfg_ic.get('list').split(',')
    descs = list(map(lambda i: cfg_ic.get('desc').get(i.strip()).split(','),
                     urls))
    text = ''
    for n, url in enumerate(urls):
        text += icecastX_cgi(params, out_dir, cfg,
                             rrd, n, url.strip(), descs[n])
    return text


def icecastX_cgi(params: Params, out_dir: Path, cfg: dict,
                 rrd, n, url, desc: List[str]) -> str:
    xport = [
        # listeners
        f'DEF:ice_mp0_ls={rrd}:icecast{n}_mp0_ls:AVERAGE',
        f'DEF:ice_mp1_ls={rrd}:icecast{n}_mp1_ls:AVERAGE',
        f'DEF:ice_mp2_ls={rrd}:icecast{n}_mp2_ls:AVERAGE',
        f'DEF:ice_mp3_ls={rrd}:icecast{n}_mp3_ls:AVERAGE',
        f'DEF:ice_mp4_ls={rrd}:icecast{n}_mp4_ls:AVERAGE',
        f'DEF:ice_mp5_ls={rrd}:icecast{n}_mp5_ls:AVERAGE',
        f'DEF:ice_mp6_ls={rrd}:icecast{n}_mp6_ls:AVERAGE',
        f'DEF:ice_mp7_ls={rrd}:icecast{n}_mp7_ls:AVERAGE',
        f'DEF:ice_mp8_ls={rrd}:icecast{n}_mp8_ls:AVERAGE',
        'XPORT:ice_mp0_ls:ice_mp0_ls',  # 0
        'XPORT:ice_mp1_ls:ice_mp1_ls',
        'XPORT:ice_mp2_ls:ice_mp2_ls',
        'XPORT:ice_mp3_ls:ice_mp3_ls',
        'XPORT:ice_mp4_ls:ice_mp4_ls',
        'XPORT:ice_mp5_ls:ice_mp5_ls',
        'XPORT:ice_mp6_ls:ice_mp6_ls',
        'XPORT:ice_mp7_ls:ice_mp7_ls',
        'XPORT:ice_mp8_ls:ice_mp8_ls',
        # bitrate
        f'DEF:ice_mp0_br={rrd}:icecast{n}_mp0_br:AVERAGE',
        f'DEF:ice_mp1_br={rrd}:icecast{n}_mp1_br:AVERAGE',
        f'DEF:ice_mp2_br={rrd}:icecast{n}_mp2_br:AVERAGE',
        f'DEF:ice_mp3_br={rrd}:icecast{n}_mp3_br:AVERAGE',
        f'DEF:ice_mp4_br={rrd}:icecast{n}_mp4_br:AVERAGE',
        f'DEF:ice_mp5_br={rrd}:icecast{n}_mp5_br:AVERAGE',
        f'DEF:ice_mp6_br={rrd}:icecast{n}_mp6_br:AVERAGE',
        f'DEF:ice_mp7_br={rrd}:icecast{n}_mp7_br:AVERAGE',
        f'DEF:ice_mp8_br={rrd}:icecast{n}_mp8_br:AVERAGE',
        'XPORT:ice_mp0_br:ice_mp0_br',  # 0
        'XPORT:ice_mp1_br:ice_mp1_br',
        'XPORT:ice_mp2_br:ice_mp2_br',
        'XPORT:ice_mp3_br:ice_mp3_br',
        'XPORT:ice_mp4_br:ice_mp4_br',
        'XPORT:ice_mp5_br:ice_mp5_br',
        'XPORT:ice_mp6_br:ice_mp6_br',
        'XPORT:ice_mp7_br:ice_mp7_br',
        'XPORT:ice_mp8_br:ice_mp8_br',
    ]
    # noinspection PyArgumentList
    data = rrdtool.xport('--start', f'-{params.when}',
                         '--step', '60',
                         *xport)
    data_lists = list(zip(*data['data']))
    xfrom = data['meta']['start']
    xto = data['meta']['end']
    #
    listeners_title = f'{cfg.get("graphs").get("_icecast1")}'
    listeners, listeners_width = _listeners_plt(
        params, f'{listeners_title}', cfg, xfrom=xfrom, xto=xto,
        mount_points=desc,
        listeners=[list(data_lists[s]) for s in range(len(desc))])

    bitrate_title = f'{cfg.get("graphs").get("_icecast2")}'
    bitrate, _ = _bitrate_plt(
        params, bitrate_title, cfg, xfrom=xfrom, xto=xto,
        mount_points=desc,
        bitrate=[list(data_lists[s + 9]) for s in range(len(desc))])

    icecast = '\n'.join(zip_plots(listeners, listeners_width, bitrate))

    pics = '\n'
    if params.picUrls:
        listeners_pic = _listeners_pic(
            params, f'{cfg.get("graphs").get("_icecast1")}  ({params.when})',
            cfg, out_dir, rrd, n, desc)
        bitrate_pic = _bitrate_pic(
            params, f'{cfg.get("graphs").get("_icecast2")}  ({params.when})',
            cfg, out_dir, rrd, n, desc)
        pics = ''.join((pic_url(listeners_pic, listeners_title),
                        pic_url(bitrate_pic, bitrate_title)))

    return (f'{pics}'
            f'```{listeners_title}, {bitrate_title}\n'
            f'{icecast}\n'
            f'```\n')


LINE_COLORS = ['#EEEE44', '#44EEEE', '#44EE44', '#4444EE', '#448844',
               '#EE4444', '#EE44EE', '#FFA500', "#444444",]
PLOT_COLORS = [lightyellow, lightcyan, lightgreen, lightblue, green,
               lightred, lightmagenta, yellow, lightgray]


def _listeners_pic(params: Params, title: str, conf: dict,
                   out_dir: Path, rrd, n, desc: List[str]) -> Path:
    graphv = [
        f'DEF:ice_mp0={rrd}:icecast{n}_mp0_ls:AVERAGE',
        f'DEF:ice_mp1={rrd}:icecast{n}_mp1_ls:AVERAGE',
        f'DEF:ice_mp2={rrd}:icecast{n}_mp2_ls:AVERAGE',
        f'DEF:ice_mp3={rrd}:icecast{n}_mp3_ls:AVERAGE',
        f'DEF:ice_mp4={rrd}:icecast{n}_mp4_ls:AVERAGE',
        f'DEF:ice_mp5={rrd}:icecast{n}_mp5_ls:AVERAGE',
        f'DEF:ice_mp6={rrd}:icecast{n}_mp6_ls:AVERAGE',
        f'DEF:ice_mp7={rrd}:icecast{n}_mp7_ls:AVERAGE',
        f'DEF:ice_mp8={rrd}:icecast{n}_mp8_ls:AVERAGE',
    ]
    colorN = 0
    for pn, p in enumerate(desc):
        color = LINE_COLORS[colorN]
        colorN += 1
        graphv += (
            f'LINE2:ice_mp{pn}{color}:{p.strip()[0:15]:<15}',
            f'GPRINT:ice_mp{pn}:LAST:Cur\\: %4.0lf',
            f'GPRINT:ice_mp{pn}:AVERAGE: Avg\\: %4.0lf',
            f'GPRINT:ice_mp{pn}:MIN: Min\\: %4.0lf',
            f'GPRINT:ice_mp{pn}:MAX: Max\\: %4.0lf\\n'
        )
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('icecast'), 0))
    pic = out_dir / f'ice{n}_ls.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Listeners',
                   *riglim,
                   *GraphSize.medium,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _listeners_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        mount_points: list, listeners: list
) -> Tuple[List[str], int]:
    legend = []
    for listener in listeners:
        legend.append(min_max_last_avg(listener))
    colors = []
    colorN = 0
    for _ in mount_points:
        colors.append(PLOT_COLORS[colorN])
        colorN += 1

    cfg = {'colors': colors, 'offset': 2, 'trim': False,
           'format': '{:>3.1f} ', 'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim(conf.get('icecast'), 0),
                              floor_scaled(min(map(lambda t: t[0], legend))),
                              ceil_scaled(max(map(lambda t: t[1], legend))))
    merge(riglim, cfg)
    merge(GraphSize.medium_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot(listeners, cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    legend = [(f'{min_:.0f}', f'{max_:.0f}', f'{last:.0f}', f'{avg:.0f}')
              for min_, max_, last, avg in legend]
    min_len = max(map(lambda t: len(t[0]), legend))
    max_len = max(map(lambda t: len(t[1]), legend))
    last_len = max(map(lambda t: len(t[2]), legend))
    avg_len = max(map(lambda t: len(t[3]), legend))
    values_width = min_len + max_len + last_len + avg_len + 14  # ' C: A: Mn: Mx:'
    for n, p in enumerate(mount_points):
        desc = f'{p.strip()[0:width - values_width]}'
        plt.append(
            f'{colors[n]}{desc}{reset}'
            + (f' C:{legend[n][2]:>{last_len}}'
               f' A:{legend[n][3]:>{avg_len}}'
               f' Mn:{legend[n][0]:>{min_len}}'
               f' Mx:{legend[n][1]:>{max_len}}').rjust(width - len(desc))
        )
    return plt, width


def _bitrate_pic(params: Params, title: str,  conf: dict,
                 out_dir: Path, rrd: str, n, desc: List[str]) -> Path:
    graphv = [
        f'DEF:ice_mp0={rrd}:icecast{n}_mp0_br:AVERAGE',
        f'DEF:ice_mp1={rrd}:icecast{n}_mp1_br:AVERAGE',
        f'DEF:ice_mp2={rrd}:icecast{n}_mp2_br:AVERAGE',
        f'DEF:ice_mp3={rrd}:icecast{n}_mp3_br:AVERAGE',
        f'DEF:ice_mp4={rrd}:icecast{n}_mp4_br:AVERAGE',
        f'DEF:ice_mp5={rrd}:icecast{n}_mp5_br:AVERAGE',
        f'DEF:ice_mp6={rrd}:icecast{n}_mp6_br:AVERAGE',
        f'DEF:ice_mp7={rrd}:icecast{n}_mp7_br:AVERAGE',
        f'DEF:ice_mp8={rrd}:icecast{n}_mp8_br:AVERAGE',
    ]
    colorN = 0
    for pn, p in enumerate(desc):
        color = LINE_COLORS[colorN]
        colorN += 1
        graphv += (
            f'LINE2:ice_mp{pn}{color}:{p.strip()[0:15]:<15}',
            f'GPRINT:ice_mp{pn}:LAST:Cur\\: %4.0lf',
            f'GPRINT:ice_mp{pn}:AVERAGE: Avg\\: %4.0lf',
            f'GPRINT:ice_mp{pn}:MIN: Min\\: %4.0lf',
            f'GPRINT:ice_mp{pn}:MAX: Max\\: %4.0lf\\n'
        )
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('icecast'), 1))
    pic = out_dir / f'ice{n}_br.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Bitrate',
                   *riglim,
                   *GraphSize.medium,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _bitrate_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        mount_points: list, bitrate: list
) -> Tuple[List[str], int]:
    legend = []
    for br in bitrate:
        legend.append(min_max_last_avg(br))
    colors = []
    colorN = 0
    for _ in mount_points:
        colors.append(PLOT_COLORS[colorN])
        colorN += 1

    cfg = {'colors': colors, 'offset': 2, 'trim': False,
           'format': '{:>3.0f} ', 'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim(conf.get('icecast'), 0),
                              floor_scaled(min(map(lambda t: t[0], legend))),
                              ceil_scaled(max(map(lambda t: t[1], legend))))
    merge(riglim, cfg)
    merge(GraphSize.medium_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot(bitrate, cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    legend = [(f'{min_:.0f}', f'{max_:.0f}', f'{last:.0f}', f'{avg:.0f}')
              for min_, max_, last, avg in legend]
    min_len = max(map(lambda t: len(t[0]), legend))
    max_len = max(map(lambda t: len(t[1]), legend))
    last_len = max(map(lambda t: len(t[2]), legend))
    avg_len = max(map(lambda t: len(t[3]), legend))
    values_width = min_len + max_len + last_len + avg_len + 14  # ' C: A: Mn: Mx:'
    for n, p in enumerate(mount_points):
        desc = f'{p.strip()[0:width - values_width]}'
        plt.append(
            f'{colors[n]}{desc}{reset}'
            + (f' C:{legend[n][2]:>{last_len}}'
               f' A:{legend[n][3]:>{avg_len}}'
               f' Mn:{legend[n][0]:>{min_len}}'
               f' Mx:{legend[n][1]:>{max_len}}').rjust(width - len(desc))
        )
    return plt, width
