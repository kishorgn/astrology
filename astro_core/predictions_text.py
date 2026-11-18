"""Prediction CONTENT, kept separate from logic.

DRAFT text for the astrologer to review, rewrite and translate. Replace freely — the
engine only looks up keys. Every table has 'english' and 'telugu'; the UI switches between them.
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
], 'telugu': [
    'మేష లగ్నం: ఉత్సాహం, సూటిదనం, ముందడుగు వేసే స్వభావం. పనులు త్వరగా మొదలుపెడతారు; పూర్తి చేయడానికి ఓర్పు అలవరచుకోవాలి. లగ్నాధిపతి కుజుడు కావడంతో ఆరోగ్యం, చురుకుదనం శారీరక శ్రమపై ఆధారపడతాయి.',
    'వృషభ లగ్నం: స్థిరత్వం, ఓర్పు, సుఖప్రియత్వం. నెమ్మదిగా సంపాదించి నిలబెట్టుకుంటారు. లగ్నాధిపతి శుక్రుడు కళాభిరుచిని, కుటుంబంపై అనురాగాన్ని ఇస్తాడు.',
    'మిథున లగ్నం: జిజ్ఞాస, మాటకారితనం, పరిస్థితులకు అనుగుణంగా మారే గుణం. సంభాషణ, వ్యాపారం, విద్యలో రాణిస్తారు. చంచలత్వం ప్రధాన బలహీనత.',
    'కర్కాటక లగ్నం: భావోద్వేగం, ఆదరణ, కుటుంబ రక్షణ. అంతర్దృష్టి బలంగా ఉంటుంది; మనోభావాలు చంద్రుని అనుసరిస్తాయి. గృహం, తల్లి ముఖ్య విషయాలు.',
    'సింహ లగ్నం: గౌరవం, ఉదారత, గుర్తింపు కోరిక. సహజ నాయకత్వం; అహంకారం అధికారులతో విభేదాలు తేవచ్చు.',
    'కన్య లగ్నం: విశ్లేషణ, ఖచ్చితత్వం, సేవా దృక్పథం. వివరాలు, లెక్కలు, ఆరోగ్య రంగాల్లో నైపుణ్యం; ఆందోళన చెందే స్వభావం.',
    'తులా లగ్నం: సమతుల్యత, దౌత్యం, భాగస్వామ్య దృష్టి. న్యాయం, సౌందర్యానికి విలువ ఇస్తారు; నిర్ణయాలు ఆలస్యం కావచ్చు.',
    'వృశ్చిక లగ్నం: తీవ్రత, గోప్యత, పట్టుదల. లోతైన పరిశోధనా శక్తి, తట్టుకునే బలం; కోపం, అనుమానాన్ని అదుపులో ఉంచుకోవాలి.',
    'ధనుస్సు లగ్నం: ఆశావాదం, నియమనిష్ఠ, విద్య మరియు ప్రయాణాలపై ఆసక్తి. బోధన, న్యాయం, ధర్మ రంగాలు బాగా సరిపోతాయి.',
    'మకర లగ్నం: క్రమశిక్షణ, ఆచరణాత్మకత, ఆశయం. విజయం ఆలస్యంగా వచ్చినా స్థిరంగా ఉంటుంది; బాధ్యతలు చిన్నవయసులోనే వస్తాయి.',
    'కుంభ లగ్నం: స్వతంత్రత, మానవతా దృక్పథం, వినూత్న ఆలోచన. సమూహాలు, సాంకేతికత, సామాజిక సేవలో రాణిస్తారు.',
    'మీన లగ్నం: కరుణ, ఊహాశక్తి, ఆధ్యాత్మికత. పరిసరాలకు సున్నితంగా స్పందిస్తారు; స్పష్టమైన హద్దులు అవసరం.',
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
], 'telugu': [
    'మేష రాశిలో చంద్రుడు: త్వరిత భావస్పందన, ధైర్యం, అసహనం.',
    'వృషభ రాశిలో చంద్రుడు (ఉచ్ఛ): మానసిక స్థిరత్వం, సంతృప్తి, సుఖాలపై ప్రీతి.',
    'మిథున రాశిలో చంద్రుడు: చురుకైన మనసు; వైవిధ్యం, సంభాషణ అవసరం.',
    'కర్కాటక రాశిలో చంద్రుడు (స్వక్షేత్రం): అమితమైన ఆదరణ, గృహం మరియు తల్లిపై అనుబంధం.',
    'సింహ రాశిలో చంద్రుడు: ఆత్మగౌరవం, ఆప్యాయత; ప్రశంస కోరుకుంటారు.',
    'కన్య రాశిలో చంద్రుడు: ఆచరణాత్మకత, విమర్శనాత్మకత; క్రమం, సేవలో ప్రశాంతత.',
    'తులా రాశిలో చంద్రుడు: సామరస్యం, సాహచర్యం కోరుకుంటారు; గొడవలు ఇష్టపడరు.',
    'వృశ్చిక రాశిలో చంద్రుడు (నీచ): తీవ్రమైన భావాలు, ఆందోళనకు గురయ్యే అవకాశం; కోలుకునే శక్తి బలంగా ఉంటుంది.',
    'ధనుస్సు రాశిలో చంద్రుడు: ఆశావాదం, దైవభక్తి, స్వేచ్ఛాప్రియత్వం.',
    'మకర రాశిలో చంద్రుడు: మితభాషిత్వం, కర్తవ్యనిష్ఠ, భావాల్లో జాగ్రత్త.',
    'కుంభ రాశిలో చంద్రుడు: నిర్లిప్తత, ఆదర్శవాదం, అందరితో స్నేహం.',
    'మీన రాశిలో చంద్రుడు: సున్నితత్వం, అంతర్దృష్టి, భక్తి.',
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
}, 'telugu': {
    'sun': 'సూర్య దశలో అధికారం, ప్రభుత్వం, తండ్రి, ఆత్మవిశ్వాసానికి సంబంధించిన విషయాలు ప్రాధాన్యం పొందుతాయి. గుండె/కళ్ళ ఆరోగ్యంపై శ్రద్ధ అవసరం.',
    'moon': 'చంద్ర దశలో మనసు, తల్లి, గృహం, ప్రజా సంబంధాలు, ప్రయాణాలు ప్రధానం. చంద్రుని బలాన్ని బట్టి మానసిక హెచ్చుతగ్గులు ఉంటాయి.',
    'mars': 'కుజ దశ శక్తి, భూమి/ఆస్తి వ్యవహారాలు, పోటీ, సోదరులు, సాంకేతిక పనులను ఇస్తుంది. తొందరపాటు, వివాదాలు నివారించాలి.',
    'mercury': 'బుధ దశ విద్య, వ్యాపారం, రచన, సంభాషణ, విశ్లేషణాత్మక పనులకు అనుకూలం.',
    'jupiter': 'గురు దశ అభివృద్ధి, సంతానం, గురువులు, ధనం, ధర్మం, మంచి సలహాలకు తోడ్పడుతుంది.',
    'venus': 'శుక్ర దశ వివాహం, సుఖాలు, వాహనాలు, కళలు, విలాసాలను ఇస్తుంది. సంబంధాలు కేంద్రంగా ఉంటాయి.',
    'saturn': 'శని దశ క్రమశిక్షణ, కష్టపడి పనిచేయడానికి ఫలితం ఇస్తుంది; ఆలస్యాలు, బాధ్యతలు, ఓర్పు పాఠాలు.',
    'rahu': 'రాహు దశ ఆకస్మిక మార్పులు, ఆశయం, విదేశీ సంబంధాలు, అసాధారణ మార్గాలను తెస్తుంది; లక్ష్యంపై స్పష్టత ముఖ్యం.',
    'ketu': 'కేతు దశ మనసును అంతర్ముఖం చేస్తుంది: వైరాగ్యం, ఆధ్యాత్మికత, పరిశోధన; భౌతిక విషయాలు అస్థిరంగా అనిపించవచ్చు.',
}}

HOUSE_LORD_TEMPLATE = {'english': 'Lord of house {h} ({h_theme}) is placed in house {p} ({p_theme}). '
                                  'Matters of {h_theme_short} get linked to {p_theme_short}.',
                       'telugu': '{h}వ భావాధిపతి ({h_theme}) {p}వ భావంలో ({p_theme}) ఉన్నాడు. '
                                 '{h_theme_short} విషయాలు {p_theme_short}తో ముడిపడతాయి.'}

DIGNITY_NOTE = {'english': {
    'exalted': '{planet} is exalted — its significations flourish.',
    'debilitated': '{planet} is debilitated — its significations need effort and remedies.',
    'own': '{planet} is in its own sign — stable, self-reliant results.',
    'moolatrikona': '{planet} is in moolatrikona — strong and dependable.',
}, 'telugu': {
    'exalted': '{planet} ఉచ్ఛలో ఉన్నాడు — కారకత్వాలు వర్ధిల్లుతాయి.',
    'debilitated': '{planet} నీచలో ఉన్నాడు — కారకత్వాలకు ప్రయత్నం, పరిహారాలు అవసరం.',
    'own': '{planet} స్వక్షేత్రంలో ఉన్నాడు — స్థిరమైన, స్వయంసమృద్ధ ఫలితాలు.',
    'moolatrikona': '{planet} మూలత్రికోణంలో ఉన్నాడు — బలమైన, నమ్మదగిన ఫలితాలు.',
}}

RUNNING_MAHADASHA = {'english': 'Running {lord} Mahadasha ({start} – {end}). ',
                     'telugu': 'ప్రస్తుతం {lord} మహాదశ ({start} – {end}). '}
RUNNING_ANTARDASHA = {'english': 'Antardasha of {lord} until {end}: ',
                      'telugu': '{end} వరకు {lord} అంతర్దశ: '}
