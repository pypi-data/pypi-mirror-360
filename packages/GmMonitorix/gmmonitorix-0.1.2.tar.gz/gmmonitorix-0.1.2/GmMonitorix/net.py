from pathlib import Path
from typing import Tuple, List

import rrdtool
from brasciichart import *

from . import (
    IMG_FORMAT, THEME_BLACK, LBL_UNITS, COLOR_RESET, XAXIS_CFG,
    GraphSize, Params,
    pic_url, lbl_size, min_max_last_avg, merge, lstrip_column, ceil_scaled,
    zip_plots, get_rig_lim_desc, setup_riglim_pic, setup_riglim_plt,
)


def net_cgi(params: Params, db_dir: Path, out_dir: Path, cfg: dict) -> str:
    rrd = str(db_dir / 'net.rrd')
    cfg_net = cfg.get('net')
    ifaces = cfg_net.get('list').split(',')
    descs = list(map(lambda i: cfg_net.get('desc').get(i.strip()).split(','),
                     ifaces))
    text = ''
    for n, iface in enumerate(ifaces):
        text += netX_cgi(params, out_dir, cfg,
                         rrd, n, iface.strip(), descs[n])
    return text


def netX_cgi(params: Params, out_dir: Path, cfg: dict,
             rrd, n, iface, desc: List[str]) -> str:
    xport = [
        # traffic
        f'DEF:in={rrd}:net{n}_bytes_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_bytes_out:AVERAGE',
        'CDEF:allvalues=in,out,+',
        'CDEF:K_in=in,1024,/',
        'CDEF:K_out=out,1024,/',
        'XPORT:in:in',  # 0
        'XPORT:out:out',
        'XPORT:K_in:K_in',
        'XPORT:K_out:K_out',
        # packets
        f'DEF:pin={rrd}:net{n}_packs_in:AVERAGE',
        f'DEF:pout={rrd}:net{n}_packs_out:AVERAGE',
        'CDEF:p_in=pin',
        'CDEF:p_out=pout,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:p_out=pout',
        'XPORT:p_in:p_in',  # 4
        'XPORT:p_out:p_out',
        # errors
        f'DEF:ein={rrd}:net{n}_error_in:AVERAGE',
        f'DEF:eout={rrd}:net{n}_error_out:AVERAGE',
        'CDEF:e_in=ein',
        'CDEF:e_out=eout,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:e_out=eout',
        'XPORT:e_in:e_in',  # 6
        'XPORT:e_out:e_out',
    ]
    # noinspection PyArgumentList
    data = rrdtool.xport('--start', f'-{params.when}',
                         '--step', '60',
                         *xport)
    data_lists = list(zip(*data['data']))
    xfrom = data['meta']['start']
    xto = data['meta']['end']
    #
    net_title = f'{cfg.get("graphs").get("_net1")} {desc[0]} ({iface})'
    net, net_width = _traffic_plt(
        params, f'{net_title} (bytes/s)', desc, xfrom=xfrom, xto=xto,
        in_b=list(data_lists[0]), in_kb=list(data_lists[2]),
        out_b=list(data_lists[1]), out_kb=list(data_lists[3]))

    packs_title = f'{cfg.get("graphs").get("_net2")} {desc[0]} ({iface})'
    packs, _ = _packets_plt(
        params, packs_title, desc, xfrom=xfrom, xto=xto,
        p_in=list(data_lists[4]), p_out=list(data_lists[5]))

    errs_title = f'{cfg.get("graphs").get("_net3")} {desc[0]} ({iface})'
    errs, _ = _errors_plt(
        params, errs_title, desc, xfrom=xfrom, xto=xto,
        e_in=list(data_lists[6]), e_out=list(data_lists[7]))

    net_packs_errs = '\n'.join(zip_plots(net, net_width, packs + [''] + errs))

    pics = '\n'
    if params.picUrls:
        net_pic = _traffic_pic(
            params, f'{net_title}  ({params.when})',
            desc, out_dir, rrd, n)
        packs_pic = _packets_pic(
            params, f'{cfg.get("graphs").get("_net2")}  ({params.when})\n'
                    f'{desc[0]} ({iface})',
            desc, cfg, out_dir, rrd, n)
        errs_pic = _errors_pic(
            params, f'{cfg.get("graphs").get("_net3")}  ({params.when})\n'
                    f'{desc[0]} ({iface})',
            desc, cfg, out_dir, rrd, n)
        pics = ''.join((pic_url(net_pic, net_title),
                        pic_url(packs_pic, packs_title),
                        pic_url(errs_pic, errs_title)))

    return (f'{pics}'
            f'```{net_title}, {packs_title}, {errs_title}\n'
            f'{net_packs_errs}\n'
            f'```\n')


def _traffic_pic(params: Params, title: str, desc: List[str],
                 out_dir: Path, rrd, n) -> Path:
    # TODO: Support net traffic bit/s
    graphv = [
        f'DEF:in={rrd}:net{n}_bytes_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_bytes_out:AVERAGE',
        'CDEF:allvalues=in,out,+',
        'CDEF:B_in=in',
        'CDEF:B_out=out',
        'CDEF:K_in=B_in,1024,/',
        'CDEF:K_out=B_out,1024,/',
        'AREA:B_in#44EE44:KB/s Input',
        'GPRINT:K_in:LAST:     Current\\: %5.0lf',
        'GPRINT:K_in:AVERAGE: Average\\: %5.0lf',
        'GPRINT:K_in:MIN:    Min\\: %5.0lf',
        'GPRINT:K_in:MAX:    Max\\: %5.0lf\\n',
        'AREA:B_out#4444EE:KB/s Output',
        'GPRINT:K_out:LAST:    Current\\: %5.0lf',
        'GPRINT:K_out:AVERAGE: Average\\: %5.0lf',
        'GPRINT:K_out:MIN:    Min\\: %5.0lf',
        'GPRINT:K_out:MAX:    Max\\: %5.0lf\\n',
        'AREA:B_out#4444EE:',
        'AREA:B_in#44EE44:',
        'LINE1:B_out#0000EE',
        'LINE1:B_in#00EE00',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim_desc(desc))
    pic = out_dir / f'net_traffic_{n}.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=bytes/s',
                   *riglim,
                   *GraphSize.main,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _traffic_plt(
        params: Params, title: str, desc: List[str], /,
        xfrom: int = None, xto: int = None, *,
        in_b: list, in_kb: list,
        out_b: list, out_kb: list
) -> Tuple[List[str], int]:
    min_in, max_in, last_in, avg_in = min_max_last_avg(in_kb)
    min_out, max_out, last_out, avg_out = min_max_last_avg(out_kb)

    min_in_b, max_in_b, _, _ = min_max_last_avg(in_b)
    min_out_b, max_out_b, _, _ = min_max_last_avg(out_b)
    #
    max_ = lbl_size(max(max_in_b, max_out_b)).split(' ')
    max_scaled = ceil_scaled(float(max_[0]))
    unit_idx = LBL_UNITS.index(max_[1]) if max_[1] else 0
    max_scaled = max_scaled if not max_[1] else max_scaled * (1024 ** unit_idx)

    cfg = {'colors': [lightgreen, lightblue],
           'offset': 2, 'trim': False,
           'format': '{:>6} ', 'format_func': lbl_size,
           'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(*get_rig_lim_desc(desc), 0, max_scaled)
    merge(riglim, cfg)
    merge(GraphSize.main_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    #
    plt = plot([in_b, out_b], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))

    min_in, max_in, last_in, avg_in = (
        f'{min_in:.0f}', f'{max_in:.0f}', f'{last_in:.0f}', f'{avg_in:.0f}')
    min_out, max_out, last_out, avg_out = (
        f'{min_out:.0f}', f'{max_out:.0f}', f'{last_out:.0f}', f'{avg_out:.0f}')

    min_len = max(len(min_in), len(min_out))
    max_len = max(len(max_in), len(max_out))
    last_len = max(len(last_in), len(last_out))
    avg_len = max(len(avg_in), len(avg_out))
    plt += (
        f'{lightgreen}KB/s Input{reset} '
        f'  Cur: {last_in:<{last_len}}  Avg: {avg_in:<{avg_len}}'
        f'  Min: {min_in:<{min_len}}  Max: {max_in:<{max_len}}'
        f''.center(width + COLOR_RESET),
        #
        f'{lightblue}KB/s Output{reset}'
        f'  Cur: {last_out:<{last_len}}  Avg: {avg_out:<{avg_len}}'
        f'  Min: {min_out:<{min_len}}  Max: {max_out:<{max_len}}'
        f''.center(width + COLOR_RESET),
    )
    return plt, width


def _packets_pic(params: Params, title: str, desc: List[str], cfg: dict,
                 out_dir: Path, rrd: str, n) -> Path:
    graphv = [
        f'DEF:in={rrd}:net{n}_packs_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_packs_out:AVERAGE',
        'CDEF:p_in=in',
        'CDEF:p_out=out,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:p_out=out',
        'AREA:p_in#44EE44:Input',
        'AREA:p_out#4444EE:Output',
        'AREA:p_out#4444EE:',
        'AREA:p_in#44EE44:',
        'LINE1:p_out#0000EE',
        'LINE1:p_in#00EE00',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim_desc(desc))
    pic = out_dir / f'net_packs_{n}.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Packets/s',
                   *riglim,
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _packets_plt(
        params: Params, title: str, desc: List[str], /,
        xfrom: int = None, xto: int = None, *,
        p_in: list, p_out: list
) -> Tuple[List[str], int]:
    _, max_p_in, _, _ = min_max_last_avg(p_in)
    _, max_p_out, _, _ = min_max_last_avg(p_out)

    cfg = {'colors': [lightgreen, lightblue], 'offset': 2,
           'format': '{:>5.0f} ', 'trim': False,
           'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(
        *get_rig_lim_desc(desc),
        0, ceil_scaled(max(max_p_in or 0, max_p_out or 0)))
    merge(riglim, cfg)
    merge(GraphSize.small_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    cfg['xrows'] = 1
    #
    plt = plot([p_in, p_out], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))
    plt.append(
        f'{lightgreen}Input{reset}'
        + f'{lightblue}Output{reset}'.rjust(width - len('Input') + COLOR_RESET),
    )
    return plt, width


def _errors_pic(params: Params, title: str, desc: List[str], cfg: dict,
                out_dir: Path, rrd: str, n) -> Path:
    graphv = [
        f'DEF:in={rrd}:net{n}_error_in:AVERAGE',
        f'DEF:out={rrd}:net{n}_error_out:AVERAGE',
        'CDEF:e_in=in',
        'CDEF:e_out=out,-1,*' if cfg.get('netstat_mode') == 'separated'
        else 'CDEF:e_out=out',
        'AREA:e_in#44EE44:Input',
        'AREA:e_out#4444EE:Output',
        'AREA:e_out#4444EE:',
        'AREA:e_in#44EE44:',
        'LINE1:e_out#0000EE',
        'LINE1:e_in#00EE00',
    ]
    if params.when == '1day':
        graphv.append('--x-grid=HOUR:1:HOUR:6:HOUR:6:0:%R')
    riglim = setup_riglim_pic(*get_rig_lim_desc(desc))
    pic = out_dir / f'net_errs_{n}.{params.when}.{IMG_FORMAT}'
    rrdtool.graphv(str(pic), '--start', f'-{params.when}',
                   '--step', '60',
                   '--imgformat', IMG_FORMAT.upper(),
                   f'--title={title}',
                   '--vertical-label=Errors/s',
                   *riglim,
                   *GraphSize.small,
                   *graphv,
                   *THEME_BLACK)
    return pic


def _errors_plt(
        params: Params, title: str, desc: List[str], /,
        xfrom: int = None, xto: int = None, *,
        e_in: list, e_out: list
) -> Tuple[List[str], int]:
    _, max_e_in, _, _ = min_max_last_avg(e_in)
    _, max_e_out, _, _ = min_max_last_avg(e_out)

    cfg = {'colors': [lightgreen, lightblue], 'offset': 2,
           'format': '{:>5.1f} ', 'trim': False,
           'xfrom': xfrom, 'xto': xto}
    riglim = setup_riglim_plt(
        *get_rig_lim_desc(desc),
        0, ceil_scaled(max(max_e_in or 0.9, max_e_out or 0.9)))
    merge(riglim, cfg)
    merge(GraphSize.small_ascii, cfg)
    merge(XAXIS_CFG.get(params.twhen, {}), cfg)
    cfg['xrows'] = 1
    #
    plt = plot([e_in, e_out], cfg)
    plt = lstrip_column(plt).split('\n')
    width = len(plt[-1])
    if title:
        plt.insert(0, title.center(width))
    plt.append(
        f'{lightgreen}Input{reset}'
        + f'{lightblue}Output{reset}'.rjust(width - len('Input') + COLOR_RESET)
    )
    return plt, width
