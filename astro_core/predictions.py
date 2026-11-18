"""Assemble rule-based life predictions from the computed chart, dasha and yogas.

Every section carries items_english and items_telugu (plus 'items' in the requested
language), so the UI can switch language without asking the server again.
"""
from .jyotish import SIGN_LORD, HOUSE_THEMES
from .constants_copied import PLANET_NAMES
from . import predictions_text as T

LANGS = ('english', 'telugu')


def _txt(table, lang):
    return table.get(lang) or table['english']


def _items(chart, dasha, yogas, lang):
    """Return {section_key: [items]} for one language."""
    lag = chart['lagna']['sign']['index']
    moon = next(g for g in chart['grahas'] if g['key'] == 'moon')
    pname = lambda k: PLANET_NAMES[k][lang]
    out = {'lagna': [_txt(T.LAGNA, lang)[lag]],
           'moon': [_txt(T.MOON_SIGN, lang)[moon['sign']['index']]]}

    themes = HOUSE_THEMES.get(lang, HOUSE_THEMES['english'])
    tmpl = _txt(T.HOUSE_LORD_TEMPLATE, lang)
    by_key = {g['key']: g for g in chart['grahas']}
    out['lords'] = []
    for h in (1, 2, 4, 5, 7, 9, 10, 11):
        p = by_key[SIGN_LORD[(lag + h - 1) % 12]]['house_whole_sign']
        out['lords'].append(tmpl.format(h=h, p=p, h_theme=themes[h - 1], p_theme=themes[p - 1],
                                        h_theme_short=themes[h - 1].split(',')[0],
                                        p_theme_short=themes[p - 1].split(',')[0]))

    dn = _txt(T.DIGNITY_NOTE, lang)
    out['strength'] = [dn[g['dignity']].format(planet=pname(g['key']))
                       for g in chart['grahas'] if g['dignity'] in dn]

    out['dasha'] = []
    if dasha.get('current'):
        cur, dl = dasha['current'], _txt(T.DASHA_LORD, lang)
        md = cur[0]
        out['dasha'].append(_txt(T.RUNNING_MAHADASHA, lang).format(lord=pname(md['lord']), start=md['start'],
                                                                   end=md['end']) + dl[md['lord']])
        if len(cur) > 1:
            ad = cur[1]
            out['dasha'].append(_txt(T.RUNNING_ANTARDASHA, lang).format(lord=pname(ad['lord']), end=ad['end'])
                                + dl[ad['lord']])

    desc = 'description_telugu' if lang == 'telugu' else 'description'
    out['yogas'] = [f"{y['name_' + lang]}: {y.get(desc) or y['description']}" for y in yogas]
    return out


SECTIONS = [('lagna', 'Lagna (Ascendant)', 'లగ్న ఫలం'),
            ('moon', 'Janma Rasi (Moon sign)', 'జన్మ రాశి ఫలం'),
            ('lords', 'House lords (Bhavadhipati phalam)', 'భావాధిపతి ఫలం'),
            ('strength', 'Planetary strength', 'గ్రహ బలం'),
            ('dasha', 'Current Dasha', 'ప్రస్తుత దశ'),
            ('yogas', 'Yogas', 'యోగాలు')]


def predictions(chart, dasha, yogas, lang='english'):
    both = {l: _items(chart, dasha, yogas, l) for l in LANGS}
    lang = lang if lang in LANGS else 'english'
    sections = []
    for key, en, te in SECTIONS:
        if not both['english'][key]:
            continue
        sections.append({'key': key, 'title_english': en, 'title_telugu': te,
                         'items_english': both['english'][key], 'items_telugu': both['telugu'][key],
                         'items': both[lang][key]})
    return sections
