"""Rule-based yoga detection on the Rasi chart (whole-sign houses from Lagna)."""
from .jyotish import SIGN_LORD, KENDRA, TRIKONA, DUSTHANA, EXALTATION, OWN_SIGNS
from .constants_copied import PLANET_NAMES


def _en(p):
    return PLANET_NAMES[p]['english']


def _te(p):
    return PLANET_NAMES[p]['telugu']


def _ctx(chart):
    g = {x['key']: x for x in chart['grahas']}
    lag = chart['lagna']['sign']['index']
    sign = {k: v['sign']['index'] for k, v in g.items()}
    house = {k: (s - lag) % 12 + 1 for k, s in sign.items()}
    lord_of = {h: SIGN_LORD[(lag + h - 1) % 12] for h in range(1, 13)}
    return g, lag, sign, house, lord_of


def _rel_house(a, b):
    """House of sign b counted from sign a."""
    return (b - a) % 12 + 1


def detect_yogas(chart):
    g, lag, sign, house, lord_of = _ctx(chart)
    found = []

    def add(key, name_en, name_te, desc, desc_te, strength='present'):
        found.append({'key': key, 'name_english': name_en, 'name_telugu': name_te,
                      'description': desc, 'description_telugu': desc_te, 'strength': strength})

    moon = sign['moon']
    # Gaja Kesari
    if _rel_house(moon, sign['jupiter']) in KENDRA:
        add('gajakesari', 'Gaja Kesari Yoga', 'గజకేసరి యోగం',
            'Jupiter in a kendra from the Moon: intelligence, reputation, respect and lasting prosperity.',
            'చంద్రునికి కేంద్రంలో గురువు: బుద్ధి, కీర్తి, గౌరవం, శాశ్వత సంపద.')
    # Budha-Aditya
    if sign['sun'] == sign['mercury'] and not g['mercury']['combust']:
        add('budhaditya', 'Budha-Aditya Yoga', 'బుధాదిత్య యోగం',
            'Sun and Mercury together (Mercury not combust): sharp intellect, communication and administrative skill.',
            'సూర్య బుధులు కలిసి ఉన్నారు (బుధుడు అస్తంగతం కాలేదు): పదునైన బుద్ధి, వాక్చాతుర్యం, పరిపాలనా నైపుణ్యం.')
    elif sign['sun'] == sign['mercury']:
        add('budhaditya', 'Budha-Aditya Yoga (weak)', 'బుధాదిత్య యోగం (బలహీనం)',
            'Sun and Mercury together but Mercury is combust, so the results are reduced.',
            'సూర్య బుధులు కలిసి ఉన్నా బుధుడు అస్తంగతుడు, కాబట్టి ఫలితం తగ్గుతుంది.', 'weak')
    # Chandra-Mangala
    if sign['moon'] == sign['mars']:
        add('chandramangala', 'Chandra-Mangala Yoga', 'చంద్ర మంగళ యోగం',
            'Moon with Mars: earning capacity through enterprise; can make the temperament restless.',
            'చంద్రునితో కుజుడు: స్వయంకృషితో సంపాదన శక్తి; స్వభావంలో అశాంతి కలగవచ్చు.')
    # Pancha Mahapurusha
    pmp = {'mars': ('Ruchaka', 'రుచక'), 'mercury': ('Bhadra', 'భద్ర'), 'jupiter': ('Hamsa', 'హంస'),
           'venus': ('Malavya', 'మాలవ్య'), 'saturn': ('Sasa', 'శశ')}
    for p, (en, te) in pmp.items():
        if house[p] in KENDRA and (sign[p] in OWN_SIGNS[p] or sign[p] == EXALTATION[p][0]):
            add(en.lower(), f'{en} Yoga (Pancha Mahapurusha)', f'{te} యోగం (పంచ మహాపురుష)',
                f'{_en(p)} in own/exaltation sign in a kendra (house {house[p]}): a strong, distinguished personality '
                f'with the qualities of {_en(p)}.',
                f'{_te(p)} స్వక్షేత్రం/ఉచ్ఛలో కేంద్రంలో ({house[p]}వ భావం) ఉన్నాడు: {_te(p)} గుణాలతో బలమైన, '
                f'విశిష్టమైన వ్యక్తిత్వం.')
    # Sunapha / Anapha / Durudhura / Kemadruma
    others = ['mars', 'mercury', 'jupiter', 'venus', 'saturn']
    in2 = [p for p in others if _rel_house(moon, sign[p]) == 2]
    in12 = [p for p in others if _rel_house(moon, sign[p]) == 12]
    if in2 and in12:
        add('durudhura', 'Durudhura Yoga', 'దురుధుర యోగం',
            'Planets on both sides of the Moon: wealth, comforts and support from others.',
            'చంద్రునికి ఇరువైపులా గ్రహాలు: ధనం, సుఖాలు, ఇతరుల సహకారం.')
    elif in2:
        add('sunapha', 'Sunapha Yoga', 'సునఫా యోగం', 'Planet(s) in the 2nd from the Moon: self-earned wealth and good name.',
            'చంద్రునికి 2వ స్థానంలో గ్రహం: స్వయంకృషి ధనం, మంచి పేరు.')
    elif in12:
        add('anapha', 'Anapha Yoga', 'అనఫా యోగం', 'Planet(s) in the 12th from the Moon: good health, charm and contentment.',
            'చంద్రునికి 12వ స్థానంలో గ్రహం: మంచి ఆరోగ్యం, ఆకర్షణ, సంతృప్తి.')
    else:
        with_moon = [p for p in others if sign[p] == moon]
        kendra_lagna = [p for p in others + ['moon'] if house[p] in KENDRA]
        if not with_moon and not kendra_lagna:
            add('kemadruma', 'Kemadruma Yoga', 'కేమద్రుమ యోగం',
                'No planets around the Moon and no cancellation by kendras: periods of struggle and loneliness; '
                'remedies are traditionally advised.',
                'చంద్రుని చుట్టూ గ్రహాలు లేవు, కేంద్రాల ద్వారా భంగం లేదు: కష్టకాలాలు, ఒంటరితనం; '
                'సంప్రదాయంగా పరిహారాలు సూచిస్తారు.', 'adverse')
        else:
            add('kemadruma_cancelled', 'Kemadruma (cancelled)', 'కేమద్రుమ భంగం',
                'Kemadruma forms but is cancelled by planets in kendra / with the Moon.',
                'కేమద్రుమ యోగం ఏర్పడినా కేంద్రంలో / చంద్రునితో ఉన్న గ్రహాల వల్ల భంగమైంది.', 'cancelled')
    # Adhi yoga — benefics in 6,7,8 from Moon
    ben = [p for p in ('mercury', 'jupiter', 'venus') if _rel_house(moon, sign[p]) in (6, 7, 8)]
    if len(ben) >= 2:
        add('adhi', 'Adhi Yoga', 'అధి యోగం',
            'Benefics in the 6th/7th/8th from the Moon: leadership, comfort and victory over opponents.',
            'చంద్రునికి 6/7/8 స్థానాల్లో శుభగ్రహాలు: నాయకత్వం, సుఖం, శత్రు జయం.')
    # Kala Sarpa
    r, k = g['rahu']['longitude'], g['ketu']['longitude']
    seven = [g[p]['longitude'] for p in ('sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn')]
    side_a = all((x - r) % 360 < 180 for x in seven)
    side_b = all((x - k) % 360 < 180 for x in seven)
    if side_a or side_b:
        add('kalasarpa', 'Kala Sarpa Yoga', 'కాలసర్ప యోగం',
            'All seven planets hemmed between Rahu and Ketu: obstacles and delays early, rise after effort.',
            'ఏడు గ్రహాలూ రాహు కేతువుల మధ్య: మొదట్లో ఆటంకాలు, ఆలస్యాలు; ప్రయత్నంతో అభ్యున్నతి.', 'adverse')
    # Raja yoga — kendra lord & trikona lord conjoined or mutual aspect (7th)
    kl = {lord_of[h] for h in (4, 7, 10)} | {lord_of[1]}
    tl = {lord_of[h] for h in (5, 9)} | {lord_of[1]}
    pairs = set()
    for a in kl:
        for b in tl:
            if a != b and (sign[a] == sign[b] or _rel_house(sign[a], sign[b]) == 7):
                pairs.add(tuple(sorted((a, b))))
    for a, b in sorted(pairs):
        add(f'raja_{a}_{b}', f'Raja Yoga ({_en(a)}–{_en(b)})', f'రాజ యోగం ({_te(a)}–{_te(b)})',
            f'Kendra and trikona lords {_en(a)} and {_en(b)} are connected: status, authority and success, '
            f'especially in their dashas.',
            f'కేంద్ర, త్రికోణాధిపతులైన {_te(a)}, {_te(b)} సంబంధం కలిగి ఉన్నారు: హోదా, అధికారం, విజయం, '
            f'ముఖ్యంగా వారి దశల్లో.')
    # Dhana yoga — lords of 2/11 linked to 5/9
    dl = {lord_of[2], lord_of[11]}
    fl = {lord_of[5], lord_of[9]}
    for a in dl:
        for b in fl:
            if a != b and sign[a] == sign[b]:
                add(f'dhana_{a}_{b}', f'Dhana Yoga ({_en(a)}–{_en(b)})', f'ధన యోగం ({_te(a)}–{_te(b)})',
                    'Wealth lords conjoined with fortune lords: accumulation of wealth.',
                    'ధన స్థానాధిపతులు భాగ్య స్థానాధిపతులతో కలిసి ఉన్నారు: ధన సంచయం.')
    # Vipareeta Raja yoga
    for h, nm, te in ((6, 'Harsha', 'హర్ష'), (8, 'Sarala', 'సరళ'), (12, 'Vimala', 'విమల')):
        l = lord_of[h]
        if house[l] in DUSTHANA:
            add(f'vipareeta_{h}', f'{nm} Yoga (Vipareeta Raja)', f'{te} యోగం (విపరీత రాజ)',
                f'Lord of the {h}th placed in a dusthana (house {house[l]}): gains arising from adversity.',
                f'{h}వ భావాధిపతి దుస్థానంలో ({house[l]}వ భావం) ఉన్నాడు: ప్రతికూల పరిస్థితుల నుండి లాభం.')
    # Neecha bhanga (simplified: dispositor of debilitated planet in kendra from lagna or moon)
    for x in chart['grahas']:
        if x['dignity'] == 'debilitated':
            disp = SIGN_LORD[x['sign']['index']]
            if house[disp] in KENDRA or _rel_house(moon, sign[disp]) in KENDRA:
                add(f'neechabhanga_{x["key"]}', f'Neecha Bhanga Raja Yoga ({_en(x["key"])})',
                    f'నీచభంగ రాజ యోగం ({_te(x["key"])})',
                    f'{_en(x["key"])} is debilitated but its dispositor is in a kendra, cancelling the debility.',
                    f'{_te(x["key"])} నీచలో ఉన్నా రాశ్యాధిపతి కేంద్రంలో ఉండటం వల్ల నీచభంగమైంది.')
    return found
