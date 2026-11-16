"""Birth chart (Jathakam) engine: graha sthiti, lagna, bhava, 16 vargas, birth panchanga."""
import datetime
import swisseph as swe

from .ephemeris import (ZoneInfo, get_ayanamsa, get_sideral_position, get_rise_set, get_elongation,
                        find_elongation_boundary_jd, _get_tithi_name_with_paksha, get_karana_num,
                        decimal_to_dms_string, format_time_local, jd_to_datetime_utc,
                        NAKSHATRA_SPAN, PADA_SPAN, YOGA_SPAN, TITHI_SPAN,
                        PLANET_MAP_SWE, RASHI_NAMES, NAKSHATRA_NAMES, YOGA_NAMES, KARANA_NAMES,
                        VARAM_NAMES, PLANET_NAMES, TELUGU_YEAR_NAMES_EN, TELUGU_YEAR_NAMES_TE,
                        UGADI_ANCHOR_YEAR)
from .jyotish import (PLANETS, SPHUTA_PLANETS, SIGN_LORD, EXALTATION, DEBILITATION, MOOLATRIKONA,
                      OWN_SIGNS, COMBUST_ORB, COMBUST_ORB_RETRO, VARGAS, NAKSHATRA_LORD, natural_relation)


# ---------------------------------------------------------------- time
def local_to_jd_utc(date_str, time_str, iana_tz):
    """'1990-08-15', '14:35' or '14:35:20', 'Asia/Kolkata' -> (jd_ut, aware local datetime)."""
    parts = [int(x) for x in time_str.split(':')] + [0, 0]
    y, m, d = [int(x) for x in date_str.split('-')]
    local = datetime.datetime(y, m, d, parts[0], parts[1], parts[2], tzinfo=ZoneInfo(iana_tz))
    utc = local.astimezone(datetime.timezone.utc)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)
    return jd, local


# ---------------------------------------------------------------- vargas
def varga_sign(lon, n):
    """Sign index (0-11) of a sidereal longitude in divisional chart Dn (Parashara rules)."""
    sign = int(lon // 30) % 12
    deg = lon % 30
    odd = sign % 2 == 0          # Mesha (index 0) is an odd sign
    mod = sign % 3               # 0 movable, 1 fixed, 2 dual
    p = int(deg // (30.0 / n)) if n not in (30,) else None
    if n == 1:
        return sign
    if n == 2:
        return (4 if deg < 15 else 3) if odd else (3 if deg < 15 else 4)
    if n == 3:
        return (sign + 4 * p) % 12
    if n == 4:
        return (sign + 3 * p) % 12
    if n == 7:
        return (sign + p) % 12 if odd else (sign + 6 + p) % 12
    if n == 9:
        return int(lon // (30.0 / 9)) % 12
    if n == 10:
        return (sign + p) % 12 if odd else (sign + 8 + p) % 12
    if n == 12:
        return (sign + p) % 12
    if n == 16:
        return ([0, 4, 8][mod] + p) % 12
    if n == 20:
        return ([0, 8, 4][mod] + p) % 12
    if n == 24:
        return ((4 if odd else 3) + p) % 12
    if n == 27:
        return int(lon // (30.0 / 27)) % 12
    if n == 30:
        if odd:
            bands = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]   # Ma Sa Ju Me Ve
        else:
            bands = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]   # Ve Me Ju Sa Ma
        for upper, s in bands:
            if deg < upper:
                return s
        return bands[-1][1]
    if n == 40:
        return ((0 if odd else 6) + p) % 12
    if n == 45:
        return ([0, 4, 8][mod] + p) % 12
    if n == 60:
        return (sign + p) % 12
    raise ValueError(f'Unsupported varga D{n}')


# ---------------------------------------------------------------- dignity
def dignity(planet, lon):
    if planet not in EXALTATION:
        return None
    sign, deg = int(lon // 30), lon % 30
    if EXALTATION[planet][0] == sign:
        return 'exalted'
    if DEBILITATION[planet][0] == sign:
        return 'debilitated'
    mt = MOOLATRIKONA.get(planet)
    if mt and mt[0] == sign and mt[1] <= deg < mt[2]:
        return 'moolatrikona'
    if sign in OWN_SIGNS.get(planet, []):
        return 'own'
    if planet in ('rahu', 'ketu'):
        return None
    return natural_relation(planet, SIGN_LORD[sign])


def nakshatra_info(lon, lang='english'):
    idx = int(lon // NAKSHATRA_SPAN) % 27
    pada = int((lon % NAKSHATRA_SPAN) // PADA_SPAN) + 1
    return {'index': idx, 'pada': pada, 'lord': NAKSHATRA_LORD[idx],
            'name_english': NAKSHATRA_NAMES['english'][idx], 'name_telugu': NAKSHATRA_NAMES['telugu'][idx]}


def sign_names(idx):
    return {'index': idx, 'name_english': RASHI_NAMES['english'][idx], 'name_telugu': RASHI_NAMES['telugu'][idx]}


# ---------------------------------------------------------------- positions
def planet_longitudes(jd):
    """{planet: (sidereal_lon, tropical_speed)} using the ephemeris_web_02 sphuta rule."""
    out = {}
    for p in PLANETS:
        lon, speed, _, _ = get_sideral_position(jd, PLANET_MAP_SWE[p], is_ketu=(p == 'ketu'),
                                                apply_sphuta=(p in SPHUTA_PLANETS))
        out[p] = (lon, speed)
    return out


def bhava_cusps(jd, lat, lon):
    """Sripati bhava: madhya from Porphyry trisection, sandhi = midpoint. Returns sidereal lists."""
    ayan = get_ayanamsa(jd)
    _, ascmc = swe.houses(jd, lat, lon, b'P')
    asc = (ascmc[0] - ayan) % 360
    mc = (ascmc[1] - ayan) % 360
    ic, dsc = (mc + 180) % 360, (asc + 180) % 360
    quads = [(asc, ic), (ic, dsc), (dsc, mc), (mc, asc)]
    madhya = []
    for a, b in quads:
        span = (b - a) % 360
        madhya += [(a + span * k / 3) % 360 for k in range(3)]
    sandhi = []  # sandhi[i] = start of bhava i
    for i in range(12):
        prev = madhya[i - 1]
        span = (madhya[i] - prev) % 360
        sandhi.append((prev + span / 2) % 360)
    return asc, mc, madhya, sandhi


def bhava_of(lon, sandhi):
    for i in range(12):
        a, b = sandhi[i], sandhi[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 1


# ---------------------------------------------------------------- panchanga at birth
def birth_panchanga(jd, local_dt, lat, lon, iana_tz):
    elong = get_elongation(jd)
    tithi_idx = min(int(elong / TITHI_SPAN) + 1, 30)
    sun_lon = planet_longitudes(jd)['sun'][0]
    moon_lon = planet_longitudes(jd)['moon'][0]
    yoga_idx = min(int(((sun_lon + moon_lon) % 360) / YOGA_SPAN) + 1, 27)
    karana_num = get_karana_num(int(elong / 6.0) + 1)

    # Vedic day runs sunrise to sunrise
    rise, sset = get_rise_set(local_dt.year, local_dt.month, local_dt.day, lat, lon, iana_tz_str=iana_tz)
    vara_date = local_dt.date()
    if rise and jd < rise:
        vara_date -= datetime.timedelta(days=1)
    vara_idx = (vara_date.weekday() + 1) % 7  # VARAM_NAMES starts on Sunday

    # Ishta kaala (ghatis from sunrise)
    ishta = None
    if rise:
        ref_rise = rise if jd >= rise else get_rise_set(vara_date.year, vara_date.month, vara_date.day,
                                                        lat, lon, iana_tz_str=iana_tz)[0]
        if ref_rise:
            g = (jd - ref_rise) * 60.0
            ishta = f"{int(g)} ఘ. {int((g % 1) * 60)} వి." if g >= 0 else None

    tname = _get_tithi_name_with_paksha(tithi_idx)
    nak = nakshatra_info(moon_lon)
    return {
        'tithi': {'index': tithi_idx, **tname},
        'nakshatra': nak,
        'yoga': {'index': yoga_idx, 'name_english': YOGA_NAMES['english'][yoga_idx],
                 'name_telugu': YOGA_NAMES['telugu'][yoga_idx]},
        'karana': {'index': karana_num, 'name_english': KARANA_NAMES['english'][karana_num],
                   'name_telugu': KARANA_NAMES['telugu'][karana_num]},
        'vara': {'index': vara_idx, 'name_english': VARAM_NAMES['english'][vara_idx],
                 'name_telugu': VARAM_NAMES['telugu'][vara_idx]},
        'sunrise': format_time_local(rise, iana_tz, True) if rise else '',
        'sunset': format_time_local(sset, iana_tz, True) if sset else '',
        'ishta_kaala_ghatis': ishta,
        'samvatsara': samvatsara(jd, local_dt.year),
    }


def _sun_sidereal(jd):
    return get_sideral_position(jd, swe.SUN)[0]


def _mesha_sankranti(year):
    lo = swe.julday(year, 3, 25, 0)
    hi = swe.julday(year, 4, 25, 0)
    for _ in range(50):
        mid = (lo + hi) / 2
        s = _sun_sidereal(mid)
        if s > 180:   # still in Meena
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _ugadi_jd(year):
    """Start of Chaitra Shukla Pratipada = the Amavasya end preceding Mesha Sankranti."""
    ms = _mesha_sankranti(year)
    approx = ms - get_elongation(ms) / 12.19
    return find_elongation_boundary_jd(0.0, approx)


def samvatsara(jd, greg_year):
    idx = (greg_year - UGADI_ANCHOR_YEAR) % 60
    if jd < _ugadi_jd(greg_year):
        idx = (idx - 1) % 60
    return {'index': idx, 'name_english': TELUGU_YEAR_NAMES_EN[idx], 'name_telugu': TELUGU_YEAR_NAMES_TE[idx]}


# ---------------------------------------------------------------- main entry
def build_chart(name, date_str, time_str, lat, lon, iana_tz, place=''):
    jd, local_dt = local_to_jd_utc(date_str, time_str, iana_tz)
    positions = planet_longitudes(jd)
    asc, mc, madhya, sandhi = bhava_cusps(jd, lat, lon)
    lagna_sign = int(asc // 30)
    sun_lon = positions['sun'][0]

    grahas = []
    for p in PLANETS:
        plon, speed = positions[p]
        retro = p in ('rahu', 'ketu') or speed < 0
        combust = False
        if p in COMBUST_ORB:
            orb = COMBUST_ORB_RETRO.get(p, COMBUST_ORB[p]) if retro else COMBUST_ORB[p]
            sep = abs((plon - sun_lon + 180) % 360 - 180)
            combust = sep <= orb
        sign = int(plon // 30)
        grahas.append({
            'key': p, 'name_english': PLANET_NAMES[p]['english'], 'name_telugu': PLANET_NAMES[p]['telugu'],
            'longitude': round(plon, 6), 'sign': sign_names(sign), 'degree_in_sign': decimal_to_dms_string(plon),
            'nakshatra': nakshatra_info(plon), 'retrograde': retro, 'combust': combust,
            'dignity': dignity(p, plon), 'house_whole_sign': (sign - lagna_sign) % 12 + 1,
            'bhava': bhava_of(plon, sandhi), 'sign_lord': SIGN_LORD[sign],
            'navamsa_sign': varga_sign(plon, 9),
        })

    lagna = {'key': 'lagna', 'longitude': round(asc, 6), 'sign': sign_names(lagna_sign),
             'degree_in_sign': decimal_to_dms_string(asc), 'nakshatra': nakshatra_info(asc),
             'sign_lord': SIGN_LORD[lagna_sign], 'navamsa_sign': varga_sign(asc, 9)}

    vargas = {}
    for code, n, en, te, use_en, use_te in VARGAS:
        boxes = {i: [] for i in range(12)}
        boxes[varga_sign(asc, n)].append('lagna')
        for g in grahas:
            boxes[varga_sign(g['longitude'], n)].append(g['key'])
        vargas[code] = {'code': code, 'n': n, 'name_english': en, 'name_telugu': te,
                        'purpose_english': use_en, 'purpose_telugu': use_te,
                        'lagna_sign': varga_sign(asc, n), 'boxes': boxes}

    bhavas = []
    for i in range(12):
        bhavas.append({'house': i + 1, 'madhya': round(madhya[i], 4), 'sandhi_start': round(sandhi[i], 4),
                       'madhya_dms': f"{RASHI_NAMES['english'][int(madhya[i] // 30)]} {decimal_to_dms_string(madhya[i])}",
                       'planets': [g['key'] for g in grahas if g['bhava'] == i + 1]})

    return {
        'name': name, 'birth': {'date': date_str, 'time': time_str, 'lat': lat, 'lon': lon,
                                'iana_tz': iana_tz, 'place': place, 'jd_ut': jd,
                                'utc': jd_to_datetime_utc(jd).strftime('%Y-%m-%d %H:%M:%S')},
        'ayanamsa': {'name': 'Lahiri', 'value': round(get_ayanamsa(jd), 6),
                     'dms': _dms_full(get_ayanamsa(jd))},
        'lagna': lagna, 'grahas': grahas, 'vargas': vargas, 'bhavas': bhavas,
        'midheaven': round(mc, 4),
        'panchanga': birth_panchanga(jd, local_dt, lat, lon, iana_tz),
    }


def _dms_full(x):
    d = int(x)
    m = int((x - d) * 60)
    s = int(((x - d) * 60 - m) * 60)
    return f"{d}° {m}' {s}\""
