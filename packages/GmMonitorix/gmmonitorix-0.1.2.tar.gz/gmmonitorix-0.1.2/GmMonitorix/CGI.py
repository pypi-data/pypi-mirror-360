import os
import re
import sys
import urllib.parse
from dataclasses import replace
from datetime import datetime, timedelta
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from typing import Union

from . import (
    ADMINS_FILE, IMG_FORMAT, OUTPUT_DIR, GRAPHS_REFRESH_PERIOD,
    MONITORIX_DB_DIR, MONITORIX_CONF,
    Locker, GraphSize, Params, parse_conf
)

META_20 = '20 text/gemini; charset=utf-8;\r\n'


def response_20(*lines):
    sys.stdout.write(META_20)
    for line in lines:
        print(line)


def cleanup_old_pics(when: datetime, out_dir: Path):
    for f in out_dir.glob(f'*.gmi'):
        if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < when:
            os.remove(f)

    for f in out_dir.glob(f'*.{IMG_FORMAT}'):
        if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < when:
            os.remove(f)


def select_twhen(params: Params):
    return (f'=> ?{replace(params, twhen="hour")} Hour\n'
            f'=> ?{replace(params, twhen="day")} Day\n'
            f'=> ?{replace(params, twhen="week")} Week\n'
            f'=> ?{replace(params, twhen="month")} Month\n'
            f'=> ?{replace(params, twhen="year")} Year\n')


def main(*, admins: Union[Path, str] = ADMINS_FILE,
         out_dir: Union[Path, str] = OUTPUT_DIR,
         db_dir: Union[Path, str] = MONITORIX_DB_DIR,
         cfg: Union[Path, str] = MONITORIX_CONF):
    admins = Path(admins) if isinstance(admins, str) else admins
    out_dir = Path(out_dir) if isinstance(out_dir, str) else out_dir
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
    db_dir = Path(db_dir) if isinstance(db_dir, str) else db_dir
    cfg = Path(cfg) if isinstance(cfg, str) else cfg
    cfg = parse_conf(cfg)
    #
    path = urllib.parse.unquote(os.environ.get("PATH_INFO") or 'cgi')
    query = urllib.parse.unquote(os.environ.get("QUERY_STRING") or '')
    params = Params.from_str(query)
    cert = os.environ.get("TLS_CLIENT_HASH") or ''
    is_admin = (not admins.exists() or (cert and cert in admins.read_text()))
    if not is_admin or re.search(r'[^/a-zA-Z0-9._-]+', path):
        response_20('# Trespassed W')
        exit(0)
    if path.endswith(f'.{IMG_FORMAT}'):
        pic = (out_dir / path).resolve()
        if not str(pic).startswith(str(out_dir.resolve())):
            response_20('# Trespassed W')
        elif pic.is_file():
            sys.stdout.write(f'20 image/{IMG_FORMAT}\r\n')
            sys.stdout.buffer.write(pic.read_bytes())
            sys.stdout.flush()
        else:
            print(f'51 Not Found\r\n')
        exit(0)
    elif path != 'cgi':
        response_20('# Trespassed W')
        exit(0)

    if 'selectTwhen' in query:
        response_20(select_twhen(params))
        exit(0)

    with Locker(out_dir / 'gm-monitorix.lock'):
        now = datetime.now()
        gmi = out_dir / (f'gm-monitorix.{params.when}'
                         f'.{1 if params.picUrls else 0}.gmi')
        modified = datetime.fromtimestamp(gmi.stat().st_mtime) if gmi.exists() \
            else now - GRAPHS_REFRESH_PERIOD
        if modified + GRAPHS_REFRESH_PERIOD <= now:
            cleanup_old_pics(now - timedelta(days=1), out_dir)
            GraphSize.apply(cfg)
            text = f'# {cfg.get("title", "Monitorix")}  ({params.when})\n'
            text += f'=> ?{replace(params, picUrls=not params.picUrls)}' \
                    f" {'☑' if params.picUrls else '☐'} Show image urls\n"
            text += f'=> ?selectTwhen&{params} ⯆ Period: {params.twhen}\n'
            text += '\n'
            for graph, enabled in cfg.get('graph_enable', {}).items():
                if enabled != 'y' or not find_spec(f'.{graph}', 'GmMonitorix'):
                    continue  #
                module = import_module(f'.{graph}', 'GmMonitorix')
                func = getattr(module, f'{graph}_cgi')
                text += func(params, db_dir, out_dir, cfg)
            gmi.write_text(text)
        else:
            text = gmi.read_text()
    response_20(text)
