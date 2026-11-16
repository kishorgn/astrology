# Jathakam (astrology)

Jathakam / Porutham / Phalitam app.

```
pip install -r requirements.txt
python app.py            # http://localhost:5050
```

## Layout
- `astro_core/` — calculation engine, **no Flask imports** (reusable by a mobile backend)
  - `ephemeris.py`, `constants_copied.py` — copied verbatim from `ephemeris_web_02/app.py`
    (Lahiri ayanamsa, true positions, sphuta rule for Ju/Sa/Ra/Ke, TRUE_NODE). Keep in sync.
  - `chart.py` — graha sthiti, lagna, Sripati bhava, 16 vargas, birth panchanga, samvatsara
  - `dasha.py` — Vimshottari MD/AD/PD
  - `ashtakavarga.py` — BAV + SAV (totals self-check: 337)
  - `matching.py` — Ashtakoota 36 + Rajju/Vedha + Kuja dosha
  - `yogas.py`, `gochara.py`, `predictions.py`
  - `predictions_text.py` — **draft** prediction text; content for the client to replace/translate
- `app.py` — JSON API: `/api/horoscope`, `/api/match`, `/api/meta`, `/api/countries`, `/api/cities/<cc>`, `/api/timezone`, `/api/health`
- `ephe/` — Swiss Ephemeris files (sepl_18, semo_18, seas_18: years 1800–2399)

## Needs astrologer sign-off
Vashya/Gana/Yoni scoring tables, Rahu/Ketu exaltation signs, combustion orbs,
dasha year length (365.2425 vs 365.25), and all prediction text.
