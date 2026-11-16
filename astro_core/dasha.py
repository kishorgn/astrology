"""Vimshottari dasha: Mahadasha -> Antardasha -> Pratyantardasha."""
import datetime
from .ephemeris import jd_to_datetime_utc, ZoneInfo, NAKSHATRA_SPAN
from .jyotish import DASHA_ORDER, DASHA_YEARS, NAKSHATRA_LORD

YEAR_DAYS = 365.2425  # Gregorian year; most Telugu software uses this or 365.25 — keep configurable


def _seq_from(lord):
    i = DASHA_ORDER.index(lord)
    return DASHA_ORDER[i:] + DASHA_ORDER[:i]


def _fmt(jd, tz):
    return jd_to_datetime_utc(jd).astimezone(ZoneInfo(tz)).strftime('%d-%m-%Y')


def vimshottari(moon_lon, birth_jd, iana_tz, now_jd=None, levels=3):
    nak = int(moon_lon // NAKSHATRA_SPAN) % 27
    lord = NAKSHATRA_LORD[nak]
    elapsed_frac = (moon_lon % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    md_start = birth_jd - elapsed_frac * DASHA_YEARS[lord] * YEAR_DAYS
    balance_years = DASHA_YEARS[lord] * (1 - elapsed_frac)

    def sub(parent_lord, start_jd, parent_years, depth):
        out, t = [], start_jd
        for l in _seq_from(parent_lord):
            yrs = parent_years * DASHA_YEARS[l] / 120.0
            end = t + yrs * YEAR_DAYS
            node = {'lord': l, 'start_jd': t, 'end_jd': end, 'start': _fmt(t, iana_tz), 'end': _fmt(end, iana_tz),
                    'years': round(yrs, 4)}
            if depth > 1:
                node['sub'] = sub(l, t, yrs, depth - 1)
            if now_jd is not None:
                node['current'] = t <= now_jd < end
            out.append(node)
            t = end
        return out

    mahadashas, t = [], md_start
    for _cycle in range(2):  # 240 years covers any life
        for l in _seq_from(lord):
            yrs = DASHA_YEARS[l]
            end = t + yrs * YEAR_DAYS
            node = {'lord': l, 'start_jd': t, 'end_jd': end, 'start': _fmt(t, iana_tz), 'end': _fmt(end, iana_tz),
                    'years': yrs}
            if levels > 1:
                node['sub'] = sub(l, t, yrs, levels - 1)
            if now_jd is not None:
                node['current'] = t <= now_jd < end
            mahadashas.append(node)
            t = end
        if t > birth_jd + 120 * YEAR_DAYS:
            break
    mahadashas = [m for m in mahadashas if m['end_jd'] > birth_jd and m['start_jd'] < birth_jd + 120 * YEAR_DAYS]

    current = None
    if now_jd is not None:
        chain = []
        level = mahadashas
        while level:
            hit = next((x for x in level if x.get('current')), None)
            if not hit:
                break
            chain.append({'lord': hit['lord'], 'start': hit['start'], 'end': hit['end']})
            level = hit.get('sub')
        current = chain
    y = int(balance_years)
    m = int((balance_years - y) * 12)
    d = int(((balance_years - y) * 12 - m) * 30.4375)
    return {'birth_lord': lord, 'balance': {'years': y, 'months': m, 'days': d},
            'mahadashas': mahadashas, 'current': current}
