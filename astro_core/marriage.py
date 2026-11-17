"""Complete marriage matching (వివాహ పొంతన) — South Indian / Telugu checklist.

Order follows the traditional checklist:
  1-10  Dasha poruthams      11 Kuja dosha      12 Nadi dosha      13 Bhakoot dosha
  14    Papasamyam           15 7th house       16 7th lord        17 Navamsa (D9)
  18    Venus & Jupiter      19 Dasha-Bhukti    20 Houses 2/4/8/12 21 Santana
  22    Graha bala (simplified, dignity based — NOT full Shadbala)
Ashtakoota (36 gunas) comes from matching.match() and is reported alongside.

Results are 'good' / 'medium' / 'bad'. Rules vary between regional traditions; every table
below is data, so an astrologer can adjust it without touching logic.
All data returned is language-neutral (keys, indices, numbers); the UI renders Telugu/English.
"""
from .jyotish import (SIGN_LORD, EXALTATION, DEBILITATION, MOOLATRIKONA, OWN_SIGNS, KENDRA, TRIKONA,
                      DUSTHANA, NATURAL_BENEFICS, natural_relation)
from .matching import (match as ashtakoota, YONI_OF_NAK, YONI_TABLE, GANA_OF_NAK, nadi_of, rajju_of,
                       VEDHA_PAIRS)
from .dasha import YEAR_DAYS

MALEFICS = ['sun', 'mars', 'saturn', 'rahu', 'ketu']

# ------------------------------------------------------------------ helpers
def _g(chart):
    return {x['key']: x for x in chart['grahas']}


def _house(from_sign, sign):
    return (sign - from_sign) % 12 + 1


def sign_dignity(planet, sign):
    """Dignity of a planet in a sign (used for D9, where only the sign is known)."""
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return 'exalted'
    if planet in DEBILITATION and DEBILITATION[planet][0] == sign:
        return 'debilitated'
    if sign in OWN_SIGNS.get(planet, []):
        return 'own'
    if planet in ('rahu', 'ketu'):
        return 'neutral'
    return natural_relation(planet, SIGN_LORD[sign])


def aspects_on(target_sign, signs):
    """Planets casting full graha drishti on target_sign (whole-sign, Parashari)."""
    special = {'mars': (4, 8), 'jupiter': (5, 9), 'saturn': (3, 10)}
    out = []
    for p, s in signs.items():
        if p in ('rahu', 'ketu'):
            continue
        h = _house(s, target_sign)
        if h == 7 or h in special.get(p, ()):
            out.append(p)
    return out


def _benefic(p, g):
    if p == 'mercury':   # Mercury is benefic unless with malefics
        return not any(g[m]['sign']['index'] == g['mercury']['sign']['index'] for m in MALEFICS)
    if p == 'moon':      # waxing-ish Moon (60°+ from Sun) treated as benefic
        return abs((g['moon']['longitude'] - g['sun']['longitude'] + 180) % 360 - 180) >= 60
    return p in NATURAL_BENEFICS


def _rate(score, good=1, bad=-2):
    return 'good' if score >= good else ('bad' if score <= bad else 'medium')


# ------------------------------------------------------------------ 1-10 Dasha poruthams
VASYA_SIGNS = {0: [4, 7], 1: [3, 6], 2: [5], 3: [7, 8], 4: [6], 5: [11, 2], 6: [5, 9],
               7: [3], 8: [11], 9: [0, 10], 10: [0], 11: [9]}
MAHENDRA_COUNTS = {4, 7, 10, 13, 16, 19, 22, 25}

PORUTHAM_NAMES = [
    ('dina', 'Dina Porutham', 'దిన పొంతన'), ('gana', 'Gana Porutham', 'గణ పొంతన'),
    ('mahendra', 'Mahendra Porutham', 'మహేంద్ర పొంతన'), ('sthree_deergha', 'Sthree Deergha', 'స్త్రీ దీర్ఘ'),
    ('yoni', 'Yoni Porutham', 'యోని పొంతన'), ('rasi', 'Rasi Porutham', 'రాశి పొంతన'),
    ('rasyadhipathi', 'Rasyadhipathi Porutham', 'రాశ్యాధిపతి పొంతన'), ('vasya', 'Vasya Porutham', 'వశ్య పొంతన'),
    ('rajju', 'Rajju Porutham', 'రజ్జు పొంతన'), ('vedha', 'Vedha Porutham', 'వేధ పొంతన'),
]


def dasha_poruthams(boy, girl):
    bg, gg = _g(boy), _g(girl)
    bn, gn = bg['moon']['nakshatra']['index'], gg['moon']['nakshatra']['index']
    bs, gs = bg['moon']['sign']['index'], gg['moon']['sign']['index']
    count = (bn - gn) % 27 + 1          # girl's star -> boy's star, inclusive
    res = {}

    rem = count % 9
    res['dina'] = {'result': 'medium' if count == 1 else ('good' if rem in (0, 2, 4, 6, 8) else 'bad'),
                   'info': {'count': count}}

    bgana, ggana = GANA_OF_NAK[bn], GANA_OF_NAK[gn]
    if bgana == ggana:
        r = 'good'
    elif {bgana, ggana} == {0, 1}:
        r = 'good' if bgana == 0 else 'medium'
    else:
        r = 'bad'
    res['gana'] = {'result': r, 'info': {'boy': bgana, 'girl': ggana}}

    res['mahendra'] = {'result': 'good' if count in MAHENDRA_COUNTS else 'bad', 'info': {'count': count}}
    res['sthree_deergha'] = {'result': 'good' if count > 13 else ('medium' if count > 7 else 'bad'),
                             'info': {'count': count}}

    ys = YONI_TABLE[YONI_OF_NAK[bn]][YONI_OF_NAK[gn]]
    res['yoni'] = {'result': 'bad' if ys == 0 else ('medium' if ys == 1 else 'good'),
                   'info': {'boy': YONI_OF_NAK[bn], 'girl': YONI_OF_NAK[gn], 'score': ys}}

    n = _house(gs, bs)                  # girl's rasi -> boy's rasi
    if n == 1:
        r = 'good' if bn != gn else 'medium'
    elif n in (2, 12, 6, 8):
        r = 'bad'
    elif n in (5, 9):
        r = 'medium'
    else:
        r = 'good'
    res['rasi'] = {'result': r, 'info': {'count': n}}

    bl, gl = SIGN_LORD[bs], SIGN_LORD[gs]
    rels = {natural_relation(bl, gl), natural_relation(gl, bl)}
    r = 'good' if bl == gl or rels == {'friend'} else ('bad' if 'enemy' in rels else 'medium')
    res['rasyadhipathi'] = {'result': r, 'info': {'boy': bl, 'girl': gl}}

    res['vasya'] = {'result': 'good' if (bs in VASYA_SIGNS[gs] or gs in VASYA_SIGNS[bs]) else 'bad',
                    'info': {'boy': bs, 'girl': gs}}

    br, gr = rajju_of(bn), rajju_of(gn)
    res['rajju'] = {'result': 'bad' if br == gr else 'good', 'info': {'boy': br, 'girl': gr}}

    vedha = frozenset((bn, gn)) in VEDHA_PAIRS
    res['vedha'] = {'result': 'bad' if vedha else 'good', 'info': {'boy': bn, 'girl': gn}}

    rows = []
    for i, (k, en, te) in enumerate(PORUTHAM_NAMES, 1):
        rows.append({'no': i, 'key': k, 'name_english': en, 'name_telugu': te, **res[k]})
    pts = sum({'good': 1, 'medium': 0.5, 'bad': 0}[r['result']] for r in rows)
    return {'rows': rows, 'score': pts, 'max': 10,
            'mandatory_ok': res['rajju']['result'] == 'good' and res['vedha']['result'] == 'good'}


# ------------------------------------------------------------------ 11 Kuja dosha
KUJA_HOUSES = (1, 2, 4, 7, 8, 12)
# Classical sign exceptions: Mars in house H in these signs does not cause dosha
KUJA_SIGN_EXCEPTIONS = {2: (2, 5), 4: (0, 7), 7: (3, 9), 8: (8, 11), 12: (1, 6)}


def kuja_dosha_full(chart):
    g = _g(chart)
    signs = {k: v['sign']['index'] for k, v in g.items()}
    mars = signs['mars']
    refs = {'lagna': chart['lagna']['sign']['index'], 'moon': signs['moon'], 'venus': signs['venus']}
    frm = {k: {'house': _house(s, mars), 'dosha': _house(s, mars) in KUJA_HOUSES} for k, s in refs.items()}
    raw = frm['lagna']['dosha'] or frm['moon']['dosha']
    exc = []
    if g['mars']['dignity'] in ('own', 'exalted', 'moolatrikona'):
        exc.append('own_exalted')
    for k in ('lagna', 'moon'):
        h = frm[k]['house']
        if frm[k]['dosha'] and mars in KUJA_SIGN_EXCEPTIONS.get(h, ()):
            exc.append(f'sign_exception_{k}')
    if 'jupiter' in aspects_on(mars, signs) or signs['jupiter'] == mars:
        exc.append('jupiter')
    if signs['moon'] == mars:
        exc.append('moon_conjunct')
    status = 'none' if not raw else ('cancelled' if exc else 'present')
    return {'status': status, 'from': frm, 'exceptions': exc}


# ------------------------------------------------------------------ 12, 13 Nadi / Bhakoot
def nadi_bhakoot(boy, girl):
    bg, gg = _g(boy), _g(girl)
    bm, gm = bg['moon'], gg['moon']
    bn, gn = bm['nakshatra']['index'], gm['nakshatra']['index']
    bs, gs = bm['sign']['index'], gm['sign']['index']
    nadi = {'boy': nadi_of(bn), 'girl': nadi_of(gn), 'dosha': nadi_of(bn) == nadi_of(gn), 'cancel': None}
    if nadi['dosha']:
        if bs == gs and bn != gn:
            nadi['cancel'] = 'same_rasi_diff_star'
        elif bn == gn and bs != gs:
            nadi['cancel'] = 'same_star_diff_rasi'
        elif bn == gn and bm['nakshatra']['pada'] != gm['nakshatra']['pada']:
            nadi['cancel'] = 'same_star_diff_pada'
    n = _house(gs, bs)
    bl, gl = SIGN_LORD[bs], SIGN_LORD[gs]
    bhakoot = {'count': n, 'dosha': n in (2, 12, 5, 9, 6, 8), 'cancel': None}
    if bhakoot['dosha']:
        if bl == gl:
            bhakoot['cancel'] = 'same_lord'
        elif natural_relation(bl, gl) == 'friend' and natural_relation(gl, bl) == 'friend':
            bhakoot['cancel'] = 'lords_friends'
    for d in (nadi, bhakoot):
        d['result'] = 'good' if not d['dosha'] else ('medium' if d['cancel'] else 'bad')
    return nadi, bhakoot


# ------------------------------------------------------------------ 14 Papasamyam
PAPA_WEIGHT = {'mars': 1, 'saturn': 1, 'rahu': 1, 'ketu': 1, 'sun': 0.5}
PAPA_FROM = {'lagna': 1, 'moon': 0.5, 'venus': 0.25}


def papa_points(chart):
    g = _g(chart)
    refs = {'lagna': chart['lagna']['sign']['index'], 'moon': g['moon']['sign']['index'],
            'venus': g['venus']['sign']['index']}
    total, items = 0.0, []
    for p, w in PAPA_WEIGHT.items():
        for ref, rw in PAPA_FROM.items():
            h = _house(refs[ref], g[p]['sign']['index'])
            if h in KUJA_HOUSES:
                total += w * rw
                items.append({'planet': p, 'from': ref, 'house': h, 'points': w * rw})
    return {'total': round(total, 2), 'items': items}


def papasamyam(boy, girl):
    b, gl = papa_points(boy), papa_points(girl)
    diff = gl['total'] - b['total']
    r = 'good' if diff <= 0 else ('medium' if diff <= 1 else 'bad')
    return {'boy': b, 'girl': gl, 'result': r}


# ------------------------------------------------------------------ 15-22 individual chart analysis
def house_info(chart, h):
    g = _g(chart)
    signs = {k: v['sign']['index'] for k, v in g.items()}
    lag = chart['lagna']['sign']['index']
    s = (lag + h - 1) % 12
    lord = SIGN_LORD[s]
    L = g[lord]
    return {'house': h, 'sign': s, 'lord': lord, 'lord_house': _house(lag, L['sign']['index']),
            'lord_sign': L['sign']['index'], 'lord_dignity': L['dignity'], 'lord_combust': L['combust'],
            'lord_retro': L['retrograde'] and lord not in ('rahu', 'ketu'),
            'occupants': [p for p, ps in signs.items() if ps == s],
            'aspects': aspects_on(s, signs)}


def _house_score(info, g):
    sc = 0
    for p in info['occupants']:
        sc += 1 if _benefic(p, g) else -1
    for p in info['aspects']:
        sc += 0.5 if _benefic(p, g) else -0.5
    lh = info['lord_house']
    sc += 1 if lh in KENDRA | TRIKONA else (-1 if lh in DUSTHANA else 0)
    sc += {'exalted': 1, 'moolatrikona': 1, 'own': 1, 'debilitated': -1, 'enemy': -0.5}.get(info['lord_dignity'], 0)
    sc -= 1 if info['lord_combust'] else 0
    return sc


def navamsa_analysis(chart):
    g = _g(chart)
    d9 = {k: v['navamsa_sign'] for k, v in g.items()}
    lag9 = chart['lagna']['navamsa_sign']
    s7 = (lag9 + 6) % 12
    lord9, lord7 = SIGN_LORD[lag9], SIGN_LORD[s7]
    return {
        'lagna_sign': lag9, 'lagna_lord': lord9, 'lagna_lord_house': _house(lag9, d9[lord9]),
        'lagna_lord_dignity': sign_dignity(lord9, d9[lord9]),
        'seventh_sign': s7, 'seventh_lord': lord7, 'seventh_lord_house': _house(lag9, d9[lord7]),
        'seventh_lord_dignity': sign_dignity(lord7, d9[lord7]),
        'seventh_occupants': [p for p, s in d9.items() if s == s7],
        'venus': {'sign': d9['venus'], 'house': _house(lag9, d9['venus']), 'dignity': sign_dignity('venus', d9['venus'])},
        'jupiter': {'sign': d9['jupiter'], 'house': _house(lag9, d9['jupiter']),
                    'dignity': sign_dignity('jupiter', d9['jupiter'])},
        'vargottama': [p for p, v in g.items() if v['sign']['index'] == v['navamsa_sign']]
                      + (['lagna'] if chart['lagna']['sign']['index'] == lag9 else []),
    }


DIG_PTS = {'exalted': 5, 'moolatrikona': 4.5, 'own': 4, 'friend': 3, 'neutral': 2, 'enemy': 1, 'debilitated': 0}


def graha_bala(chart):
    """Simplified dignity/placement strength 0-10. Not Shadbala (no kala/dig/ayana/drik components)."""
    g = _g(chart)
    lag = chart['lagna']['sign']['index']
    out = {}
    for p in ('sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn'):
        x = g[p]
        sc = DIG_PTS.get(x['dignity'], 2)
        sc += DIG_PTS.get(sign_dignity(p, x['navamsa_sign']), 2) * 0.5
        h = _house(lag, x['sign']['index'])
        sc += 1 if h in KENDRA | TRIKONA else (-1 if h in DUSTHANA else 0)
        sc -= 1.5 if x['combust'] else 0
        sc += 0.5 if x['retrograde'] and p not in ('sun', 'moon') else 0
        sc = max(0, min(10, round(sc, 1)))
        out[p] = {'score': sc, 'level': 'good' if sc >= 6 else ('medium' if sc >= 3.5 else 'bad')}
    return out


def marriage_dasha(chart, gender, dasha, now_jd, years=7):
    g = _g(chart)
    h7 = house_info(chart, 7)
    nav = navamsa_analysis(chart)
    karaka = 'venus' if gender == 'boy' else 'jupiter'
    supportive = {h7['lord'], karaka, 'venus', nav['seventh_lord']} | set(h7['occupants'])
    end = now_jd + years * YEAR_DAYS
    periods = []
    for md in dasha['mahadashas']:
        if md['end_jd'] < now_jd or md['start_jd'] > end:
            continue
        for ad in md['sub']:
            if ad['end_jd'] < now_jd or ad['start_jd'] > end:
                continue
            periods.append({'md': md['lord'], 'ad': ad['lord'], 'start': ad['start'], 'end': ad['end'],
                            'current': ad['start_jd'] <= now_jd < ad['end_jd'],
                            'supportive': md['lord'] in supportive or ad['lord'] in supportive,
                            'strong': md['lord'] in supportive and ad['lord'] in supportive})
    return {'current': dasha.get('current'), 'karaka': karaka, 'supportive_lords': sorted(supportive),
            'periods': periods}


def individual(chart, gender, dasha, now_jd):
    g = _g(chart)
    h7 = house_info(chart, 7)
    santana = house_info(chart, 5)
    j = g['jupiter']
    s_score = _house_score(santana, g) + DIG_PTS.get(j['dignity'], 2) / 2 - 1 - (1 if j['combust'] else 0)
    karakas = {}
    for p in ('venus', 'jupiter'):
        x = g[p]
        karakas[p] = {'sign': x['sign']['index'], 'house': x['house_whole_sign'], 'dignity': x['dignity'],
                      'combust': x['combust'], 'retro': x['retrograde'],
                      'd9_sign': x['navamsa_sign'], 'd9_dignity': sign_dignity(p, x['navamsa_sign'])}
    return {
        'gender': gender,
        'kuja': kuja_dosha_full(chart),
        'papa': papa_points(chart),
        'seventh': {**h7, 'result': _rate(_house_score(h7, g))},
        'navamsa': navamsa_analysis(chart),
        'karakas': karakas, 'primary_karaka': 'venus' if gender == 'boy' else 'jupiter',
        'dasha': marriage_dasha(chart, gender, dasha, now_jd),
        'houses': {h: {**house_info(chart, h), 'result': _rate(_house_score(house_info(chart, h), g))}
                   for h in (2, 4, 8, 12)},
        'santana': {**santana, 'jupiter_dignity': j['dignity'], 'jupiter_house': j['house_whole_sign'],
                    'result': _rate(s_score)},
        'graha_bala': graha_bala(chart),
    }


# ------------------------------------------------------------------ orchestrator
def full_match(boy, girl, boy_dasha, girl_dasha, now_jd):
    por = dasha_poruthams(boy, girl)
    ak = ashtakoota(boy, girl)
    nadi, bhakoot = nadi_bhakoot(boy, girl)
    papa = papasamyam(boy, girl)
    bi, gi = individual(boy, 'boy', boy_dasha, now_jd), individual(girl, 'girl', girl_dasha, now_jd)

    kb, kg = bi['kuja']['status'], gi['kuja']['status']
    kuja = {'boy': kb, 'girl': kg,
            'result': 'good' if (kb == 'present') == (kg == 'present') else 'bad',
            'samyam': kb == 'present' and kg == 'present'}

    flags = []
    if not por['mandatory_ok']:
        flags.append('rajju' if por['rows'][8]['result'] == 'bad' else 'vedha')
    if kuja['result'] == 'bad':
        flags.append('kuja_one_sided')
    if nadi['result'] == 'bad':
        flags.append('nadi')
    if bhakoot['result'] == 'bad':
        flags.append('bhakoot')
    if papa['result'] == 'bad':
        flags.append('papa')

    if not por['mandatory_ok']:
        verdict = 'not_recommended'
    elif por['score'] >= 6 and ak['total'] >= 18 and not flags:
        verdict = 'good'
    elif por['score'] >= 5 and ak['total'] >= 18 and len(flags) <= 1:
        verdict = 'average'
    else:
        verdict = 'weak'

    return {
        'summary': {'verdict': verdict, 'porutham_score': por['score'], 'ashtakoota': ak['total'], 'flags': flags},
        'poruthams': por, 'ashtakoota': ak,
        'doshas': {'kuja': kuja, 'nadi': nadi, 'bhakoot': bhakoot},
        'papasamyam': papa,
        'individual': {'boy': bi, 'girl': gi},
    }
