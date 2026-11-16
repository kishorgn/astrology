"""Gocharam (transits) relative to the natal Moon sign, incl. Sade Sati / Ashtama Shani."""
import datetime
import swisseph as swe
from .chart import planet_longitudes, sign_names, nakshatra_info
from .ephemeris import PLANET_NAMES, decimal_to_dms_string

# Classical favourable houses from Janma Rasi (Phaladeepika)
GOOD_FROM_MOON = {'sun': {3, 6, 10, 11}, 'moon': {1, 3, 6, 7, 10, 11}, 'mars': {3, 6, 11},
                  'mercury': {2, 4, 6, 8, 10, 11}, 'jupiter': {2, 5, 7, 9, 11}, 'venus': {1, 2, 3, 4, 5, 8, 9, 11, 12},
                  'saturn': {3, 6, 11}, 'rahu': {3, 6, 11}, 'ketu': {3, 6, 11}}


def now_jd():
    t = datetime.datetime.now(datetime.timezone.utc)
    return swe.julday(t.year, t.month, t.day, t.hour + t.minute / 60 + t.second / 3600)


def gochara(chart, jd=None):
    jd = jd or now_jd()
    moon_sign = next(x for x in chart['grahas'] if x['key'] == 'moon')['sign']['index']
    lagna_sign = chart['lagna']['sign']['index']
    pos = planet_longitudes(jd)
    rows = []
    for p, (lon, speed) in pos.items():
        s = int(lon // 30)
        h = (s - moon_sign) % 12 + 1
        rows.append({'key': p, 'name_english': PLANET_NAMES[p]['english'], 'name_telugu': PLANET_NAMES[p]['telugu'],
                     'sign': sign_names(s), 'degree_in_sign': decimal_to_dms_string(lon),
                     'nakshatra': nakshatra_info(lon), 'retrograde': p in ('rahu', 'ketu') or speed < 0,
                     'house_from_moon': h, 'house_from_lagna': (s - lagna_sign) % 12 + 1,
                     'favourable': h in GOOD_FROM_MOON[p]})
    sat_h = next(r for r in rows if r['key'] == 'saturn')['house_from_moon']
    shani = None
    if sat_h in (12, 1, 2):
        phase = {12: 'first (rising)', 1: 'second (peak)', 2: 'third (setting)'}[sat_h]
        shani = {'type': 'sade_sati', 'name_english': f'Sade Sati — {phase} phase',
                 'name_telugu': 'ఏలినాటి శని', 'house': sat_h}
    elif sat_h == 8:
        shani = {'type': 'ashtama', 'name_english': 'Ashtama Shani', 'name_telugu': 'అష్టమ శని', 'house': 8}
    elif sat_h == 4:
        shani = {'type': 'ardhashtama', 'name_english': 'Ardhashtama Shani', 'name_telugu': 'అర్ధాష్టమ శని', 'house': 4}
    return {'jd': jd, 'rows': rows, 'shani': shani}
