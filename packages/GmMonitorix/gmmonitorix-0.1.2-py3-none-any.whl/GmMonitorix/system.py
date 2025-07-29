from pathlib import Path
from typing import Tuple, List

import rrdtool
from brasciichart import *

from . import (
    THEME_BLACK, IMG_FORMAT, COLOR_RESET, XAXIS_CFG, GraphSize, Params,
    pic_url, lbl_size, min_max_last_avg, merge, lstrip_column,
    ceil_scaled, floor_scaled, total_mem_kbytes, zip_plots,
    setup_riglim_pic, setup_riglim_plt, get_rig_lim,
)


def system_cgi(params: Params, db_dir: Path, out_dir: Path, cfg: dict) -> str:
    rrd = str(db_dir / 'system.rrd')
    #
    xport = [
        # system load
        f'DEF:load1={rrd}:system_load1:AVERAGE',
        f'DEF:load5={rrd}:system_load5:AVERAGE',
        f'DEF:load15={rrd}:system_load15:AVERAGE',
        'XPORT:load1:load1',  # 0
        'XPORT:load5:load5',
        'XPORT:load15:load15',
        # memory
        # TODO: Support OpenBSD, NetBSD with m_mused, m_macti only
        f'DEF:mtotl={rrd}:system_mtotl:AVERAGE',
        f'DEF:mbuff={rrd}:system_mbuff:AVERAGE',
        f'DEF:mcach={rrd}:system_mcach:AVERAGE',
        f'DEF:mfree={rrd}:system_mfree:AVERAGE',
        f'DEF:macti={rrd}:system_macti:AVERAGE',
        f'DEF:minac={rrd}:system_minac:AVERAGE',
        'CDEF:m_mtotl=mtotl,1024,*',
        'CDEF:m_mbuff=mbuff,1024,*',
        'CDEF:m_mcach=mcach,1024,*',
        'CDEF:m_mused=m_mtotl,mfree,1024,*,-,m_mbuff,-,m_mcach,-',
        'CDEF:m_macti=macti,1024,*',
        'CDEF:m_minac=minac,1024,*',
        'XPORT:m_mbuff:m_mbuff',  # 3
        'XPORT:m_mcach:m_mcach',
        'XPORT:m_mused:m_mused',
        'XPORT:m_macti:m_macti',
        'XPORT:m_minac:m_minac',
        # processes
        f'DEF:nproc={rrd}:system_nproc:AVERAGE',
        f'DEF:npslp={rrd}:system_npslp:AVERAGE',
        f'DEF:nprun={rrd}:system_nprun:AVERAGE',
        f'DEF:npwio={rrd}:system_npwio:AVERAGE',
        f'DEF:npzom={rrd}:system_npzom:AVERAGE',
        f'DEF:npstp={rrd}:system_npstp:AVERAGE',
        f'DEF:npswp={rrd}:system_npswp:AVERAGE',
        f'XPORT:nproc:nproc',  # 8
        f'XPORT:npslp:npslp',
        f'XPORT:nprun:nprun',
        f'XPORT:npwio:npwio',
        f'XPORT:npzom:npzom',
        f'XPORT:npstp:npstp',
        f'XPORT:npswp:npswp',
        # entropy
        f'DEF:entropy={rrd}:system_entrop:AVERAGE',  #
        f'XPORT:entropy:entropy',  # 15
        # uptime
        f'DEF:uptime={rrd}:system_uptime:AVERAGE',
        f'CDEF:uptime_days=uptime,86400,/',
        f'XPORT:uptime_days:uptime_days',  # 16
    ]
    # noinspection PyArgumentList
    data = rrdtool.xport('--start', f'-{params.when}',
                         '--step', '60',
                         *xport)
    data_lists = list(zip(*data['data']))
    xfrom = data['meta']['start']
    xto = data['meta']['end']

    load_title = f'{cfg.get("graphs").get("_system1")}'
    load, load_width = _load_plt(
        params, load_title, cfg, xfrom=xfrom, xto=xto,
        load1=list(data_lists[0]),
        load5=list(data_lists[1]),
        load15=list(data_lists[2]))

    total_mem_kb = total_mem_kbytes()
    mem_title = f'{cfg.get("graphs").get("_system2")} ({total_mem_kb // 1024}MB)'
    mem, mem_width = _mem_plt(
        params, mem_title, xfrom=xfrom, xto=xto,
        total_mem_b=total_mem_kb * 1024,
        mem_buf=list(data_lists[3]),
        mem_cache=list(data_lists[4]),
        mem_used=list(data_lists[5]),
        mem_act=list(data_lists[6]),
        mem_inact=list(data_lists[7]))

    proc_title = f'{cfg.get("graphs").get("_system3")}'
    proc, _ = _processes_plt(
        params, proc_title, cfg, xfrom=xfrom, xto=xto,
        p_total=list(data_lists[8]),
        p_sleeping=list(data_lists[9]),
        p_running=list(data_lists[10]),
        p_wait_io=list(data_lists[11]),
        p_zombie=list(data_lists[12]),
        p_stopped=list(data_lists[13]),
        p_paging=list(data_lists[14]))

    entropy_title = f'{cfg.get("graphs").get("_system4")}'
    entropy, _ = _entropy_plt(params, entropy_title, cfg,
                              xfrom=xfrom, xto=xto,
                              entropy=list(data_lists[15]))

    uptime_title = f'{cfg.get("graphs").get("_system5")}'
    uptime, _ = _uptime_plt(params, f'{uptime_title} (days)', cfg,
                            xfrom=xfrom, xto=xto,
                            uptime=list(data_lists[16]))
    #
    load_proc = '\n'.join(zip_plots(load, load_width, proc))
    mem_ent_upt = '\n'.join(zip_plots(mem, mem_width, entropy + [''] + uptime))
    #
    pics_load = ''
    if params.picUrls:
        load_pic = _load_pic(params, f'{load_title}  ({params.when})',
                             cfg, out_dir, rrd)
        proc_pic = _processes_pic(params, f'{proc_title}  ({params.when})',
                                  cfg, out_dir, rrd)
        pics_load = ''.join((pic_url(load_pic, load_title),
                             pic_url(proc_pic, proc_title)))
    pics_mem = '\n'
    if params.picUrls:
        mem_pic = _mem_pic(params, f'{mem_title}  ({params.when})',
                           out_dir, rrd, total_mem_kb * 1024)
        ent_pic = _entropy_pic(params, f'{entropy_title}  ({params.when})',
                               cfg, out_dir, rrd)
        upt_pic = _uptime_pic(params, f'{uptime_title}  ({params.when})',
                              cfg, out_dir, rrd)
        pics_mem = ''.join((pic_url(mem_pic, mem_title),
                            pic_url(ent_pic, entropy_title),
                            pic_url(upt_pic, uptime_title)))
    return (f'{pics_load}'
            f'```{load_title}, {proc_title}\n'
            f'{load_proc}\n'
            f'```\n'
            #
            f'{pics_mem}'
            f'```{mem_title}, {entropy_title}\n'
            f'{mem_ent_upt}\n'
            f'```\n')


def _load_pic(params: Params, title: str,
              conf: dict, out_dir: Path, rrd: str) -> Path:
    graphv = [
        f'DEF:load1={rrd}:system_load1:AVERAGE',
        f'DEF:load5={rrd}:system_load5:AVERAGE',
        f'DEF:load15={rrd}:system_load15:AVERAGE',
        'AREA:load1#4444EE: 1 min average',
        'GPRINT:load1:LAST:  Current\\: %4.2lf',
        'GPRINT:load1:AVERAGE:   Average\\: %4.2lf',
        'GPRINT:load1:MIN:   Min\\: %4.2lf',
        'GPRINT:load1:MAX:   Max\\: %4.2lf\\n',
        'LINE1:load1#0000EE',
        'LINE1:load5#EEEE00: 5 min average',
        'GPRINT:load5:LAST:  Current\\: %4.2lf',
        'GPRINT:load5:AVERAGE:   Average\\: %4.2lf',
        'GPRINT:load5:MIN:   Min\\: %4.2lf',
        'GPRINT:load5:MAX:   Max\\: %4.2lf\\n',
        'LINE1:load15#00EEEE:15 min average',
        'GPRINT:load15:LAST:  Current\\: %4.2lf',
        'GPRINT:load15:AVERAGE:   Average\\: %4.2lf',
        'GPRINT:load15:MIN:   Min\\: %4.2lf',
        'GPRINT:load15:MAX:   Max\\: %4.2lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('system'), 0))
    pic = out_dir / f'system_load.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Load average',
                   *GraphSize.main,
                   *riglim,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _load_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        load1: list, load5: list, load15: list,
) -> Tuple[List[str], int]:
    min1, max1, last1, avg1 = min_max_last_avg(load1)
    min5, max5, last5, avg5 = min_max_last_avg(load5)
    min15, max15, last15, avg15 = min_max_last_avg(load15)

    cfg = {'colors': [lightblue, lightyellow, lightcyan],
           'offset': 2, 'format': '{:6.2f} ', 'trim': False,
           'xfrom': xfrom, 'xto': xto}
    riglm = setup_riglim_plt(*get_rig_lim(conf.get('system'), 0),
                             min(min1, min5, min15),
                             ceil_scaled(max(max1, max5, max15)))
    merge(riglm, cfg)
    merge(GraphSize.main_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    plt = plot([load1, load5, load15], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    min1, max1, last1, avg1 = (f'{min1:.2f}', f'{max1:.2f}',
                               f'{last1:.2f}', f'{avg1:.2f}')
    min5, max5, last5, avg5 = (f'{min5:.2f}', f'{max5:.2f}',
                               f'{last5:.2f}', f'{avg5:.2f}')
    min15, max15, last15, avg15 = (f'{min15:.2f}', f'{max15:.2f}',
                                   f'{last15:.2f}', f'{avg15:.2f}')
    min_len = max(len(min1), len(min5), len(min15))
    max_len = max(len(max1), len(max5), len(max15))
    last_len = max(len(last1), len(last5), len(last15))
    avg_len = max(len(avg1), len(avg5), len(avg15))
    plt.append(
        f' {lightblue}1 min avg{reset}'
        f' Cur: {last1:<{last_len}} Avg: {avg1:<{avg_len}}'
        f' Min: {min1:<{min_len}} Max: {max1:<{max_len}}'
        f''.ljust(width + COLOR_RESET))
    plt.append(
        f' {lightyellow}5 min avg{reset}'
        f' Cur: {last5:<{last_len}} Avg: {avg5:<{avg_len}}'
        f' Min: {min5:<{min_len}} Max: {max5:<{max_len}}'
        f''.ljust(width + COLOR_RESET))
    plt.append(
        f'{lightcyan}15 min avg{reset}'
        f' Cur: {last15:<{last_len}} Avg: {avg15:<{avg_len}}'
        f' Min: {min15:<{min_len}} Max: {max15:<{max_len}}'
        f''.ljust(width + COLOR_RESET))

    return plt, width


def _processes_pic(params: Params, title: str,
                   conf: dict, out_dir: Path, rrd: str) -> Path:
    graphv = [
        f'DEF:nproc={rrd}:system_nproc:AVERAGE',
        f'DEF:npslp={rrd}:system_npslp:AVERAGE',
        f'DEF:nprun={rrd}:system_nprun:AVERAGE',
        f'DEF:npwio={rrd}:system_npwio:AVERAGE',
        f'DEF:npzom={rrd}:system_npzom:AVERAGE',
        f'DEF:npstp={rrd}:system_npstp:AVERAGE',
        f'DEF:npswp={rrd}:system_npswp:AVERAGE',
        'AREA:npslp#448844:Sleeping',
        'GPRINT:npslp:LAST:             Current\\:%5.0lf\\n',
        'LINE2:npwio#EE44EE:Wait I/O',
        'GPRINT:npwio:LAST:             Current\\:%5.0lf\\n',
        'LINE2:npzom#00EEEE:Zombie',
        'GPRINT:npzom:LAST:               Current\\:%5.0lf\\n',
        'LINE2:npstp#EEEE00:Stopped',
        'GPRINT:npstp:LAST:              Current\\:%5.0lf\\n',
        'LINE2:npswp#0000EE:Paging',
        'GPRINT:npswp:LAST:               Current\\:%5.0lf\\n',
        'LINE2:nprun#EE0000:Running',
        'GPRINT:nprun:LAST:              Current\\:%5.0lf\\n',
        'COMMENT: \\n',
        'LINE2:nproc#888888:Total Processes',
        'GPRINT:nproc:LAST:      Current\\:%5.0lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('system'), 2))
    pic = out_dir / f'system_processes.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Processes',
                   *riglim,
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _processes_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        p_total: list, p_sleeping: list, p_running: list, p_wait_io: list,
        p_zombie: list, p_stopped: list, p_paging: list
) -> Tuple[List[str], int]:
    # @formatter:off
    min_total,    max_total, last_total,    _ = min_max_last_avg(p_total)
    min_sleeping, _,         last_sleeping, _ = min_max_last_avg(p_sleeping)
    min_running,  _,         last_running,  _ = min_max_last_avg(p_running)
    min_wait_io,  _,         last_wait_io,  _ = min_max_last_avg(p_wait_io)
    min_zombie,   _,         last_zombie,   _ = min_max_last_avg(p_zombie)
    min_stopped,  _,         last_stopped,  _ = min_max_last_avg(p_stopped)
    min_paging,   _,         last_paging,   _ = min_max_last_avg(p_paging)
    # @formatter:on
    ceil_max_total = ceil_scaled(max_total)
    ceil_max_total_len = len(f'{ceil_max_total}')
    cfg = {'colors': [lightgray, green, lightred, lightmagenta,
                      lightcyan, lightyellow, blue],
           'offset': 2,
           'format': f'{{:>{ceil_max_total_len}.0f}} ', 'trim': False,
           'xfrom': xfrom, 'xto': xto}
    riglm = setup_riglim_plt(
        *get_rig_lim(conf.get('system'), 2),
        min(min_total, min_sleeping, min_running, min_wait_io,
            min_zombie, min_stopped, min_paging),
        ceil_max_total)
    merge(riglm, cfg)
    merge(GraphSize.small_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot([p_total, p_sleeping, p_running, p_wait_io,
                p_zombie, p_stopped, p_paging], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))
    plt += (
        f'',
        f'{green}Sleeping{reset}         Cur: {last_sleeping:<.0f}',
        f'{lightmagenta}Wait I/O{reset}         Cur: {last_wait_io:<.0f}',
        f'{lightcyan}Zombie{reset}           Cur: {last_zombie:<.0f}',
        f'{lightyellow}Stopped{reset}          Cur: {last_stopped:<.0f}',
        f'{blue}Paging{reset}           Cur: {last_paging:<.0f}',
        f'{lightred}Running{reset}          Cur: {last_running:<.0f}',
        f'',
        f'{lightgray}Total Processes{reset}  Cur: {last_total:<.0f}'
    )
    return plt, width


def _mem_pic(params: Params, title: str,
             out_dir: Path, rrd: str, total_mem_bytes: int) -> Path:
    graphv = [
        f'DEF:mtotl={rrd}:system_mtotl:AVERAGE',
        f'DEF:mbuff={rrd}:system_mbuff:AVERAGE',
        f'DEF:mcach={rrd}:system_mcach:AVERAGE',
        f'DEF:mfree={rrd}:system_mfree:AVERAGE',
        f'DEF:macti={rrd}:system_macti:AVERAGE',
        f'DEF:minac={rrd}:system_minac:AVERAGE',
        'CDEF:m_mtotl=mtotl,1024,*',
        'CDEF:m_mbuff=mbuff,1024,*',
        'CDEF:m_mcach=mcach,1024,*',
        'CDEF:m_mused=m_mtotl,mfree,1024,*,-,m_mbuff,-,m_mcach,-',
        'CDEF:m_macti=macti,1024,*',
        'CDEF:m_minac=minac,1024,*',
        'CDEF:allvalues=mtotl,mbuff,mcach,mfree,macti,minac,+,+,+,+,+',
        'AREA:m_mused#EE4444:Used',
        'AREA:m_mcach#44EE44:Cached',
        'AREA:m_mbuff#CCCCCC:Buffers',
        'AREA:m_macti#E29136:Active',
        'AREA:m_minac#448844:Inactive',
        'LINE2:m_minac#008800',
        'LINE2:m_macti#E29136',
        'LINE2:m_mbuff#CCCCCC',
        'LINE2:m_mcach#00EE00',
        'LINE2:m_mused#EE0000',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    pic = out_dir / f'system_memory.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=bytes',
                   f'--upper-limit={total_mem_bytes}',
                   '--lower-limit=0',
                   '--rigid',
                   '--base=1024',
                   *GraphSize.main,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _mem_plt(
        params: Params, title: str, /,
        xfrom: int = None, xto: int = None, *,
        total_mem_b: int,
        mem_buf: list, mem_cache: list, mem_used: list,
        mem_act: list, mem_inact: list
) -> Tuple[List[str], int]:
    cfg = {'colors': [lightred, lightgreen, white, lightyellow, green],
           'offset': 2, 'min': 0, 'max': total_mem_b, 'trim': False,
           'format': '{:>6} ', 'format_func': lbl_size,
           'xfrom': xfrom, 'xto': xto}
    merge(GraphSize.main_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot([mem_used, mem_cache, mem_buf, mem_act, mem_inact], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))
    plt.append(' ' * width)
    plt.append(
        f'{lightred}Used{reset}  {lightgreen}Cached{reset}'
        f'  {white}Buffers{reset}  {lightyellow}Active{reset}'
        f'  {green}Inactive{reset}'.center(width + 5 * COLOR_RESET))

    return plt, width


def _entropy_pic(params: Params, title: str,
                 conf: dict, out_dir: Path, rrd: str) -> Path:
    graphv = [
        f'DEF:entropy={rrd}:system_entrop:AVERAGE',
        'LINE2:entropy#EEEE00:Entropy',
        'GPRINT:entropy:LAST:              Current\\:%5.0lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('system'), 3))
    pic = out_dir / f'system_entropy.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Size',
                   *riglim,
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _entropy_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        entropy: list
) -> Tuple[List[str], int]:
    min_ent, max_ent, last_ent, _ = min_max_last_avg(entropy)

    cfg = {'colors': [lightyellow], 'offset': 2,
           'format': '{:>4.0f} ', 'trim': False,
           'xfrom': xfrom, 'xto': xto}
    riglm = setup_riglim_plt(*get_rig_lim(conf.get('system'), 3),
                             floor_scaled(min_ent), ceil_scaled(max_ent))
    merge(riglm, cfg)
    merge(GraphSize.small_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    cfg['xrows'] = 1
    #
    plt = plot([entropy], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))
    plt.append(
        f'{lightyellow}Entropy{reset}'
        + f'Cur: {last_ent:.0f}'.rjust(width - len('Entropy'))
    )
    return plt, width


def _uptime_pic(params: Params, title: str, conf: dict,
                out_dir: Path, rrd: str) -> Path:
    graphv = [
        f'DEF:uptime={rrd}:system_uptime:AVERAGE',
        # TODO: Support uptime units: minutes, hours
        f'CDEF:uptime_days=uptime,86400,/',
        'LINE2:uptime_days#EE44EE:Uptime',
        'GPRINT:uptime_days:LAST:               Current\\:%5.1lf\\n',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim(conf.get('system'), 4))
    pic = out_dir / f'system_uptime.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Days',
                   *riglim,
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _uptime_plt(
        params: Params, title: str, conf: dict, /,
        xfrom: int = None, xto: int = None, *,
        uptime: list
) -> Tuple[List[str], int]:
    min_upt, max_upt, last_upt, _ = min_max_last_avg(uptime)

    cfg = {'colors': [lightmagenta], 'offset': 2,
           'format': '{:>4.0f} ', 'trim': False,
           'xfrom': xfrom, 'xto': xto}
    riglm = setup_riglim_plt(*get_rig_lim(conf.get('system'), 4),
                             floor_scaled(min_upt), ceil_scaled(max_upt))
    merge(riglm, cfg)
    merge(GraphSize.small_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    cfg['xrows'] = 1
    #
    plt = plot([uptime], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    plt.insert(0, title.center(width))
    plt.append(
        f'{lightmagenta}Uptime{reset}'
        + f'Cur: {last_upt:.1f}'.rjust(width - len('Uptime'))
    )
    return plt, width
