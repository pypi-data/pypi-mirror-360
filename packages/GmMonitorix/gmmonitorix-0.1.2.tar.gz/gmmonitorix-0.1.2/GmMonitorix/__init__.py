import fcntl
import math
import re
import urllib.parse
from dataclasses import dataclass
from datetime import timedelta, datetime
from pathlib import Path
from typing import Union, List, Optional

__version__ = '0.1.2'

OUTPUT_DIR = Path('.tmp')
ADMINS_FILE = Path('.admins')
MONITORIX_CONF = Path('/etc/monitorix/monitorix.conf')
MONITORIX_DB_DIR = Path('/var/lib/monitorix')
GRAPHS_REFRESH_PERIOD = timedelta(seconds=15)
IMG_FORMAT = 'png'
THEME_BLACK = [
    '--slope-mode',
    '--font=LEGEND:7:',
    '--font=TITLE:9:',
    '--font=UNIT:8:',
    '--font=DEFAULT:0:Mono',
    '--color=CANVAS#000000',
    '--color=BACK#101010',
    '--color=FONT#C0C0C0',
    '--color=MGRID#80C080',
    '--color=GRID#808020',
    '--color=FRAME#808080',
    '--color=ARROW#FFFFFF',
    '--color=SHADEA#404040',
    '--color=SHADEB#404040',
    '--color=AXIS#101010',
]


@dataclass(frozen=True)
class Params:
    picUrls: bool = False
    nwhen: str = '1'
    twhen: str = 'day'

    @property
    def when(self):
        return f'{self.nwhen}{self.twhen}'

    @staticmethod
    def from_str(query) -> 'Params':
        params = urllib.parse.parse_qs(query)

        pic_urls = params.get('urls', '0')
        pic_urls = (pic_urls[0] == '1' if isinstance(pic_urls, list)
                    else pic_urls == '1')

        when = params.get('when', '1day')
        when = when[0] if isinstance(when, list) else when
        nwhen = (re.search(r'^\d+', when) or [1])[0]
        twhen = (re.search(r'hour|day|week|month|year', when) or ['day'])[0]

        return Params(picUrls=pic_urls, nwhen=nwhen, twhen=twhen)

    def __str__(self):
        return f'when={self.when}&urls={"1" if self.picUrls else "0"}'


class GraphSize:
    # @formatter:off
    large         = ['--width=750', '--height=180']  # noqa
    large_ascii   = {'width': 75,   'height': 12  }  # noqa
    main          = ['--width=450', '--height=150']  # noqa
    main_ascii    = {'width': 45,   'height': 11  }  # noqa
    medium        = ['--width=325', '--height=150']  # noqa
    medium_ascii  = {'width': 33,   'height': 11  }  # noqa
    medium2       = ['--width=325', '--height=70' ]  # noqa
    medium2_ascii = {'width': 32,   'height': 4   }  # noqa
    small         = ['--width=200', '--height=66' ]  # noqa
    small_ascii   = {'width': 20,   'height': 4   }  # noqa
    mini          = ['--width=183', '--height=66' ]  # noqa
    mini_ascii    = {'width': 18,   'height': 4   }  # noqa
    tiny          = ['--width=110', '--height=40' ]  # noqa
    tiny_ascii    = {'width': 11,   'height': 2   }  # noqa
    zoom          = ['--width=800', '--height=300']  # noqa
    zoom_ascii    = {'width': 80,   'height': 20  }  # noqa
    remote        = ['--width=300', '--height=100']  # noqa
    remote_ascii  = {'width': 30,   'height': 6   }  # noqa
    # @formatter:on

    @staticmethod
    def apply(cfg: dict):
        sizes = cfg.get('graph_size', {})
        for name, size in sizes.items():  # type: str, str
            wh = size.split('x')
            setattr(GraphSize, name,
                    [f'--width={wh[0]}', f'--height={wh[1]}'])
            # setattr(GraphSize, f'{name}_ascii',
            #         {'width': int(wh[0]) // 10, 'height': int(wh[1]) // 15})


class Locker:
    filename: Path

    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.fp = open(self.filename, mode='w')
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, _type, value, tb):
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        self.fp.close()
        return False


UNITS = [' bytes', 'KiB', 'MiB', 'GiB']


def human_size(size, units=None):
    if units is None:
        units = UNITS
    return f'{size:.01f} {units[0]}' if size < 1024 \
        else human_size(size / 1024, units[1:])


def pic_url(pic: Path, title: str) -> str:
    return (f'=> {pic.name} {title}'
            f' ({pic.suffix[1:]}, {human_size(pic.stat().st_size)})\n')


LBL_UNITS = ['b', 'k', 'M', 'G']


def lbl_size(size, units=None):
    if units is None:
        units = LBL_UNITS
    return '0  ' if math.ceil(size) == 0 \
        else f'{math.ceil(size):.0f} {units[0]}' if size < 1024 \
        else lbl_size(size / 1024, units[1:])


def min_max_last_avg(ser: list):
    if values := list(filter(lambda x: x is not None, ser)):
        return min(values), max(values), values[-1], sum(values) / len(values)
    return None, None, None, None


def lstrip_column(text):
    spaces = re.findall(r'^\s*', text, re.MULTILINE)
    min_spaces = min(map(len, spaces))
    if not min_spaces:
        return text  # nothing to strip
    return ''.join(map(lambda line: line[min_spaces:],
                       text.splitlines(keepends=True)))


def ceil_scaled(value: Union[int, float]) -> float:
    """
    Round a number up to its first significant digit.

    >>> print(ceil_scaled(123))
    200
    >>> print(ceil_scaled(23))
    30
    >>> print(ceil_scaled(10))
    20
    >>> print(ceil_scaled(4))
    5
    >>> print(ceil_scaled(3.21))
    4
    >>> print(ceil_scaled(0.075))
    0.08
    """
    n = 0
    if value > 1:
        while value >= 10:
            value = value // 10
            n += 1
        return math.floor(value + 1) * (10 ** n)
    elif value > 0:
        while value < 1:
            value = value * 10
            n += 1
        return math.floor(value + 1) / (10 ** n)
    return value


def floor_scaled(value: Union[int, float, str]) -> float:
    """
    Round a number down to its first significant digit.

    >>> print(floor_scaled(123))
    100
    >>> print(floor_scaled(23))
    20
    >>> print(floor_scaled(4))
    3
    >>> print(floor_scaled(3.21))
    3
    >>> print(floor_scaled(0.075))
    0.07
    """
    if isinstance(value, str):
        value = float(value)
    n = 0
    if value > 1:
        while value > 10:
            value = value // 10
            n += 1
        if n == 0 and math.floor(value) == value:
            return value - 1
        return math.floor(value) * (10 ** n)
    elif value > 0:
        while value < 1:
            value = value * 10
            n += 1
        return math.ceil(value - 1) / (10 ** n)
    return value


# region x-axis funcs
def xround_func_hour(v):
    dt = datetime.fromtimestamp(v)
    minutes = dt.minute % 10
    dt = dt.replace(minute=(dt.minute // 10) * 10)
    if minutes >= 5:
        dt = dt + timedelta(minutes=10)

    return dt.timestamp()


def xround_func_day(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_hour = dt.replace(minute=0, second=0, microsecond=0)
    dt_half_hour = dt.replace(minute=30, second=0, microsecond=0)

    if dt > dt_half_hour:
        dt = dt_start_of_hour + timedelta(hours=1)
    else:
        dt = dt_start_of_hour

    return dt.timestamp()


def xround_func_week(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_mid_day = dt.replace(hour=12, minute=0, second=0, microsecond=0)

    if dt > dt_mid_day:
        dt = dt_start_of_day + timedelta(days=1)
    else:
        dt = dt_start_of_day

    return dt.timestamp()


def xround_func_month(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_week = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_start_of_week = dt_start_of_week - timedelta(days=dt.weekday())
    dt_half_week = dt.replace(hour=12, minute=0, second=0, microsecond=0)
    dt_half_week = dt_half_week - timedelta(days=dt.weekday())
    dt_half_week += timedelta(days=3)

    if dt > dt_half_week:
        dt = dt_start_of_week + timedelta(weeks=1)
    else:
        dt = dt_start_of_week

    return dt.timestamp()


def xformat_func_month(v: float):
    val = datetime.fromtimestamp(v)
    return val.strftime('Week %V')


def xround_func_year(v):
    dt = datetime.fromtimestamp(v)
    dt_start_of_month = dt.replace(day=1,
                                   hour=0, minute=0, second=0, microsecond=0)
    dt_half_month = dt.replace(day=16,
                               hour=0, minute=0, second=0, microsecond=0)

    if dt > dt_half_month:
        dt = (dt_start_of_month + timedelta(days=32)).replace(day=1)
    else:
        dt = dt_start_of_month

    return dt.timestamp()


XAXIS_CFG = {
    'hour': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%H:%M'),
        'xround_func': xround_func_hour
    },
    'day': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%H:%M'),
        'xround_func': xround_func_day
    },
    'week': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%d %b'),
        'xround_func': xround_func_week
    },
    'month': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('Week %V'),
        'xround_func': xround_func_month
    },
    'year': {
        'xrows': 2, 'xformat': '{}',
        'xformat_func': lambda x: datetime.fromtimestamp(x).strftime('%b %Y'),
        'xround_func': xround_func_year
    },
}
# endregion x-axis funcs

# brasciichart color symbols width, 5 '\033[XXm' + 4 '\033[0m'
COLOR_RESET = 9


def total_mem_kbytes():
    meminfo = dict((i.split()[0].rstrip(':'), int(i.split()[1]))
                   for i in open('/proc/meminfo').readlines())
    # TODO: Support FreeBSD, OpenBSD, NetBSD total memory bytes
    total_mem = meminfo['MemTotal']  # in KB
    return int(total_mem)


def zip_plots(left: List[str], lwidth: int, right: List[str]) -> List[str]:
    if len(left) < len(right):
        left += ([' ' * lwidth] * (len(right) - len(left)))
    elif len(left) > len(right):
        right += [''] * (len(left) - len(right))

    return list(map(lambda t: f'{t[0]}   {t[1]}',
                    zip(left, right)))


def merge(src: dict, dst: dict):
    """
    Deep merge two dictionaries

    >>> a = {'first': {'rows': {'pass': 'dog', 'num': '1'}}}
    >>> b = {'first': {'rows': {'fail': 'cat', 'num': '5'}}}
    >>> merge(b, a) == {'first': {'rows': {'pass': 'dog', 'fail': 'cat', 'num': '5'}}}
    True
    """
    for key, value in src.items():
        if isinstance(value, dict):
            node = dst.setdefault(key, {})
            merge(value, node)
        else:
            dst[key] = value
    return dst


def parse_conf(conf: Path) -> dict:
    cfg = {}
    stack = []
    element = cfg
    with open(conf) as f:
        for line in f:
            line = line.strip()
            if re.match(r'^#', line):
                continue  # skip comment
            if tag := re.search(r'^<\w*>', line):
                name = tag[0].strip('<>')
                new_element = {}
                element[name] = new_element
                stack.append(element)
                element = new_element
            elif re.search(r'^</\w*>', line):
                element = stack.pop()
            elif re.search(r'^[-:/.\w\s]+=[-/.\w\s]*', line):
                param = line.split('=', 2)
                element[param[0].strip()] = (param[1] or '').strip()

    if inc := cfg.get('include_dir', ''):
        inc = Path(conf.parent, inc)
        if inc.is_file():
            inc_cfg = parse_conf(inc)
            cfg = merge(cfg, inc_cfg)
        elif inc.is_dir():
            for f in inc.rglob('*.conf'):
                inc_cfg = parse_conf(f)
                cfg = merge(inc_cfg, cfg)

    return cfg


def get_rig_lim_desc(desc: List[str]) -> tuple[int, Optional[float], Optional[float]]:
    if not desc or len(desc) < 2:
        return 0, None, None  #
    rigid = desc[-2] if len(desc) > 2 else None
    limit = desc[-1] if len(desc) > 1 else None
    limit = (limit or '0:0').strip().split(':')
    #
    upper = limit[0].strip() if len(limit) > 0 else None
    lower = limit[1].strip() if len(limit) > 1 else None
    #
    return (int(rigid or '0'),
            float(lower) if lower else None,
            float(upper) if upper else None)


def get_rig_lim(cfg: dict, num) -> tuple[int, Optional[float], Optional[float]]:
    if not cfg:
        return 0, None, None  #
    rigids = cfg.get('rigid', '').split(',')
    limits = cfg.get('limit', '').split(',')
    #
    rigid = rigids[num].strip() if len(rigids) > num else None
    limit = limits[num].strip() if len(limits) > num else None
    limit = (limit or '0:0').strip().split(':')
    #
    upper = limit[0].strip() if len(limit) > 0 else None
    lower = limit[1].strip() if len(limit) > 1 else None
    #
    return (int(rigid or '0'),
            float(lower) if lower else None,
            float(upper) if upper else None)


def setup_riglim_pic(rigid, lower, upper) -> List[str]:
    # https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html
    # Limits
    # [-u|--upper-limit value]
    # [-l|--lower-limit value]
    # [-r|--rigid]
    # [--allow-shrink]
    #
    # By default the graph will be autoscaling so that it will adjust
    # the y-axis to the range of the data. You can change this behavior
    # by explicitly setting the limits. The displayed y-axis will then
    # range at least from lower-limit to upper-limit. Autoscaling will
    # still permit those boundaries to be stretched unless the rigid
    # option is set.
    riglim = []
    if rigid == 0:
        if lower:
            riglim.append(f'--lower-limit={lower}')
    else:
        riglim += (f'--lower-limit={lower or "0"}',
                   f'--upper-limit={upper or "0"}')
        if rigid == 2:
            riglim.append('--rigid')
    return riglim


def setup_riglim_plt(rigid, lower, upper, min_, max_) -> dict:
    # https://www.monitorix.org/manpage.html
    # rigid
    #  This value defines how the graph must be scaled. Its possible values are:
    #
    # 0 No rigid, the graph will be scaled automatically.
    #   Only the lower-limit value will be used if it’s defined.
    # 1 The graph will be scaled by default according the values in limit
    #   but without rigidness.
    # 2 The graph will be forced to scale using the contents of limit
    #   as its upper-limit and lower-limit values.
    if rigid == 0:
        if lower is not None:
            min_ = min(lower, min_)
    else:
        if rigid == 2:
            # --rigid and Strict limits for brasciichart
            min_, max_ = lower or 0, upper
        else:
            min_, max_ = min(lower or 0, min_), max(upper, max_)
    cfg = {}
    if min_ is not None:
        cfg['min'] = min_
    if max_ is not None:
        cfg['max'] = max_
    return cfg
