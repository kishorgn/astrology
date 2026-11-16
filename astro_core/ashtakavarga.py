"""Bhinnashtakavarga (BAV) for the 7 planets and Sarvashtakavarga (SAV)."""
from .jyotish import ASHTAKAVARGA, SEVEN


def ashtakavarga(chart):
    signs = {g['key']: g['sign']['index'] for g in chart['grahas']}
    signs['lagna'] = chart['lagna']['sign']['index']
    bav = {}
    for planet, refs in ASHTAKAVARGA.items():
        row = [0] * 12
        for ref, houses in refs.items():
            base = signs[ref]
            for h in houses:
                row[(base + h - 1) % 12] += 1
        bav[planet] = row
    sav = [sum(bav[p][i] for p in SEVEN) for i in range(12)]
    lagna = signs['lagna']
    return {
        'bav': bav, 'bav_totals': {p: sum(r) for p, r in bav.items()},
        'sav': sav, 'sav_total': sum(sav),
        # SAV re-ordered by house from Lagna (house 1 first) — easier to read
        'sav_by_house': [sav[(lagna + i) % 12] for i in range(12)],
    }
