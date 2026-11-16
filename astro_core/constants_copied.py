"""Shared names/constants — copied verbatim from ephemeris_web_02/app.py (lines 98-187).
Keep in sync with the Panchangam app so both show identical Telugu/English names."""
import swisseph as swe

# --- FIX: Corrected Tithi Name Definitions ---
# Base names (1-14)
TITHI_NAMES_BASE_EN = ['Prathama', 'Dwitiya', 'Tritiya', 'Chaturthi', 'Panchami', 'Shashti', 'Saptami', 'Ashtami',
                       'Navami', 'Dashami', 'Ekadashi', 'Dwadashi', 'Trayodashi', 'Chaturdashi']
TITHI_NAMES_BASE_TE = ['పాడ్యమి', 'విదియ', 'తదియ', 'చవితి', 'పంచమి', 'షష్ఠి', 'సప్తమి', 'అష్టమి', 'నవమి', 'దశమి',
                       'ఏకాదశి', 'ద్వాదశి', 'త్రయోదశి', 'చతుర్దశి']

TITHI_NAMES = {
    'english': [''] + TITHI_NAMES_BASE_EN + ['Purnima'] + TITHI_NAMES_BASE_EN + ['Amavasya'],
    'telugu': [''] + TITHI_NAMES_BASE_TE + ['పూర్ణిమ'] + TITHI_NAMES_BASE_TE + ['అమావాస్య']
}
# --- END FIX ---

NAKSHATRA_NAMES = {
    'english': ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Arudra', 'Punarvasu', 'Pushyami', 'Ashlesha',
                'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha',
                'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
                'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'],
    'telugu': ['అశ్వని', 'భరణి', 'కృత్తిక', 'రోహిణి', 'మృగశిర', 'ఆరుద్ర', 'పునర్వసు', 'పుష్యమి', 'ఆశ్లేష', 'మఖ',
               'పుబ్బ', 'ఉత్తర', 'హస్త', 'చిత్త', 'స్వాతి', 'విశాఖ', 'అనురాధ', 'జ్యేష్ఠ', 'మూల',
               'పూర్వాషాఢ', 'ఉత్తరాషాఢ', 'శ్రవణం', 'ధనిష్ట', 'శతభిషం', 'పూర్వాభాద్ర', 'ఉత్తరాభాద్ర', 'రేవతి']}
YOGA_NAMES = {
    'english': ['', 'Vishkambha', 'Priti', 'Ayushman', 'Saubhagya', 'Shobhana', 'Atiganda', 'Sukarma', 'Dhriti',
                'Shula', 'Ganda', 'Vriddhi', 'Dhruva', 'Vyaghata', 'Harshana', 'Vajra', 'Siddhi', 'Vyatipata',
                'Variyana', 'Parigha', 'Shiva', 'Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma', 'Indra', 'Vaidhriti'],
    'telugu': ['', 'విష్కంభ', 'ప్రీతి', 'ఆయుష్మాన్', 'సౌభాగ్య', 'శోభన', 'అతిగండ', 'సుకర్మ', 'ధృతి', 'శూల', 'గండ',
               'వృద్ధి', 'ధృవ', 'వ్యాఘాత', 'హర్షణ', 'వజ్ర', 'సిద్ధి', 'వ్యతీపాత', 'వరీయాన్', 'పరిఘ', 'శివ', 'సిద్ధ',
               'సాధ్య', 'శుభ', 'శుక్ల', 'బ్రహ్మ', 'ఇంద్ర', 'వైధృతి']}
KARANA_NAMES = {
    'english': ['', 'Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti', 'Shakuni', 'Chatushpada',
                'Naga', 'Kimstughna'],
    'telugu': ['', 'బవ', 'బాలవ', 'కౌలవ', 'తైతిల', 'గర', 'వణిజ', 'విష్టి', 'శకుని', 'చతుష్పాద', 'నాగ', 'కిమ్స్తుఘ్న']}
RASHI_NAMES = {
    'english': ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn',
                'Aquarius', 'Pisces'],
    'telugu': ['మేష', 'వృషభ', 'మిథున', 'కర్కాటక', 'సింహ', 'కన్య', 'తులా', 'వృశ్చిక', 'ధనుస్సు', 'మకర', 'కుంభ', 'మీన']}
VARAM_NAMES = {'english': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
               'telugu': ['ఆదివారం', 'సోమవారం', 'మంగళవారం', 'బుధవారం', 'గురువారం', 'శుక్రవారం', 'శనివారం']}
PLANET_NAMES = {'sun': {'english': 'Sun', 'telugu': 'సూర్యుడు'}, 'moon': {'english': 'Moon', 'telugu': 'చంద్రుడు'},
                'mars': {'english': 'Mars', 'telugu': 'మంగళ'}, 'mercury': {'english': 'Mercury', 'telugu': 'బుధ'},
                'jupiter': {'english': 'Jupiter', 'telugu': 'గురు'}, 'venus': {'english': 'Venus', 'telugu': 'శుక్ర'},
                'saturn': {'english': 'Saturn', 'telugu': 'శని'}, 'rahu': {'english': 'Rahu', 'telugu': 'రాహు'},
                'ketu': {'english': 'Ketu', 'telugu': 'కేతు'}}
INDIAN_MONTHS = {
    'english': ['Chaitra', 'Vaisakha', 'Jyeshtha', 'Ashadha', 'Shravana', 'Bhadrapada', 'Ashvina', 'Kartika',
                'Margashirsha', 'Pausha', 'Magha', 'Phalguna'],
    'telugu': ['చైత్ర', 'వైశాఖ', 'జ్యేష్ఠ', 'ఆషాఢ', 'శ్రావణ', 'భాద్రపద', 'ఆశ్వయుజ', 'కార్తీక', 'మార్గశిర', 'పుష్య',
               'మాఘ', 'ఫాల్గుణ']}

# --- NEW: Telugu Year (Samvatsara) Constants ---
TELUGU_YEAR_NAMES_EN = [
    'Prabhava', 'Vibhava', 'Shukla', 'Pramoduta', 'Prajothpatti', 'Angirasa', 'Shrimukha', 'Bhava', 'Yuva', 'Dhatri',
    'Ishwara', 'Bahudhanya', 'Pramadi', 'Vikrama', 'Vishu', 'Chitrabhanu', 'Swabhanu', 'Tarana', 'Parthiva', 'Vyaya',
    'Sarvajit', 'Sarvadhari', 'Virodhi', 'Vikriti', 'Khara', 'Nandana', 'Vijaya', 'Jaya', 'Manmatha', 'Durmukhi',
    'Hevilambi', 'Vilambi', 'Vikari', 'Sharvari', 'Plava', 'Shubhakriti', 'Shobhakriti', 'Krodhi', 'Vishwavasu',
    'Parabhava', 'Plavanga', 'Kilaka', 'Saumya', 'Sadharana', 'Virodhikriti', 'Paridhavi', 'Pramadicha', 'Ananda',
    'Rakshasa', 'Nala', 'Pingala', 'Kalayukti', 'Siddharthi', 'Raudri', 'Durmati', 'Dundubhi', 'Rudhirodgari',
    'Raktakshi', 'Krodhana', 'Akshaya'
]
TELUGU_YEAR_NAMES_TE = [
    'ప్రభవ', 'విభవ', 'శుక్ల', 'ప్రమోదూత', 'ప్రజోత్పత్తి', 'ఆంగీరస', 'శ్రీముఖ', 'భావ', 'యువ', 'ధాత్రి',
    'ఈశ్వర', 'బహుధాన్య', 'ప్రమాది', 'విక్రమ', 'విషు', 'చిత్రభాను', 'స్వభాను', 'తారణ', 'పార్థివ', 'వ్యయ',
    'సర్వజిత్', 'సర్వధారి', 'విరోధి', 'వికృతి', 'ఖర', 'నందన', 'విజయ', 'జయ', 'మన్మథ', 'దుర్ముఖి',
    'హేవిళంబి', 'విళంబి', 'వికారి', 'శార్వరి', 'ప్లవ', 'శుభకృతి', 'శోభకృతి', 'క్రోధి', 'విశ్వావసు',
    'పరాభవ', 'ప్లవంగ', 'కీలక', 'సౌమ్య', 'సాధారణ', 'విరోధికృతి', 'పరిధావి', 'ప్రమాదీచ', 'ఆనంద',
    'రాక్షస', 'నళ', 'పింగళ', 'కాళయుక్తి', 'సిద్ధార్థి', 'రౌద్రి', 'దుర్మతి', 'దుందుభి', 'రుధిరోద్గారి',
    'రక్తాక్షి', 'క్రోధన', 'అక్షయ'
]
UGADI_CUTOFF_HOUR = 8.5  # 8:30 AM
UGADI_ANCHOR_YEAR = 1987  # Gregorian year 1987 was Prabhava (index 0)
# --- END NEW CONSTANTS ---

PLANET_MAP_SWE = {'sun': swe.SUN, 'moon': swe.MOON, 'mars': swe.MARS, 'mercury': swe.MERCURY,
                  'jupiter': swe.JUPITER, 'venus': swe.VENUS, 'saturn': swe.SATURN,
                  'rahu': swe.TRUE_NODE, 'ketu': swe.TRUE_NODE}

PLANET_ID_TO_NAME_MAP = {
    swe.SUN: 'Sun',
    swe.MOON: 'Moon',
    swe.MARS: 'Mars',
    swe.MERCURY: 'Mercury',
    swe.JUPITER: 'Jupiter',
    swe.VENUS: 'Venus',
    swe.SATURN: 'Saturn',
    swe.TRUE_NODE: 'Rahu/Ketu Node'  # This will be refined by the 'is_ketu' flag
}

# --- DURMUHURTHAM FIX (Req 4) ---
# --- DELETED Old DURMUHURTHAM_RULES constant ---
# --- The correct rules are now defined inside calculate_inauspicious_timings ---
