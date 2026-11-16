"""Marriage matching: Ashtakoota (36 Guna) + Kuja dosha + Rajju/Vedha (South Indian checks).

Score tables vary slightly between traditions; the ones here follow the most widely used
North/Telugu software convention. An astrologer should confirm Vashya and Gana tables.
"""
from .jyotish import SIGN_LORD, natural_relation

KOOTA_MAX = {'varna': 1, 'vashya': 2, 'tara': 3, 'yoni': 4, 'graha_maitri': 5, 'gana': 6, 'bhakoot': 7, 'nadi': 8}
KOOTA_TE = {'varna': 'వర్ణ', 'vashya': 'వశ్య', 'tara': 'తార', 'yoni': 'యోని', 'graha_maitri': 'గ్రహ మైత్రి',
            'gana': 'గణ', 'bhakoot': 'భకూట (రాశి)', 'nadi': 'నాడి'}

# Varna by moon sign: 4 Brahmin, 3 Kshatriya, 2 Vaishya, 1 Shudra
VARNA = [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4]
VARNA_NAMES = {4: 'Brahmin', 3: 'Kshatriya', 2: 'Vaishya', 1: 'Shudra'}

VASHYA_CATS = ['Chatushpada', 'Manava', 'Jalachara', 'Vanachara', 'Keeta']
VASHYA_TABLE = [  # groom row, bride col
    [2, 1, 1, 0.5, 1],
    [1, 2, 0.5, 0, 1],
    [1, 0.5, 2, 1, 1],
    [0.5, 0, 1, 2, 0],
    [1, 1, 1, 0, 2],
]


def vashya_cat(moon_lon):
    s, d = int(moon_lon // 30), moon_lon % 30
    if s in (0, 1):
        return 0
    if s in (2, 5, 6, 10):
        return 1
    if s == 8:
        return 1 if d < 15 else 0
    if s == 9:
        return 0 if d < 15 else 2
    if s in (3, 11):
        return 2
    if s == 4:
        return 3
    return 4  # Vrischika


YONI_OF_NAK = [0, 1, 2, 3, 3, 4, 5, 2, 5, 6, 6, 7, 8, 9, 8, 9, 10, 10, 4, 11, 12, 11, 13, 0, 13, 7, 1]
YONI_NAMES = ['Horse', 'Elephant', 'Sheep', 'Serpent', 'Dog', 'Cat', 'Rat', 'Cow', 'Buffalo', 'Tiger',
              'Deer', 'Monkey', 'Mongoose', 'Lion']
YONI_TABLE = [
    [4, 2, 2, 3, 2, 2, 2, 1, 0, 1, 3, 3, 2, 1],
    [2, 4, 3, 3, 2, 2, 2, 2, 3, 1, 2, 3, 2, 0],
    [2, 3, 4, 2, 1, 2, 1, 3, 3, 1, 2, 0, 3, 1],
    [3, 3, 2, 4, 2, 1, 1, 1, 1, 2, 2, 2, 0, 2],
    [2, 2, 1, 2, 4, 2, 1, 2, 2, 1, 0, 2, 1, 1],
    [2, 2, 2, 1, 2, 4, 0, 2, 2, 1, 3, 3, 2, 1],
    [2, 2, 1, 1, 1, 0, 4, 2, 2, 2, 2, 2, 1, 2],
    [1, 2, 3, 1, 2, 2, 2, 4, 3, 0, 3, 2, 2, 1],
    [0, 3, 3, 1, 2, 2, 2, 3, 4, 1, 2, 2, 2, 1],
    [1, 1, 1, 2, 1, 1, 2, 0, 1, 4, 1, 1, 2, 1],
    [3, 2, 2, 2, 0, 3, 2, 3, 2, 1, 4, 2, 2, 1],
    [3, 3, 0, 2, 2, 3, 2, 2, 2, 1, 2, 4, 3, 2],
    [2, 2, 3, 0, 1, 2, 1, 2, 2, 2, 2, 3, 4, 2],
    [1, 0, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 4],
]

# 0 Deva, 1 Manushya, 2 Rakshasa
GANA_OF_NAK = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]
GANA_NAMES = ['Deva', 'Manushya', 'Rakshasa']
GANA_TABLE = [[6, 6, 1], [5, 6, 0], [1, 0, 6]]  # groom row, bride col

NADI_NAMES = ['Adi', 'Madhya', 'Antya']


def nadi_of(nak):
    return [0, 1, 2, 2, 1, 0][nak % 6]


# Rajju: 0 Pada, 1 Kati, 2 Nabhi, 3 Kantha, 4 Siro — pattern over 27 nakshatras
RAJJU_PATTERN = [0, 1, 2, 3, 4, 3, 2, 1, 0]
RAJJU_NAMES = ['Pada', 'Kati', 'Nabhi', 'Kantha', 'Siro']
VEDHA_PAIRS = {frozenset(p) for p in [(0, 17), (1, 16), (2, 15), (3, 14), (5, 21), (6, 20), (7, 19), (8, 18),
                                      (9, 26), (10, 25), (11, 24), (12, 23), (4, 13), (13, 22), (4, 22)]}
# Mrigashira(4)-Dhanishta(22)-Chitra(13) form the classic triple vedha group


def rajju_of(nak):
    return RAJJU_PATTERN[nak % 9]


def kuja_dosha(chart):
    """Mars in 1,2,4,7,8,12 from Lagna, Moon and Venus."""
    g = {x['key']: x for x in chart['grahas']}
    mars = g['mars']['sign']['index']
    refs = {'lagna': chart['lagna']['sign']['index'], 'moon': g['moon']['sign']['index'],
            'venus': g['venus']['sign']['index']}
    hits = {}
    for k, s in refs.items():
        h = (mars - s) % 12 + 1
        hits[k] = {'house': h, 'dosha': h in (1, 2, 4, 7, 8, 12)}
    exceptions = []
    if g['mars']['dignity'] in ('own', 'exalted', 'moolatrikona'):
        exceptions.append('Mars in own/exaltation sign — dosha considered cancelled')
    present = hits['lagna']['dosha'] or hits['moon']['dosha']
    return {'present': present and not exceptions, 'from': hits, 'exceptions': exceptions}


def _moon(chart):
    m = next(x for x in chart['grahas'] if x['key'] == 'moon')
    return m['longitude'], m['nakshatra']['index'], m['sign']['index']


def match(boy_chart, girl_chart):
    b_lon, b_nak, b_sign = _moon(boy_chart)
    g_lon, g_nak, g_sign = _moon(girl_chart)
    k = {}

    k['varna'] = {'score': 1 if VARNA[b_sign] >= VARNA[g_sign] else 0,
                  'boy': VARNA_NAMES[VARNA[b_sign]], 'girl': VARNA_NAMES[VARNA[g_sign]]}

    bv, gv = vashya_cat(b_lon), vashya_cat(g_lon)
    k['vashya'] = {'score': VASHYA_TABLE[bv][gv], 'boy': VASHYA_CATS[bv], 'girl': VASHYA_CATS[gv]}

    def tara_ok(frm, to):
        r = ((to - frm) % 27) % 9 + 1
        return r not in (3, 5, 7)
    k['tara'] = {'score': 1.5 * tara_ok(g_nak, b_nak) + 1.5 * tara_ok(b_nak, g_nak),
                 'boy': ((b_nak - g_nak) % 27) % 9 + 1, 'girl': ((g_nak - b_nak) % 27) % 9 + 1}

    by, gy = YONI_OF_NAK[b_nak], YONI_OF_NAK[g_nak]
    k['yoni'] = {'score': YONI_TABLE[by][gy], 'boy': YONI_NAMES[by], 'girl': YONI_NAMES[gy]}

    bl, gl = SIGN_LORD[b_sign], SIGN_LORD[g_sign]
    if bl == gl:
        gm = 5
    else:
        pair = sorted([natural_relation(bl, gl), natural_relation(gl, bl)])
        gm = {('friend', 'friend'): 5, ('friend', 'neutral'): 4, ('neutral', 'neutral'): 3,
              ('enemy', 'friend'): 1, ('enemy', 'neutral'): 0.5, ('enemy', 'enemy'): 0}[tuple(pair)]
    k['graha_maitri'] = {'score': gm, 'boy': bl, 'girl': gl}

    bg, gg = GANA_OF_NAK[b_nak], GANA_OF_NAK[g_nak]
    k['gana'] = {'score': GANA_TABLE[bg][gg], 'boy': GANA_NAMES[bg], 'girl': GANA_NAMES[gg]}

    dist = (b_sign - g_sign) % 12 + 1
    bad = dist in (2, 12, 5, 9, 6, 8)
    k['bhakoot'] = {'score': 0 if bad else 7, 'boy': dist, 'girl': (g_sign - b_sign) % 12 + 1}

    bn, gn = nadi_of(b_nak), nadi_of(g_nak)
    k['nadi'] = {'score': 0 if bn == gn else 8, 'boy': NADI_NAMES[bn], 'girl': NADI_NAMES[gn]}

    for key in k:
        k[key]['max'] = KOOTA_MAX[key]
        k[key]['name_telugu'] = KOOTA_TE[key]
    total = sum(v['score'] for v in k.values())

    rajju_same = rajju_of(b_nak) == rajju_of(g_nak)
    vedha = frozenset((b_nak, g_nak)) in VEDHA_PAIRS
    boy_kuja, girl_kuja = kuja_dosha(boy_chart), kuja_dosha(girl_chart)

    if total >= 28:
        verdict = 'Excellent match'
    elif total >= 21:
        verdict = 'Good match'
    elif total >= 18:
        verdict = 'Average — acceptable with other factors'
    else:
        verdict = 'Not recommended by Guna score'

    notes = []
    if k['nadi']['score'] == 0:
        notes.append('Nadi dosha (same Nadi). Traditionally cancelled if same rasi with different nakshatra, '
                     'or same nakshatra with different rasi/pada.')
    if k['bhakoot']['score'] == 0:
        notes.append('Bhakoot dosha. Often cancelled when both moon-sign lords are the same or mutual friends.')
    if rajju_same:
        notes.append(f'Rajju dosha: both in {RAJJU_NAMES[rajju_of(b_nak)]} rajju (South Indian check).')
    if vedha:
        notes.append('Vedha dosha between the two nakshatras (South Indian check).')
    if boy_kuja['present'] != girl_kuja['present']:
        notes.append('Kuja dosha present in only one chart — needs astrologer review.')

    return {'kootas': k, 'total': total, 'max': 36, 'verdict': verdict,
            'rajju': {'boy': RAJJU_NAMES[rajju_of(b_nak)], 'girl': RAJJU_NAMES[rajju_of(g_nak)],
                      'dosha': rajju_same},
            'vedha': vedha, 'kuja': {'boy': boy_kuja, 'girl': girl_kuja}, 'notes': notes}
