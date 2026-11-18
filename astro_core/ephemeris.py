"""Ephemeris helpers — copied verbatim from ephemeris_web_02/app.py.
Source of truth: ephemeris_web_02. Same Lahiri ayanamsa, true (FLG_TRUEPOS) positions,
TRUE_NODE for Rahu/Ketu, so numbers match the Panchangam app exactly."""
import os
import datetime
from datetime import timezone
from functools import lru_cache
import swisseph as swe
try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from .constants_copied import *  # noqa

TITHI_SPAN, NAKSHATRA_SPAN, YOGA_SPAN, PADA_SPAN = 12.0, 360.0 / 27.0, 360.0 / 27.0, (360.0 / 27.0) / 4.0


def initialize_swisseph():
    """Copied from ephemeris_web_02.initialize_swisseph (path is the app root /ephe)."""
    ephe_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ephe')
    swe.set_ephe_path(ephe_path)
    return ephe_path


EPHE_PATH = initialize_swisseph()

# pyswisseph keeps the ephemeris path PER THREAD. Web servers run each request on a worker thread,
# where the path set at import time is missing and Swiss Ephemeris silently falls back to the less
# precise Moshier model (~1 arc-second Moon error). Every public entry point calls ensure_ephe().
import threading as _threading
_tls = _threading.local()


def ensure_ephe():
    if not getattr(_tls, 'ready', False):
        swe.set_ephe_path(EPHE_PATH)
        _tls.ready = True

# --- Core Calculation Functions ---
@lru_cache(maxsize=32)
def get_ayanamsa(julian_day):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_value = swe.get_ayanamsa_ut(julian_day)

    # print(f"--- AYANAMSA LOG --- JD: {julian_day}, Ayanamsa (Lahiri): {ayanamsa_value} ---")

    return ayanamsa_value


@lru_cache(maxsize=4096)
def get_sideral_position(jd, p_id, is_ketu=False, apply_sphuta=False):
    ayanamsa = get_ayanamsa(jd)

    planet_name = PLANET_ID_TO_NAME_MAP.get(p_id, f"Unknown ID {p_id}")
    if p_id == swe.TRUE_NODE:
        planet_name = 'Ketu' if is_ketu else 'Rahu'

    # print(f"--- AYANAMSA LOG --- Planet: {planet_name:<10} | JD: {jd} | Ayanamsa (Lahiri): {ayanamsa} ---")
    true_flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_TRUEPOS
    true_pos_data, _ = swe.calc_ut(jd, p_id, true_flags)
    true_sidereal_pos = (true_pos_data[0] - ayanamsa + 360) % 360
    apparent_flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    apparent_pos_data, _ = swe.calc_ut(jd, p_id, apparent_flags)
    apparent_sidereal_pos = (apparent_pos_data[0] - ayanamsa + 360) % 360
    if p_id == swe.TRUE_NODE: apparent_sidereal_pos = true_sidereal_pos
    if apply_sphuta:
        final_pos_data, final_sidereal_pos = apparent_pos_data, apparent_sidereal_pos
    else:
        final_pos_data, final_sidereal_pos = true_pos_data, true_sidereal_pos
    if is_ketu:
        true_sidereal_pos = (true_sidereal_pos + 180) % 360
        apparent_sidereal_pos = (apparent_sidereal_pos + 180) % 360
        final_sidereal_pos = (final_sidereal_pos + 180) % 360
    return final_sidereal_pos, final_pos_data[3], true_sidereal_pos, apparent_sidereal_pos


def jd_to_datetime_utc(jd):
    """Converts Julian Day to an *aware* UTC datetime object."""
    if jd is None or jd < 1721425.5: return None
    return datetime.datetime.fromtimestamp((jd - 2440587.5) * 86400.0, timezone.utc)


def get_timezone_abbreviation(iana_tz_str, jd_utc):
    """Get timezone abbreviation (IST, EST, GMT, etc.) for display."""
    if not iana_tz_str:
        return "UTC"

    try:
        dt_utc = jd_to_datetime_utc(jd_utc)
        if dt_utc is None:
            return "UTC"

        target_tz = ZoneInfo(iana_tz_str)
        local_dt = dt_utc.astimezone(target_tz)
        tz_abbr = local_dt.tzname()

        return tz_abbr if tz_abbr else "UTC"
    except (ZoneInfoNotFoundError, Exception) as e:
        print(f"Warning: Could not get timezone abbreviation for '{iana_tz_str}': {e}")
        return "UTC"


def format_timerange(start_jd, end_jd, iana_tz):
    """
    Returns a dict with formatted times for HTML (with <br>) and Excel.
    Displays start and end times on separate lines.
    """
    if not start_jd or not end_jd:
        return {'start': 'N/A', 'end': 'N/A', 'formatted': 'N/A', 'formatted_excel': 'N/A'}

    s_time = format_time_local(start_jd, iana_tz, True)
    e_time = format_time_local(end_jd, iana_tz, True)

    return {
        'start': s_time,
        'end': e_time,
        # For HTML: Show on separate lines with <br>
        'formatted': f"{s_time}<br>{e_time}",
        # For Excel: Show on separate lines with newline
        'formatted_excel': f"{s_time}\n{e_time}",
        'start_jd': start_jd,
        'end_jd': end_jd
    }


def format_time_local(jd, iana_tz_str=None, show_date=True, show_seconds=False):
    """Formats Julian Day (UTC) to local time string WITHOUT timezone suffix."""
    dt_utc = jd_to_datetime_utc(jd)
    if dt_utc is None: return ""

    target_tz = timezone.utc

    if iana_tz_str:
        try:
            target_tz = ZoneInfo(iana_tz_str)
        except ZoneInfoNotFoundError:
            print(f"Warning: Timezone '{iana_tz_str}' not found. Falling back to UTC.")

    local_dt = dt_utc.astimezone(target_tz)

    time_format = "%I:%M:%S %p" if show_seconds else "%I:%M %p"
    date_format = "%d-%m-%Y " if show_date else ""
    formatted_time = local_dt.strftime(f"{date_format}{time_format}").strip()

    return formatted_time


def decimal_to_dms_string(dec_deg):
    dec_deg %= 30
    degrees, minutes, seconds = int(dec_deg), int((dec_deg * 60) % 60), int((dec_deg * 3600) % 60)
    return f"{degrees}° {minutes}' {seconds}\""




def get_rise_set(year, month, day, latitude, longitude, body=swe.SUN, iana_tz_str=None):
    """Calculates rise/set times as Julian Day (UTC)."""
    jd_start_local_midnight = swe.julday(year, month, day, 0.0)

    if iana_tz_str:
        try:
            tz = ZoneInfo(iana_tz_str)
            naive_dt = datetime.datetime(year, month, day)
            local_dt = naive_dt.replace(tzinfo=tz)
            offset_hours = local_dt.utcoffset().total_seconds() / 3600
            jd_start_local_midnight -= offset_hours / 24.0
        except ZoneInfoNotFoundError:
            pass

    try:
        body_int = int(body)
        geopos = [longitude, latitude, 0.0]

        rise_result = swe.rise_trans(
            jd_start_local_midnight,
            body_int,
            swe.CALC_RISE | swe.BIT_DISC_CENTER,
            geopos
        )
        rise_jd_utc = rise_result[1][0] if rise_result[0] == 0 else None

        set_result = swe.rise_trans(
            jd_start_local_midnight,
            body_int,
            swe.CALC_SET | swe.BIT_DISC_CENTER,
            geopos
        )
        set_jd_utc = set_result[1][0] if set_result[0] == 0 else None

        return rise_jd_utc, set_jd_utc
    except Exception as e:
        print(f"Error in get_rise_set for body {body}: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def get_elongation(jd):
    sun_pos, _, _, _ = get_sideral_position(jd, swe.SUN, is_ketu=False, apply_sphuta=False)
    moon_pos, _, _, _ = get_sideral_position(jd, swe.MOON, is_ketu=False, apply_sphuta=False)
    return (moon_pos - sun_pos + 360) % 360


def find_elongation_boundary_jd(target_elongation, start_jd_approx):
    low, high = start_jd_approx - 16.0, start_jd_approx + 16.0

    # Handle wrap for 0/360
    if target_elongation == 0.0 or target_elongation == 360.0:
        for _ in range(40):
            mid = (low + high) / 2
            elong = get_elongation(mid)
            if elong < 180:  # e.g., 5 degrees
                diff = elong
            else:  # e.g., 355 degrees
                diff = elong - 360.0

            if diff < 0:
                low = mid
            else:
                high = mid
    else:
        for _ in range(40):
            mid = (low + high) / 2
            diff = (get_elongation(mid) - target_elongation + 180) % 360 - 180
            if diff < 0:
                low = mid
            else:
                high = mid

    return (low + high) / 2


# --- FIX 5: Helper function for Tithi names with Paksha ---


# --- FIX 5: Helper function for Tithi names with Paksha ---
def _get_tithi_name_with_paksha(tithi_idx):
    """Returns tithi names prefixed with Shukla/Krishna (Suddha/Bahula)."""
    if not 1 <= tithi_idx <= 30:
        return {'name_telugu': 'Error', 'name_english': 'Error'}

    if 1 <= tithi_idx <= 15:
        paksha_en, paksha_te = 'Shukla', 'శుద్ధ'
    else:
        paksha_en, paksha_te = 'Krishna', 'బహుళ'

    name_en = TITHI_NAMES['english'][tithi_idx]
    name_te = TITHI_NAMES['telugu'][tithi_idx]

    return {
        'name_telugu': f"{paksha_te} {name_te}",
        'name_english': f"{paksha_en} {name_en}"
    }




# --- NEW HELPER FUNCTION (Add this before get_all_karanas_for_day) ---
def get_karana_num(k_index):
    """
    Calculates the Karana number (1-11) from the Karana index (1-60).
    Accounts for the 4 Sthira (fixed) Karanas.
    """
    if k_index == 1:
        return 11  # 1. Kimstughna (1st half of Shukla 1)
    elif k_index == 58:
        return 8  # 2. Shakuni (2nd half of Bahula 14)
    elif k_index == 59:
        return 9  # 3. Chatushpada (1st half of Amavasya)
    elif k_index == 60:
        return 10  # 4. Naga (2nd half of Amavasya)
    else:
        # Chara (movable) karanas (indices 2 through 57)
        # These repeat the 7 karanas (Bava[1] to Vishti[7])
        return ((k_index - 2) % 7) + 1



def get_ascendant_longitude(jd, lat, lon):
    try:
        _, ascmc = swe.houses(jd, lat, lon, b'P')
        return (ascmc[0] - get_ayanamsa(jd) + 360) % 360
    except swe.Error as e:
        print(f"Sweph error calculating houses (ascendant): {e}")
        return None

