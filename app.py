# app.py - Jathakam / Porutham / Phalitam
# Thin Flask layer. All calculations live in astro_core/ (no Flask imports there),
# so a mobile app can call the same JSON endpoints.
import json
import os
import unicodedata

from flask import Flask, jsonify, render_template, request
from timezonefinder import TimezoneFinder

from astro_core import full_horoscope, build_chart, vimshottari, now_jd
from astro_core.marriage import full_match
from astro_core.ephemeris import (EPHE_PATH, RASHI_NAMES, PLANET_NAMES, NAKSHATRA_NAMES, VARAM_NAMES)
from astro_core.jyotish import PLANET_ABBR, VARGAS, HOUSE_THEMES, UI_LABELS
from config import BRAND_NAME, DEVELOPER_CREDIT

app = Flask(__name__)
SUBPATH = os.environ.get('FLASK_SUBPATH', '')
tf = TimezoneFinder()

def _alpha_key(name):
    """Alphabetical sort key that ignores case and accents (Ísafjörður sorts with I)."""
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().casefold()


with open(os.path.join(os.path.dirname(__file__), 'locations.json'), encoding='utf-8') as f:
    location_data = json.load(f)
# Always serve countries and cities alphabetically, whatever order they are in the file,
# so new entries can be appended anywhere in locations.json (restart the app after editing it).
location_data['countries'].sort(key=lambda c: _alpha_key(c['name']))
for _c in location_data['countries']:
    _c.get('cities', []).sort(key=lambda x: _alpha_key(x['name']))


@app.context_processor
def inject_globals():
    return {'brand_name': BRAND_NAME, 'developer_credit': DEVELOPER_CREDIT, 'subpath': SUBPATH}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/meta')
def meta():
    """Static labels the client needs to draw charts (names in both languages)."""
    return jsonify({'rashi': RASHI_NAMES, 'planets': PLANET_NAMES, 'abbr': PLANET_ABBR,
                    'nakshatra': NAKSHATRA_NAMES, 'vara': VARAM_NAMES, 'house_themes': HOUSE_THEMES,
                    'labels': UI_LABELS,
                    'vargas': [{'code': v[0], 'name_english': v[2], 'name_telugu': v[3],
                                'purpose_english': v[4], 'purpose_telugu': v[5]} for v in VARGAS]})


# --- locations (copied from ephemeris_web_02, without the Lite-mode India filter) ---
@app.route('/api/countries')
def get_countries_api():
    return jsonify([{'name': c['name'], 'code': c['code']} for c in location_data.get('countries', [])])


@app.route('/api/cities/<country_code>')
def get_cities_api(country_code):
    for country in location_data.get('countries', []):
        if country['code'].lower() == country_code.lower():
            return jsonify(country.get('cities', []))
    return jsonify([])


@app.route('/api/timezone')
def timezone_for():
    lat, lon = float(request.args['lat']), float(request.args['lon'])
    return jsonify({'iana_tz': tf.timezone_at(lat=lat, lng=lon) or 'UTC'})


def _birth(d):
    lat, lon = float(d['lat']), float(d['lon'])
    tz = d.get('iana_tz') or tf.timezone_at(lat=lat, lng=lon) or 'UTC'
    return dict(name=d.get('name', ''), date=d['date'], time=d['time'], lat=lat, lon=lon,
                iana_tz=tz, place=d.get('place', ''))


def _err(e, code=400):
    return jsonify({'error': str(e)}), code


@app.route('/api/horoscope', methods=['POST'])
def horoscope():
    d = request.get_json(force=True)
    try:
        b = _birth(d)
        return jsonify(full_horoscope(b['name'], b['date'], b['time'], b['lat'], b['lon'], b['iana_tz'],
                                      b['place'], d.get('lang', 'english')))
    except (KeyError, ValueError) as e:
        return _err(e)


@app.route('/api/match', methods=['POST'])
def matchmaking():
    d = request.get_json(force=True)
    try:
        boy, girl = _birth(d['boy']), _birth(d['girl'])
        bc = build_chart(boy['name'], boy['date'], boy['time'], boy['lat'], boy['lon'], boy['iana_tz'], boy['place'])
        gc = build_chart(girl['name'], girl['date'], girl['time'], girl['lat'], girl['lon'], girl['iana_tz'],
                         girl['place'])
        slim = lambda c: {'name': c['name'], 'lagna': c['lagna'], 'grahas': c['grahas'],
                          'vargas': {'D1': c['vargas']['D1'], 'D9': c['vargas']['D9']},
                          'panchanga': c['panchanga']}
        nj = now_jd()
        moon = lambda c: next(x['longitude'] for x in c['grahas'] if x['key'] == 'moon')
        bd = vimshottari(moon(bc), bc['birth']['jd_ut'], boy['iana_tz'], now_jd=nj, levels=2)
        gd = vimshottari(moon(gc), gc['birth']['jd_ut'], girl['iana_tz'], now_jd=nj, levels=2)
        return jsonify({'result': full_match(bc, gc, bd, gd, nj), 'boy': slim(bc), 'girl': slim(gc)})
    except (KeyError, ValueError) as e:
        return _err(e)


@app.route('/api/health')
def health():
    files = sorted(f for f in os.listdir(EPHE_PATH) if f.endswith('.se1')) if os.path.isdir(EPHE_PATH) else []
    return jsonify({'ok': True, 'ephe_path': EPHE_PATH, 'ephe_files': files,
                    'warning': None if files else 'No .se1 files: Swiss Ephemeris is silently falling back to Moshier'})


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5050)))
