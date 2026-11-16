"""Classical Jyotish reference tables (Parashara / BPHS conventions).

Everything here is data, not logic, so an astrologer can review it in one place.
Sign index: 0 = Mesha (Aries) ... 11 = Meena (Pisces).
Nakshatra index: 0 = Ashwini ... 26 = Revati.
"""

PLANETS = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
SEVEN = PLANETS[:7]

# Positions are taken exactly the way ephemeris_web_02 does it (apparent/sphuta for these
# four, true geometric for the rest) so the two apps never disagree.
SPHUTA_PLANETS = {'jupiter', 'saturn', 'rahu', 'ketu'}

PLANET_ABBR = {
    'english': {'sun': 'Su', 'moon': 'Mo', 'mars': 'Ma', 'mercury': 'Me', 'jupiter': 'Ju',
                'venus': 'Ve', 'saturn': 'Sa', 'rahu': 'Ra', 'ketu': 'Ke', 'lagna': 'Asc'},
    'telugu': {'sun': 'ర', 'moon': 'చం', 'mars': 'కు', 'mercury': 'బు', 'jupiter': 'గు',
               'venus': 'శు', 'saturn': 'శ', 'rahu': 'రా', 'ketu': 'కే', 'lagna': 'ల'},
}

SIGN_LORD = ['mars', 'venus', 'mercury', 'moon', 'sun', 'mercury',
             'venus', 'mars', 'jupiter', 'saturn', 'saturn', 'jupiter']

# Exaltation sign and deep-exaltation degree
EXALTATION = {'sun': (0, 10), 'moon': (1, 3), 'mars': (9, 28), 'mercury': (5, 15),
              'jupiter': (3, 5), 'venus': (11, 27), 'saturn': (6, 20),
              'rahu': (1, 20), 'ketu': (7, 20)}  # Rahu/Ketu: Vrishabha/Vrischika (common Telugu usage)
DEBILITATION = {p: ((s + 6) % 12, d) for p, (s, d) in EXALTATION.items()}

# Moolatrikona: (sign, from_deg, to_deg)
MOOLATRIKONA = {'sun': (4, 0, 20), 'moon': (1, 4, 30), 'mars': (0, 0, 12), 'mercury': (5, 16, 20),
                'jupiter': (8, 0, 10), 'venus': (6, 0, 15), 'saturn': (10, 0, 20)}

OWN_SIGNS = {p: [i for i, l in enumerate(SIGN_LORD) if l == p] for p in SEVEN}

# Naisargika (natural) relationships — BPHS
NATURAL_FRIENDS = {
    'sun': {'friend': ['moon', 'mars', 'jupiter'], 'neutral': ['mercury'], 'enemy': ['venus', 'saturn']},
    'moon': {'friend': ['sun', 'mercury'], 'neutral': ['mars', 'jupiter', 'venus', 'saturn'], 'enemy': []},
    'mars': {'friend': ['sun', 'moon', 'jupiter'], 'neutral': ['venus', 'saturn'], 'enemy': ['mercury']},
    'mercury': {'friend': ['sun', 'venus'], 'neutral': ['mars', 'jupiter', 'saturn'], 'enemy': ['moon']},
    'jupiter': {'friend': ['sun', 'moon', 'mars'], 'neutral': ['saturn'], 'enemy': ['mercury', 'venus']},
    'venus': {'friend': ['mercury', 'saturn'], 'neutral': ['mars', 'jupiter'], 'enemy': ['sun', 'moon']},
    'saturn': {'friend': ['mercury', 'venus'], 'neutral': ['jupiter'], 'enemy': ['sun', 'moon', 'mars']},
}


def natural_relation(p, other):
    if p == other:
        return 'friend'
    rel = NATURAL_FRIENDS[p]
    for k in ('friend', 'neutral', 'enemy'):
        if other in rel[k]:
            return k
    return 'neutral'


NATURAL_BENEFICS = {'jupiter', 'venus', 'mercury', 'moon'}
NATURAL_MALEFICS = {'sun', 'mars', 'saturn', 'rahu', 'ketu'}

# --- Vimshottari ---
DASHA_ORDER = ['ketu', 'venus', 'sun', 'moon', 'mars', 'rahu', 'jupiter', 'saturn', 'mercury']
DASHA_YEARS = {'ketu': 7, 'venus': 20, 'sun': 6, 'moon': 10, 'mars': 7,
               'rahu': 18, 'jupiter': 16, 'saturn': 19, 'mercury': 17}
NAKSHATRA_LORD = [DASHA_ORDER[i % 9] for i in range(27)]

# --- Combustion orbs (degrees from Sun), BPHS/Surya Siddhanta values ---
COMBUST_ORB = {'moon': 12, 'mars': 17, 'mercury': 14, 'jupiter': 11, 'venus': 10, 'saturn': 15}
COMBUST_ORB_RETRO = {'mercury': 12, 'venus': 8}

# --- Shodasha varga ---
VARGAS = [
    ('D1', 1, 'Rasi', 'రాశి', 'Overall life', 'సమగ్ర జీవితం'),
    ('D2', 2, 'Hora', 'హోర', 'Wealth', 'ధనం'),
    ('D3', 3, 'Drekkana', 'ద్రేక్కాణ', 'Siblings, courage', 'సోదరులు, ధైర్యం'),
    ('D4', 4, 'Chaturthamsa', 'చతుర్థాంశ', 'Property, fortune', 'ఆస్తి, భాగ్యం'),
    ('D7', 7, 'Saptamsa', 'సప్తాంశ', 'Children', 'సంతానం'),
    ('D9', 9, 'Navamsa', 'నవాంశ', 'Marriage, dharma', 'వివాహం, ధర్మం'),
    ('D10', 10, 'Dasamsa', 'దశాంశ', 'Career', 'వృత్తి'),
    ('D12', 12, 'Dwadasamsa', 'ద్వాదశాంశ', 'Parents', 'తల్లిదండ్రులు'),
    ('D16', 16, 'Shodasamsa', 'షోడశాంశ', 'Vehicles, comforts', 'వాహనాలు, సుఖాలు'),
    ('D20', 20, 'Vimsamsa', 'వింశాంశ', 'Spiritual progress', 'ఆధ్యాత్మికత'),
    ('D24', 24, 'Chaturvimsamsa', 'చతుర్వింశాంశ', 'Education', 'విద్య'),
    ('D27', 27, 'Bhamsa', 'భాంశ', 'Strengths & weaknesses', 'బలాబలాలు'),
    ('D30', 30, 'Trimsamsa', 'త్రింశాంశ', 'Misfortunes', 'కష్టాలు'),
    ('D40', 40, 'Khavedamsa', 'ఖవేదాంశ', 'Auspicious effects', 'శుభాశుభ ఫలాలు'),
    ('D45', 45, 'Akshavedamsa', 'అక్షవేదాంశ', 'Character', 'శీలం'),
    ('D60', 60, 'Shashtiamsa', 'షష్ట్యంశ', 'Past karma (fine)', 'పూర్వ కర్మ'),
]

# --- Ashtakavarga: benefic houses (counted from reference) — BPHS ---
# Totals: Su 48, Mo 49, Ma 39, Me 54, Ju 56, Ve 52, Sa 39 => SAV 337
ASHTAKAVARGA = {
    'sun': {'sun': [1, 2, 4, 7, 8, 9, 10, 11], 'moon': [3, 6, 10, 11], 'mars': [1, 2, 4, 7, 8, 9, 10, 11],
            'mercury': [3, 5, 6, 9, 10, 11, 12], 'jupiter': [5, 6, 9, 11], 'venus': [6, 7, 12],
            'saturn': [1, 2, 4, 7, 8, 9, 10, 11], 'lagna': [3, 4, 6, 10, 11, 12]},
    'moon': {'sun': [3, 6, 7, 8, 10, 11], 'moon': [1, 3, 6, 7, 10, 11], 'mars': [2, 3, 5, 6, 9, 10, 11],
             'mercury': [1, 3, 4, 5, 7, 8, 10, 11], 'jupiter': [1, 4, 7, 8, 10, 11, 12],
             'venus': [3, 4, 5, 7, 9, 10, 11], 'saturn': [3, 5, 6, 11], 'lagna': [3, 6, 10, 11]},
    'mars': {'sun': [3, 5, 6, 10, 11], 'moon': [3, 6, 11], 'mars': [1, 2, 4, 7, 8, 10, 11],
             'mercury': [3, 5, 6, 11], 'jupiter': [6, 10, 11, 12], 'venus': [6, 8, 11, 12],
             'saturn': [1, 4, 7, 8, 9, 10, 11], 'lagna': [1, 3, 6, 10, 11]},
    'mercury': {'sun': [5, 6, 9, 11, 12], 'moon': [2, 4, 6, 8, 10, 11], 'mars': [1, 2, 4, 7, 8, 9, 10, 11],
                'mercury': [1, 3, 5, 6, 9, 10, 11, 12], 'jupiter': [6, 8, 11, 12],
                'venus': [1, 2, 3, 4, 5, 8, 9, 11], 'saturn': [1, 2, 4, 7, 8, 9, 10, 11],
                'lagna': [1, 2, 4, 6, 8, 10, 11]},
    'jupiter': {'sun': [1, 2, 3, 4, 7, 8, 9, 10, 11], 'moon': [2, 5, 7, 9, 11], 'mars': [1, 2, 4, 7, 8, 10, 11],
                'mercury': [1, 2, 4, 5, 6, 9, 10, 11], 'jupiter': [1, 2, 3, 4, 7, 8, 10, 11],
                'venus': [2, 5, 6, 9, 10, 11], 'saturn': [3, 5, 6, 12], 'lagna': [1, 2, 4, 5, 6, 7, 9, 10, 11]},
    'venus': {'sun': [8, 11, 12], 'moon': [1, 2, 3, 4, 5, 8, 9, 11, 12], 'mars': [3, 5, 6, 9, 11, 12],
              'mercury': [3, 5, 6, 9, 11], 'jupiter': [5, 8, 9, 10, 11], 'venus': [1, 2, 3, 4, 5, 8, 9, 10, 11],
              'saturn': [3, 4, 5, 8, 9, 10, 11], 'lagna': [1, 2, 3, 4, 5, 8, 9, 11]},
    'saturn': {'sun': [1, 2, 4, 7, 8, 10, 11], 'moon': [3, 6, 11], 'mars': [3, 5, 6, 10, 11, 12],
               'mercury': [6, 8, 9, 10, 11, 12], 'jupiter': [5, 6, 11, 12], 'venus': [6, 11, 12],
               'saturn': [3, 5, 6, 11], 'lagna': [1, 3, 4, 6, 10, 11]},
}

# --- Bhava (house) significations used by the prediction templates ---
HOUSE_THEMES = {
    'english': ['self, body, personality', 'wealth, family, speech', 'courage, siblings, efforts',
                'mother, home, comforts, property', 'children, intelligence, past merit',
                'enemies, debts, disease, service', 'spouse, partnerships', 'longevity, sudden events, inheritance',
                'fortune, father, dharma, higher learning', 'career, status, karma', 'gains, income, elder siblings',
                'expenses, losses, foreign lands, moksha'],
    'telugu': ['శరీరం, వ్యక్తిత్వం', 'ధనం, కుటుంబం, వాక్కు', 'ధైర్యం, సోదరులు, ప్రయత్నం',
               'తల్లి, గృహం, సుఖం, ఆస్తి', 'సంతానం, బుద్ధి, పూర్వపుణ్యం', 'శత్రువులు, ఋణం, రోగం, సేవ',
               'జీవిత భాగస్వామి, భాగస్వామ్యం', 'ఆయుష్షు, ఆకస్మిక సంఘటనలు, వారసత్వం',
               'భాగ్యం, తండ్రి, ధర్మం, ఉన్నత విద్య', 'వృత్తి, హోదా, కర్మ', 'లాభం, ఆదాయం, అన్నలు',
               'వ్యయం, నష్టం, విదేశం, మోక్షం'],
}

KENDRA = {1, 4, 7, 10}
TRIKONA = {1, 5, 9}
DUSTHANA = {6, 8, 12}
UPACHAYA = {3, 6, 10, 11}

UI_LABELS = {
    'telugu': {'retro': 'వ', 'combust': 'అ', 'exalted': 'ఉచ్ఛ', 'debilitated': 'నీచ',
               'moolatrikona': 'మూలత్రికోణ', 'own': 'స్వక్షేత్ర', 'friend': 'మిత్ర', 'neutral': 'సమ',
               'enemy': 'శత్రు'},
    'english': {'retro': 'R', 'combust': 'C', 'exalted': 'Exalted', 'debilitated': 'Debilitated',
                'moolatrikona': 'Moolatrikona', 'own': 'Own', 'friend': 'Friendly', 'neutral': 'Neutral',
                'enemy': 'Enemy'},
}
