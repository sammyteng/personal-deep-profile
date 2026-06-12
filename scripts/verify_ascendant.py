#!/usr/bin/env python3
"""上升点/天顶独立核算脚本（不依赖任何星历库，纯天文公式）。

用途：与排盘 App 或 pyswisseph 的结果交叉验证。
2026-06-12 实测：1997-04-03 07:30 +08:00 安吉(120°06'E 30°52'N)
→ Asc 金牛 16°51'，与测测App 完全一致（角分级）。

用法：
    python3 verify_ascendant.py "1997-04-03 07:30" 8 120.1 30.867
    # 参数：本地时间 / 时区(小时) / 东经(度) / 北纬(度)
"""
import math
import sys
from datetime import datetime, timedelta

SIGNS = ['白羊', '金牛', '双子', '巨蟹', '狮子', '处女',
         '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼']


def julian_day(dt_utc: datetime) -> float:
    y, m = dt_utc.year, dt_utc.month
    d = dt_utc.day + (dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600) / 24
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def asc_mc(local_str: str, tz_hours: float, lon_deg: float, lat_deg: float):
    dt_local = datetime.strptime(local_str, '%Y-%m-%d %H:%M')
    dt_utc = dt_local - timedelta(hours=tz_hours)
    jd = julian_day(dt_utc)
    t = (jd - 2451545.0) / 36525

    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * t ** 2 - t ** 3 / 38710000) % 360
    lst = (gmst + lon_deg) % 360  # RAMC

    eps = math.radians(23.4392911 - 0.0130042 * t)
    ramc = math.radians(lst)
    phi = math.radians(lat_deg)

    asc = math.degrees(math.atan2(
        math.cos(ramc),
        -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)))) % 360

    mc = math.degrees(math.atan2(math.tan(ramc), math.cos(eps))) % 360
    if abs(mc - lst) > 90:
        mc = (mc + 180) % 360
    return asc, mc


def fmt(deg: float) -> str:
    sign = SIGNS[int(deg // 30)]
    within = deg % 30
    return f"{sign} {int(within)}°{round((within % 1) * 60):02d}'"


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)
    asc, mc = asc_mc(sys.argv[1], float(sys.argv[2]),
                     float(sys.argv[3]), float(sys.argv[4]))
    print(f"Asc = {fmt(asc)}  ({asc:.2f}°)")
    print(f"MC  = {fmt(mc)}  ({mc:.2f}°)")
