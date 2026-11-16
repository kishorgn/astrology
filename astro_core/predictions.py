"""Assemble rule-based life predictions from the computed chart, dasha and yogas."""
from .jyotish import SIGN_LORD, HOUSE_THEMES
from . import predictions_text as T


def _txt(table, lang):
    return table.get(lang) or table['english']


def predictions(chart, dasha, yogas, lang='english'):
    lag = chart['lagna']['sign']['index']
    moon = next(g for g in chart['grahas'] if g['key'] == 'moon')
    sections = []

    sections.append({'title_english': 'Lagna (Ascendant)', 'title_telugu': 'లగ్న ఫలం',
                     'items': [_txt(T.LAGNA, lang)[lag]]})
    sections.append({'title_english': 'Janma Rasi (Moon sign)', 'title_telugu': 'జన్మ రాశి ఫలం',
                     'items': [_txt(T.MOON_SIGN, lang)[moon['sign']['index']]]})

    themes = HOUSE_THEMES.get(lang, HOUSE_THEMES['english'])
    tmpl = _txt(T.HOUSE_LORD_TEMPLATE, lang)
    by_key = {g['key']: g for g in chart['grahas']}
    items = []
    for h in (1, 2, 4, 5, 7, 9, 10, 11):
        lord = SIGN_LORD[(lag + h - 1) % 12]
        p = by_key[lord]['house_whole_sign']
        items.append(tmpl.format(h=h, p=p, h_theme=themes[h - 1], p_theme=themes[p - 1],
                                 h_theme_short=themes[h - 1].split(',')[0],
                                 p_theme_short=themes[p - 1].split(',')[0]))
    sections.append({'title_english': 'House lords (Bhavadhipati phalam)', 'title_telugu': 'భావాధిపతి ఫలం',
                     'items': items})

    dn = _txt(T.DIGNITY_NOTE, lang)
    dig = [dn[g['dignity']].format(planet=g['name_english']) for g in chart['grahas'] if g['dignity'] in dn]
    if dig:
        sections.append({'title_english': 'Planetary strength', 'title_telugu': 'గ్రహ బలం', 'items': dig})

    if dasha.get('current'):
        cur = dasha['current']
        dl = _txt(T.DASHA_LORD, lang)
        items = [f"Running {cur[0]['lord'].title()} Mahadasha ({cur[0]['start']} – {cur[0]['end']}). "
                 + dl[cur[0]['lord']]]
        if len(cur) > 1:
            items.append(f"Antardasha of {cur[1]['lord'].title()} until {cur[1]['end']}: "
                         + dl[cur[1]['lord']])
        sections.append({'title_english': 'Current Dasha', 'title_telugu': 'ప్రస్తుత దశ', 'items': items})

    if yogas:
        sections.append({'title_english': 'Yogas', 'title_telugu': 'యోగాలు',
                         'items': [f"{y['name_english']}: {y['description']}" for y in yogas]})
    return sections
