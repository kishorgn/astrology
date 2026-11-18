"""Parihara puja / dosha nivarana japa suggestions — only for doshas actually found in the chart."""
from .ephemeris import PLANET_NAMES, RASHI_NAMES
from .remedies_data import GRAHA, DOSHA, GRAHA_SHANTI_TITLE, GRAHA_SHANTI_PUJA

GANDANTA = {(0, 1), (9, 1), (18, 1), (8, 4), (17, 4), (26, 4)}   # (nakshatra index, pada)


def _pn(p, lang):
    return PLANET_NAMES[p][lang]


# Telugu compound (samasa) forms: "చంద్ర గ్రహ శాంతి", "కుజ మహాదశ"
TE_STEM = {'sun': 'సూర్య', 'moon': 'చంద్ర', 'mars': 'కుజ', 'mercury': 'బుధ', 'jupiter': 'గురు',
           'venus': 'శుక్ర', 'saturn': 'శని', 'rahu': 'రాహు', 'ketu': 'కేతు'}


def _japa(planets):
    return [{'planet': p, 'name_english': _pn(p, 'english'), 'name_telugu': TE_STEM[p],
             'beeja': GRAHA[p]['beeja'], 'count': GRAHA[p]['count'],
             'day_english': GRAHA[p]['day'][0], 'day_telugu': GRAHA[p]['day'][1]} for p in planets]


def _dosha_item(key, reasons, priority, extra=None):
    d = DOSHA[key]
    g = d['graha']
    item = {'key': key, 'priority': priority, 'title_english': d['title'][0], 'title_telugu': d['title'][1],
            'reasons_english': [r[0] for r in reasons], 'reasons_telugu': [r[1] for r in reasons],
            'puja_english': d['puja'][0], 'puja_telugu': d['puja'][1], 'japa': _japa(g),
            'mantra': d.get('mantra'),
            'dana_english': '; '.join(GRAHA[p]['dana'][0] for p in g) or None,
            'dana_telugu': '; '.join(GRAHA[p]['dana'][1] for p in g) or None,
            'temple_english': d['temple'][0] if d.get('temple') else None,
            'temple_telugu': d['temple'][1] if d.get('temple') else None}
    if extra:
        item.update(extra)
    return item


def _graha_item(p, reasons, priority):
    G = GRAHA[p]
    return {'key': f'graha_{p}', 'priority': priority,
            'title_english': GRAHA_SHANTI_TITLE[0].format(planet=_pn(p, 'english')),
            'title_telugu': GRAHA_SHANTI_TITLE[1].format(planet=TE_STEM[p]),
            'reasons_english': [r[0] for r in reasons], 'reasons_telugu': [r[1] for r in reasons],
            'puja_english': GRAHA_SHANTI_PUJA[0].format(deity=G['deity'][0], day=G['day'][0], stotra=G['stotra'][0]),
            'puja_telugu': GRAHA_SHANTI_PUJA[1].format(deity_te=G['deity'][1], day_te=G['day'][1], stotra_te=G['stotra'][1]),
            'japa': _japa([p]), 'mantra': None,
            'dana_english': G['dana'][0], 'dana_telugu': G['dana'][1], 'temple_english': None, 'temple_telugu': None}


def chart_remedies(chart, dasha, yogas, kuja, gochara):
    g = {x['key']: x for x in chart['grahas']}
    sign = {k: v['sign']['index'] for k, v in g.items()}
    lag = chart['lagna']['sign']['index']
    house = {k: (s - lag) % 12 + 1 for k, s in sign.items()}
    pan = chart['panchanga']
    out = []

    # --- doshas
    if kuja['status'] == 'present':
        frm = [k for k, v in kuja['from'].items() if v['dosha'] and k != 'venus']
        out.append(_dosha_item('kuja', [(
            f"Mars in house {kuja['from'][frm[0]]['house']} from {'Lagna' if frm[0] == 'lagna' else 'Moon'}, no cancellation applies",
            f"{'లగ్నం' if frm[0] == 'lagna' else 'చంద్రుని'} నుండి {kuja['from'][frm[0]]['house']}వ స్థానంలో కుజుడు; భంగం లేదు")], 1))
    ykeys = {y['key'] for y in yogas}
    if 'kalasarpa' in ykeys:
        out.append(_dosha_item('kalasarpa', [('All seven planets lie between Rahu and Ketu',
                                              'ఏడు గ్రహాలూ రాహు-కేతువుల మధ్య ఉన్నాయి')], 1))
    if 'kemadruma' in ykeys:
        out.append(_dosha_item('kemadruma', [('No planets on either side of the Moon and no cancellation',
                                              'చంద్రునికి ఇరువైపులా గ్రహాలు లేవు; భంగం లేదు')], 2))
    sh = gochara.get('shani')
    if sh:
        key = {'sade_sati': 'sade_sati', 'ashtama': 'ashtama', 'ardhashtama': 'ardhashtama'}[sh['type']]
        out.append(_dosha_item(key, [(f"Saturn now transits house {sh['house']} from the Janma Rasi ({sh['name_english']})",
                                      f"ప్రస్తుతం శని జన్మ రాశి నుండి {sh['house']}వ స్థానంలో ({sh['name_telugu']})")],
                               1 if key != 'ardhashtama' else 2, {'transit': True}))
    for lum, key in (('sun', 'grahana_sun'), ('moon', 'grahana_moon')):
        nodes = [n for n in ('rahu', 'ketu') if sign[n] == sign[lum]]
        if nodes:
            out.append(_dosha_item(key, [(f"{_pn(lum, 'english')} conjoined with {_pn(nodes[0], 'english')} in {RASHI_NAMES['english'][sign[lum]]}",
                                          f"{RASHI_NAMES['telugu'][sign[lum]]}లో {_pn(lum, 'telugu')}తో {_pn(nodes[0], 'telugu')} కలయిక")], 2))
    nk = pan['nakshatra']
    if (nk['index'], nk['pada']) in GANDANTA:
        out.append(_dosha_item('gandanta', [(f"Born in {nk['name_english']} pada {nk['pada']} (gandanta)",
                                             f"{nk['name_telugu']} {nk['pada']}వ పాదంలో జననం (గండాంతం)")], 2))
    if pan['tithi']['index'] in (29, 30):
        out.append(_dosha_item('amavasya', [(f"Born on {pan['tithi']['name_english']}",
                                             f"{pan['tithi']['name_telugu']} నాడు జననం")], 2))

    # --- graha shanti for afflicted planets (natal debility + afflicted running dasha lords)
    reasons = {}

    def add(p, en, te, pr):
        r = reasons.setdefault(p, {'list': [], 'pr': 9})
        r['list'].append((en, te)); r['pr'] = min(r['pr'], pr)

    cur = dasha.get('current') or []
    for lvl, (en_l, te_l) in zip(cur[:2], (('Mahadasha', 'మహాదశ'), ('Antardasha', 'అంతర్దశ'))):
        p = lvl['lord']
        x = g[p]
        why = []
        if x['dignity'] == 'debilitated' and f'neechabhanga_{p}' not in ykeys:
            why.append(('debilitated', 'నీచ'))
        if x['combust']:
            why.append(('combust', 'అస్తంగతం'))
        if house[p] in (6, 8, 12) and en_l == 'Mahadasha':   # placement alone counts only for the long Mahadasha
            why.append((f'in house {house[p]}', f'{house[p]}వ స్థానంలో'))
        if why:
            add(p, f"Running {_pn(p, 'english')} {en_l} ({lvl['start']} – {lvl['end']}); {_pn(p, 'english')} is " + ', '.join(w[0] for w in why),
                f"ప్రస్తుతం {TE_STEM[p]} {te_l} ({lvl['start']} – {lvl['end']}); {_pn(p, 'telugu')} " + ', '.join(w[1] for w in why), 1)
    for p, x in g.items():
        if p in ('rahu', 'ketu'):
            continue
        if x['dignity'] == 'debilitated' and f'neechabhanga_{p}' not in ykeys:   # skip when debility is cancelled
            add(p, f"{_pn(p, 'english')} is debilitated in {x['sign']['name_english']}",
                f"{_pn(p, 'telugu')} {x['sign']['name_telugu']}లో నీచ", 3)
    for p, r in reasons.items():
        out.append(_graha_item(p, r['list'], r['pr']))

    out.sort(key=lambda i: i['priority'])
    return out


def match_remedies(result):
    out = []
    D = result['doshas']
    rows = {r['key']: r for r in result['poruthams']['rows']}
    if rows['rajju']['result'] == 'bad':
        out.append(_dosha_item('rajju', [('Both nakshatras fall in the same Rajju', 'ఇద్దరి నక్షత్రాలు ఒకే రజ్జులో')], 1))
    if rows['vedha']['result'] == 'bad':
        out.append(_dosha_item('vedha', [('The two nakshatras are in Vedha', 'రెండు నక్షత్రాల మధ్య వేధ')], 1))
    if D['nadi']['result'] == 'bad':
        out.append(_dosha_item('nadi', [('Both have the same Nadi and no cancellation applies', 'ఇద్దరిదీ ఒకే నాడి; భంగం లేదు')], 1))
    if D['bhakoot']['result'] == 'bad':
        out.append(_dosha_item('bhakoot', [(f"Rasi count {D['bhakoot']['count']} (2/12, 5/9 or 6/8) without cancellation",
                                            f"రాశి లెక్క {D['bhakoot']['count']} (2/12, 5/9, 6/8); భంగం లేదు")], 2))
    k = D['kuja']
    if k['result'] == 'bad':
        who = 'boy' if k['boy'] == 'present' else 'girl'
        out.append(_dosha_item('kuja', [(f"Kuja dosha only in the {'boy' if who == 'boy' else 'girl'}'s chart",
                                         f"{'వరుని' if who == 'boy' else 'వధువు'} జాతకంలో మాత్రమే కుజ దోషం")], 1, {'for': who}))
    return out
