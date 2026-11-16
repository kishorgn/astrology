"""astro_core — Jathakam calculation engine.

Pure Python, no Flask dependency, so the same engine can serve the web app and a
mobile app (via the JSON API in app.py).
"""
from .chart import build_chart, varga_sign  # noqa
from .dasha import vimshottari  # noqa
from .ashtakavarga import ashtakavarga  # noqa
from .matching import match, kuja_dosha  # noqa
from .yogas import detect_yogas  # noqa
from .gochara import gochara, now_jd  # noqa
from .predictions import predictions  # noqa


def full_horoscope(name, date, time, lat, lon, iana_tz, place='', lang='english'):
    chart = build_chart(name, date, time, lat, lon, iana_tz, place)
    moon_lon = next(g['longitude'] for g in chart['grahas'] if g['key'] == 'moon')
    nj = now_jd()
    dasha = vimshottari(moon_lon, chart['birth']['jd_ut'], iana_tz, now_jd=nj)
    yogas = detect_yogas(chart)
    return {
        'chart': chart,
        'dasha': dasha,
        'ashtakavarga': ashtakavarga(chart),
        'yogas': yogas,
        'kuja_dosha': kuja_dosha(chart),
        'gochara': gochara(chart, nj),
        'predictions': predictions(chart, dasha, yogas, lang),
    }
