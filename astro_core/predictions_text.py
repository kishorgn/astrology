"""Prediction CONTENT, kept separate from logic.

DRAFT text for the astrologer to review, rewrite and translate. Replace freely — the
engine only looks up keys. Add 'telugu' entries alongside 'english' and the UI will use them.
"""

LAGNA = {'english': [
    'Mesha Lagna: energetic, direct, pioneering. Quick to start, must learn patience to finish. Mars as lagna lord makes health and drive depend on physical activity.',
    'Vrishabha Lagna: steady, patient, comfort-loving. Builds wealth slowly and keeps it. Venus as lagna lord gives artistic taste and attachment to family.',
    'Mithuna Lagna: curious, talkative, adaptable. Does well with communication, trade and learning. Restlessness is the main weakness.',
    'Karkataka Lagna: emotional, caring, protective of family. Strong intuition; moods follow the Moon. Home and mother are central themes.',
    'Simha Lagna: dignified, generous, wants recognition. Natural leader; pride can create conflict with authority.',
    'Kanya Lagna: analytical, precise, service-minded. Good with detail, accounts and health fields; tends to worry.',
    'Tula Lagna: balanced, diplomatic, partnership-oriented. Values fairness and beauty; decisions can be slow.',
    'Vrischika Lagna: intense, secretive, determined. Deep research ability and resilience; must manage anger and suspicion.',
    'Dhanus Lagna: optimistic, principled, fond of learning and travel. Teaching, law and dharma suit well.',
    'Makara Lagna: disciplined, practical, ambitious. Success comes late but lasts; responsibilities come early.',
    'Kumbha Lagna: independent, humanitarian, unconventional thinker. Good with groups, technology and social causes.',
    'Meena Lagna: compassionate, imaginative, spiritual. Sensitive to surroundings; needs clear boundaries.',
]}

MOON_SIGN = {'english': [
    'Moon in Mesha: quick emotional reactions, courage, impatience.',
    'Moon in Vrishabha (exalted): emotional stability, contentment, love of comforts.',
    'Moon in Mithuna: lively mind, needs variety and conversation.',
    'Moon in Karkataka (own): deeply caring, attached to home and mother.',
    'Moon in Simha: proud, warm-hearted, needs appreciation.',
    'Moon in Kanya: practical, critical, finds peace in order and service.',
    'Moon in Tula: seeks harmony and companionship; dislikes conflict.',
    'Moon in Vrischika (debilitated): intense feelings, prone to anxiety; strong recovery power.',
    'Moon in Dhanus: optimistic, religious-minded, freedom-loving.',
    'Moon in Makara: reserved, dutiful, emotionally cautious.',
    'Moon in Kumbha: detached, idealistic, friendly with many.',
    'Moon in Meena: tender, intuitive, devotional.',
]}

DASHA_LORD = {'english': {
    'sun': 'Sun dasha brings matters of authority, government, father and self-confidence to the front. Health of heart/eyes needs care.',
    'moon': 'Moon dasha emphasises mind, mother, home, public dealings and travel. Emotional ups and downs follow the Moon\'s strength.',
    'mars': 'Mars dasha gives energy, property matters, competition, siblings and technical work. Avoid haste and disputes.',
    'mercury': 'Mercury dasha favours studies, business, writing, communication and analytical work.',
    'jupiter': 'Jupiter dasha supports growth, children, teachers, wealth, dharma and good counsel.',
    'venus': 'Venus dasha brings marriage, comforts, vehicles, arts and luxury. Relationships are central.',
    'saturn': 'Saturn dasha rewards discipline and hard work; delays, responsibilities and lessons of patience.',
    'rahu': 'Rahu dasha brings sudden changes, ambition, foreign links and unconventional paths; clarity of intent is key.',
    'ketu': 'Ketu dasha turns the mind inward: detachment, spirituality, research; material matters can feel unsettled.',
}}

HOUSE_LORD_TEMPLATE = {'english': 'Lord of house {h} ({h_theme}) is placed in house {p} ({p_theme}). '
                                  'Matters of {h_theme_short} get linked to {p_theme_short}.'}

DIGNITY_NOTE = {'english': {
    'exalted': '{planet} is exalted — its significations flourish.',
    'debilitated': '{planet} is debilitated — its significations need effort and remedies.',
    'own': '{planet} is in its own sign — stable, self-reliant results.',
    'moolatrikona': '{planet} is in moolatrikona — strong and dependable.',
}}
