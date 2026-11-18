/* Jathakam front-end. Display only — every number comes from /api. */
(function () {
  const API = (window.SUBPATH || '') + '/api';
  const S = { lang: 'telugu', meta: null, horo: null, varga: 'D9', countries: [] };
  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const T = (en, te) => (S.lang === 'telugu' ? te : en);
  const nm = (o) => (o ? (S.lang === 'telugu' ? o.name_telugu : o.name_english) : '');
  const pn = (k) => S.meta.planets[k] ? S.meta.planets[k][S.lang] : (k === 'lagna' ? T('Lagna', 'లగ్నం') : k);
  const ab = (k) => S.meta.abbr[S.lang][k];
  const rasi = (i) => S.meta.rashi[S.lang][i];

  // ------------------------------------------------------------ boot
  async function boot() {
    S.meta = await (await fetch(API + '/meta')).json();
    S.countries = await (await fetch(API + '/countries')).json();
    for (const id of ['birthForm', 'boyForm', 'girlForm']) await setupForm($('#' + id), id === 'birthForm');
    $$('.lang button').forEach(b => b.onclick = () => setLang(b.dataset.lang));
    $$('#tabs button').forEach(b => b.onclick = () => showTab(b.dataset.tab));
    $('#matchBtn').onclick = runMatch;
    setLang('telugu');
  }

  async function setupForm(form, withSubmit) {
    form.appendChild($('#birthFields').content.cloneNode(true));
    if (withSubmit) {
      const b = document.createElement('button');
      b.className = 'primary'; b.type = 'submit'; b.dataset.te = 'జాతకం తయారు చేయి'; b.dataset.en = 'Generate';
      form.appendChild(b);
      form.onsubmit = (e) => { e.preventDefault(); runHoroscope(); };
    }
    const cSel = form.elements.country, citySel = form.elements.city;
    cSel.innerHTML = S.countries.map(c => `<option value="${c.code}">${c.name}</option>`).join('');
    cSel.value = S.countries.some(c => c.code === 'IN') ? 'IN' : S.countries[0].code;
    cSel.onchange = () => loadCities(form);
    await loadCities(form);
  }

  async function loadCities(form) {
    const cities = await (await fetch(API + '/cities/' + form.elements.country.value)).json();
    form._cities = cities;
    form.elements.city.innerHTML = cities.map((c, i) => `<option value="${i}">${c.name}</option>`).join('');
    const hyd = cities.findIndex(c => /Hyderabad/i.test(c.name));
    if (hyd >= 0) form.elements.city.value = hyd;
  }

  function readForm(form) {
    const f = form.elements;
    const city = form._cities[f.city.value] || {};
    const manual = f.lat.value !== '' || f.lon.value !== '';
    if (manual && (f.lat.value === '' || f.lon.value === ''))
      throw new Error(T('Enter both latitude and longitude', 'అక్షాంశం, రేఖాంశం రెండూ నింపండి'));
    const lat = manual ? +f.lat.value : city.lat, lon = manual ? +f.lon.value : city.lng;
    if (manual && (Math.abs(lat) > 90 || Math.abs(lon) > 180))
      throw new Error(T('Latitude must be -90..90, longitude -180..180 (West/South negative)', 'అక్షాంశం -90..90, రేఖాంశం -180..180 మధ్య ఉండాలి'));
    if (!f.date.value || !f.time.value || lat == null) throw new Error(T('Fill date, time and place', 'తేదీ, సమయం, ప్రదేశం నింపండి'));
    // Manual coordinates: timezone comes from the box if typed, else the server looks it up from lat/lon
    return { name: f.name.value, date: f.date.value, time: f.time.value, lat, lon,
             iana_tz: f.iana_tz.value.trim() || (manual ? '' : city.iana_tz), place: manual ? `${lat}, ${lon}` : city.name };
  }

  function setLang(l) {
    S.lang = l;
    document.documentElement.lang = l === 'telugu' ? 'te' : 'en';
    $$('.lang button').forEach(b => b.classList.toggle('on', b.dataset.lang === l));
    $$('[data-te]').forEach(el => el.textContent = l === 'telugu' ? el.dataset.te : el.dataset.en);
    if (S.horo) renderAll();
    if (S.match) renderMatch();
  }

  function showTab(t) {
    $$('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === t));
    $$('.tab').forEach(s => s.classList.toggle('on', s.id === 'tab-' + t));
    $('#birthCard').hidden = t === 'match';
  }

  function msg(text, isErr) {
    const m = $('#msg'); m.hidden = !text; m.textContent = text || ''; m.classList.toggle('err', !!isErr);
  }

  async function post(path, body) {
    const r = await fetch(API + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    const j = await r.json();
    if (!r.ok) throw new Error(j.error || r.statusText);
    return j;
  }

  async function runHoroscope() {
    try {
      msg(T('Calculating…', 'లెక్కిస్తున్నాం…'));
      S.horo = await post('/horoscope', { ...readForm($('#birthForm')), lang: S.lang });
      msg('');
      renderAll();
    } catch (e) { msg(e.message, true); }
  }

  // ------------------------------------------------------------ Rasi chakram (Telugu hand-drawn layout)
  // 3x3 grid, open outer edges. Movable signs in the side boxes (Mesha top, Karkataka left,
  // Tula bottom, Makara right); each corner split diagonally into two signs; anticlockwise.
  // Pure SVG <text> placed by geometry — no foreignObject / CSS transforms, so Safari/WebKit,
  // Chrome and mobile web-views all draw it identically. viewBox is 300 x 300.
  const GEO = {
    0: { pts: [[100, 0], [200, 0], [200, 100], [100, 100]], box: [100, 15, 200, 98], l: [150, 11, 'middle'] },
    1: { pts: [[0, 0], [100, 0], [100, 100]] },
    2: { pts: [[0, 0], [100, 100], [0, 100]] },
    3: { pts: [[0, 100], [100, 100], [100, 200], [0, 200]], box: [0, 115, 100, 198], l: [4, 111, 'start'] },
    4: { pts: [[0, 200], [100, 200], [0, 300]] },
    5: { pts: [[100, 200], [100, 300], [0, 300]] },
    6: { pts: [[100, 200], [200, 200], [200, 300], [100, 300]], box: [100, 202, 200, 285], l: [150, 296, 'middle'] },
    7: { pts: [[200, 200], [200, 300], [300, 300]] },
    8: { pts: [[200, 200], [300, 200], [300, 300]] },
    9: { pts: [[200, 100], [300, 100], [300, 200], [200, 200]], box: [200, 115, 300, 198], l: [296, 111, 'end'] },
    10: { pts: [[300, 0], [300, 100], [200, 100]] },
    11: { pts: [[200, 0], [300, 0], [200, 100]] },
  };
  const LINES = 'M100,0V300 M200,0V300 M0,100H300 M0,200H300 M100,100L0,0 M200,100L300,0 M100,200L0,300 M200,200L300,300';
  const PAD = 4;           // keep text this far (horizontally) from any line
  const LBL = 8.5;         // sign-name font size

  // Text width via canvas, using the page's own font stack (works for hidden tabs too)
  const _ctx = document.createElement('canvas').getContext('2d');
  let _font = null;
  function tw(text, size, weight) {
    _font = _font || getComputedStyle(document.body).fontFamily;
    _ctx.font = `${weight} ${size}px ${_font}`;
    return _ctx.measureText(text).width * 1.06;   // 6% safety margin for renderer differences
  }
  // Real font box (ascent/descent) of the active font — Telugu glyphs hang low, so never assume.
  let _metric = null;
  function fm() {
    if (!_metric) {
      _font = _font || getComputedStyle(document.body).fontFamily;
      _ctx.font = `600 100px ${_font}`;
      const m = _ctx.measureText('అమృశ్చMgy');
      const asc = m.fontBoundingBoxAscent || m.actualBoundingBoxAscent || 90;
      const desc = m.fontBoundingBoxDescent || m.actualBoundingBoxDescent || 45;
      _metric = { asc: asc / 100, desc: Math.max(desc, m.actualBoundingBoxDescent || 0) / 100 };
    }
    return _metric;
  }
  const lineH = (fs) => (fm().asc + fm().desc) * fs + 0.6;     // row height that holds the whole glyph box
  const baseIn = (ya, fs) => ya + 0.3 + fm().asc * fs;         // baseline that keeps the glyph box inside the row
  const esc = (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;');

  // Horizontal extent of a convex polygon at height y
  function spanAt(pts, y) {
    const xs = [];
    for (let i = 0; i < pts.length; i++) {
      const [x1, y1] = pts[i], [x2, y2] = pts[(i + 1) % pts.length];
      if (y < Math.min(y1, y2) - 1e-9 || y > Math.max(y1, y2) + 1e-9) continue;
      if (y1 === y2) xs.push(x1, x2); else xs.push(x1 + (y - y1) * (x2 - x1) / (y2 - y1));
    }
    return xs.length ? [Math.min(...xs), Math.max(...xs)] : null;
  }
  // Usable [left, right] for a row occupying ya..yb (intersection of both edges, minus padding)
  function bandSpan(pts, ya, yb) {
    const a = spanAt(pts, ya), b = spanAt(pts, yb);
    if (!a || !b) return null;
    const l = Math.max(a[0], b[0]) + PAD, r = Math.min(a[1], b[1]) - PAD;
    return r > l ? [l, r] : null;
  }

  // Greedy row fill. rowAt(r, h) -> [ya, yb, left, right] or null. Returns null if the items do not fit.
  function fillRows(items, fs, rowAt) {
    const gap = fs * 0.45, h = lineH(fs), rows = [];
    let i = 0, r = 0;
    while (i < items.length) {
      const band = rowAt(r, h);
      if (!band) return null;
      const [ya, yb, l, rt] = band, row = { ya, yb, l, r: rt, items: [], w: 0 };
      while (i < items.length) {
        const w = items[i].w(fs), need = row.items.length ? row.w + gap + w : w;
        if (need > rt - l) break;
        row.items.push({ ...items[i], width: w }); row.w = need; i++;
      }
      if (!row.items.length) return null;     // even one item does not fit this row
      rows.push(row); r++;
    }
    return { rows, gap, fs };
  }

  function triangleFrame(pts) {
    // the horizontal edge is the wide side; rows stack from it toward the apex
    const ys = pts.map(p => p[1]);
    const legY = ys.find((y, i) => ys.indexOf(y) !== i);
    const apexY = ys.find(y => y !== legY), dir = Math.sign(apexY - legY);
    const lblH = lineH(LBL);
    const lblBand = dir > 0 ? [legY + 1, legY + 1 + lblH] : [legY - 1 - lblH, legY - 1];
    return { legY, dir, start: legY + dir * (1 + lblH), lblBand };
  }

  function layoutTriangle(pts, items, sizes) {
    const f = triangleFrame(pts);
    for (const fs of sizes) {
      const res = fillRows(items, fs, (r, h) => {
        const y0 = f.start + f.dir * r * h, ya = Math.min(y0, y0 + f.dir * h), yb = Math.max(y0, y0 + f.dir * h);
        const sp = bandSpan(pts, ya, yb);
        return sp ? [ya, yb, sp[0], sp[1]] : null;
      });
      if (res) return res;
    }
    return null;
  }

  function layoutRect(box, items, sizes) {
    const [x0, y0, x1, y1] = box;
    for (const fs of sizes) {
      const h = lineH(fs), maxRows = Math.floor((y1 - y0) / h);
      const res = fillRows(items, fs, (r) => r < maxRows ? [0, 0, x0 + PAD, x1 - PAD] : null);
      if (res) {   // centre the block vertically
        const top = (y0 + y1) / 2 - res.rows.length * h / 2;
        res.rows.forEach((row, k) => { row.ya = top + k * h; row.yb = row.ya + h; });
        return res;
      }
    }
    return null;
  }

  function drawRows(res, s) {
    let out = '';
    for (const row of res.rows) {
      let x = (row.l + row.r) / 2 - row.w / 2;
      const base = baseIn(row.ya, res.fs), mid = base - (fm().asc - fm().desc) * res.fs / 2;
      for (const it of row.items) {
        if (it.lagna) {
          out += `<ellipse class="lge" cx="${(x + it.width / 2).toFixed(1)}" cy="${mid.toFixed(1)}" rx="${(it.width / 2).toFixed(1)}" ry="${((row.yb - row.ya) / 2 - 0.2).toFixed(1)}"/>`;
          out += `<text class="lgt" data-sign="${s}" data-k="lagna" x="${(x + it.width / 2).toFixed(1)}" y="${base.toFixed(1)}" text-anchor="middle" font-size="${res.fs}">${esc(it.text)}</text>`;
        } else {
          out += `<text class="${it.cls}" data-sign="${s}" data-k="${it.key}" x="${(x + it.width / 2).toFixed(1)}" y="${base.toFixed(1)}" text-anchor="middle" font-size="${res.fs}">${esc(it.text)}</text>`;
        }
        x += it.width + res.gap;
      }
    }
    return out;
  }

  // opts.nums: array of 12 numbers to show instead of planets (Ashtakavarga)
  function southChart(boxes, lagnaSign, title, sub, flagsFrom, opts = {}) {
    const flags = {};
    const src = flagsFrom === undefined ? (S.horo ? S.horo.chart.grahas : []) : flagsFrom;
    src.forEach(g => flags[g.key] = (g.retrograde && !['rahu', 'ketu'].includes(g.key) ? '(' + S.meta.labels[S.lang].retro + ')' : '') + (g.combust ? '*' : ''));
    let fills = '', body = '';
    for (let s = 0; s < 12; s++) {
      const g = GEO[s], tri = !g.box;
      fills += `<polygon points="${g.pts.map(p => p.join(',')).join(' ')}" class="${s === lagnaSign ? 'lagna' : ''}"/>`;
      let items;
      if (opts.nums) {
        const v = String(opts.nums[s]);
        items = [{ key: 'num', text: v, cls: 'numt ' + (+v >= 28 ? 'good' : 'weak'), w: fs => tw(v, fs, 700) }];
      } else {
        items = (boxes[s] || []).map(k => k === 'lagna'
          ? { key: k, text: ab(k), lagna: true, w: fs => tw(ab(k), fs, 700) + fs * 0.9 }
          : { key: k, text: ab(k) + (flags[k] || ''), cls: 'pt', w: fs => tw(ab(k) + (flags[k] || ''), fs, 600) });
      }
      const sizes = opts.nums ? (tri ? [20, 17, 14, 12] : [26, 22, 18])
        : (tri ? [12, 11, 10, 9, 8, 7, 6, 5] : [13, 12, 11, 10, 9, 8, 7, 6]);
      const res = items.length ? (tri ? layoutTriangle(g.pts, items, sizes) : layoutRect(g.box, items, sizes)) : null;
      if (tri) {
        const lb = triangleFrame(g.pts).lblBand;
        const sp = bandSpan(g.pts, lb[0], lb[1]) || spanAt(g.pts, (lb[0] + lb[1]) / 2);
        body += `<text class="sn" data-sign="${s}" x="${((sp[0] + sp[1]) / 2).toFixed(1)}" y="${baseIn(lb[0], LBL).toFixed(1)}" text-anchor="middle" font-size="${LBL}">${esc(rasi(s))}</text>`;
      } else {
        body += `<text class="sn" data-sign="${s}" x="${g.l[0]}" y="${g.l[1]}" text-anchor="${g.l[2]}" font-size="${LBL}">${esc(rasi(s))}</text>`;
      }
      if (res) body += drawRows(res, s);
      else if (items.length) console.error('Chart: could not fit sign', s, items.map(i => i.text));
    }
    // centre: title + sub lines, each shrunk to fit
    const lines = [{ t: title, fs: 13, w: 700, cls: 'tit' }].concat(
      String(sub || '').split('<br>').map(x => x.trim()).filter(Boolean).map(t => ({ t, fs: 7.5, w: 400, cls: 'sub' })));
    lines.forEach(L => { while (L.fs > 4 && tw(L.t, L.fs, L.w) > 90) L.fs -= 0.5; });
    const totalH = lines.reduce((acc, L) => acc + lineH(L.fs), 0);
    let y = 150 - totalH / 2, centre = '';
    lines.forEach(L => { centre += `<text class="${L.cls}" x="150" y="${baseIn(y, L.fs).toFixed(1)}" text-anchor="middle" font-size="${L.fs}">${esc(L.t)}</text>`; y += lineH(L.fs); });
    return `<svg class="rchart" viewBox="-4 -4 308 308" role="img" aria-label="${esc(title)}">
      <g class="fills">${fills}</g><path d="${LINES}" class="lines"/>${body}${centre}</svg>`;
  }

  // ------------------------------------------------------------ renderers
  function renderAll() {
    renderJathakam(); renderGrahas(); renderVargas(); renderDasha(); renderAshtaka(); renderPhalitam(); renderParihara(); renderGochara();
  }

  function renderJathakam() {
    const c = S.horo.chart, p = c.panchanga, v = c.vargas;
    const kd = S.horo.kuja_dosha;
    const sub = `${c.name || ''}<br>${c.birth.date} ${c.birth.time}<br>${c.birth.place || ''}`;
    const rows = [
      [T('Lagna', 'లగ్నం'), `${nm(c.lagna.sign)} ${c.lagna.degree_in_sign}`],
      [T('Rasi (Moon)', 'జన్మ రాశి'), nm(c.grahas[1].sign)],
      [T('Nakshatra', 'జన్మ నక్షత్రం'), `${nm(p.nakshatra)} – ${T('Pada', 'పాదం')} ${p.nakshatra.pada}`],
      [T('Tithi', 'తిథి'), nm(p.tithi)], [T('Vara', 'వారం'), nm(p.vara)], [T('Yoga', 'యోగం'), nm(p.yoga)],
      [T('Karana', 'కరణం'), nm(p.karana)], [T('Samvatsara', 'సంవత్సరం'), nm(p.samvatsara)],
      [T('Sunrise / Sunset', 'సూర్యోదయం / అస్తమయం'), `${p.sunrise} / ${p.sunset}`],
      [T('Ishta kaala', 'ఇష్ట కాలం'), p.ishta_kaala_ghatis || '-'],
      [T('Ayanamsa (Lahiri)', 'అయనాంశ (లాహిరి)'), c.ayanamsa.dms],
      [T('Dasha balance at birth', 'జనన కాల దశా శేషం'), `${pn(S.horo.dasha.birth_lord)} ${S.horo.dasha.balance.years}${T('y', 'సం')} ${S.horo.dasha.balance.months}${T('m', 'నె')} ${S.horo.dasha.balance.days}${T('d', 'రో')}`],
      [T('Kuja dosha', 'కుజ దోషం'), { present: T('Present', 'ఉంది'), cancelled: T('Cancelled (exception applies)', 'దోష భంగం'), none: T('Not present', 'లేదు') }[kd.status]],
    ];
    $('#tab-jathakam').innerHTML = `
      <div class="charts">
        ${southChart(v.D1.boxes, v.D1.lagna_sign, T('Rasi', 'రాశి చక్రం'), sub)}
        ${southChart(v.D9.boxes, v.D9.lagna_sign, T('Navamsa', 'నవాంశ చక్రం'), '')}
      </div>
      <div class="card"><table class="kv">${rows.map(r => `<tr><th>${r[0]}</th><td>${r[1]}</td></tr>`).join('')}</table>
      <p class="note">(${S.meta.labels[S.lang].retro}) = ${T('retrograde', 'వక్రం')}, * = ${T('combust', 'అస్తంగతం')}</p></div>`;
  }

  function renderGrahas() {
    const c = S.horo.chart, L = S.meta.labels[S.lang];
    const head = [T('Planet', 'గ్రహం'), T('Rasi', 'రాశి'), T('Degree', 'అంశ'), T('Nakshatra', 'నక్షత్రం'), T('Pada', 'పాదం'),
      T('Star lord', 'నక్షత్రాధిపతి'), T('House', 'స్థానం'), T('Bhava', 'భావం'), T('Navamsa', 'నవాంశ'), T('Status', 'స్థితి')];
    const row = (g, isL) => `<tr><td><b>${isL ? T('Lagna', 'లగ్నం') : nm(g)}</b></td><td>${nm(g.sign)}</td><td>${g.degree_in_sign}</td>
      <td>${nm(g.nakshatra)}</td><td>${g.nakshatra.pada}</td><td>${pn(g.nakshatra.lord)}</td>
      <td>${isL ? 1 : g.house_whole_sign}</td><td>${isL ? 1 : g.bhava}</td><td>${rasi(g.navamsa_sign)}</td>
      <td>${isL ? '' : [g.retrograde ? T('Retro', 'వక్రం') : '', g.combust ? T('Combust', 'అస్తంగతం') : '', g.dignity ? L[g.dignity] || '' : ''].filter(Boolean).join(', ')}</td></tr>`;
    const bh = c.bhavas.map(b => `<tr><td>${b.house}</td><td>${b.madhya_dms}</td><td>${b.planets.map(pn).join(', ')}</td></tr>`).join('');
    const boxes = {}; for (let i = 0; i < 12; i++) boxes[i] = [];
    const lag = c.lagna.sign.index;
    c.grahas.forEach(g => boxes[(lag + g.bhava - 1) % 12].push(g.key)); boxes[lag].unshift('lagna');
    $('#tab-grahas').innerHTML = `
      <div class="card scroll"><h3>${T('Graha Sthiti', 'గ్రహ స్థితి')}</h3><table class="grid"><tr>${head.map(h => `<th>${h}</th>`).join('')}</tr>
      ${row(c.lagna, true)}${c.grahas.map(g => row(g)).join('')}</table></div>
      <div class="charts">${southChart(boxes, lag, T('Bhava (Sripati)', 'భావ చక్రం'), T('planets by bhava', 'భావ ప్రకారం'))}
      <div class="card scroll"><h3>${T('Bhava madhya', 'భావ మధ్యం')}</h3><table class="grid"><tr><th>#</th><th>${T('Madhya', 'మధ్యం')}</th><th>${T('Planets', 'గ్రహాలు')}</th></tr>${bh}</table></div></div>`;
  }

  function renderVargas() {
    const v = S.horo.chart.vargas;
    const btns = S.meta.vargas.map(x => `<button class="${x.code === S.varga ? 'on' : ''}" data-v="${x.code}">${x.code}</button>`).join('');
    const sel = v[S.varga];
    const grid = S.meta.vargas.map(m => v[m.code]).map(x => `<div class="mini" data-v="${x.code}">${southChart(x.boxes, x.lagna_sign, x.code, nm(x))}</div>`).join('');
    $('#tab-vargas').innerHTML = `<div class="pills">${btns}</div>
      <div class="card"><h3>${sel.code} – ${nm(sel)}</h3><p>${S.lang === 'telugu' ? sel.purpose_telugu : sel.purpose_english}</p>
      <div class="charts">${southChart(sel.boxes, sel.lagna_sign, sel.code, nm(sel))}</div></div>
      <div class="minis">${grid}</div>`;
    $$('#tab-vargas [data-v]').forEach(b => b.onclick = () => { S.varga = b.dataset.v; renderVargas(); });
  }

  function renderDasha() {
    const d = S.horo.dasha, bj = S.horo.chart.birth.jd_ut;
    const bd = S.horo.chart.birth.date.split('-').reverse().join('-');      // dd-mm-yyyy
    const BIRTH = T('Birth', 'జననం');
    // state of a period relative to the birth moment
    const st = (x) => x.end_jd <= bj ? 'prebirth' : (x.start_jd <= bj ? 'atbirth' : '');
    const from = (x) => st(x) === 'atbirth'
      ? `<b>${bd}</b> <span class="bmark">★ ${BIRTH}</span><br><small class="orig">${T('began', 'ప్రారంభం')} ${x.start}</small>` : x.start;
    const tag = (x) => st(x) === 'prebirth' ? ` <small class="pbtag">${T('before birth', 'జననానికి ముందు')}</small>` : '';
    const cur = (d.current || []).map(x => `${pn(x.lord)} (${x.start} – ${x.end})`).join(' › ');
    const bal = d.balance;
    const md = d.mahadashas.map(m => `
      <details ${m.current ? 'open' : ''} class="${m.current ? 'cur' : ''} ${st(m)}"><summary><b>${pn(m.lord)} ${T('Mahadasha', 'మహాదశ')}</b>
        ${st(m) === 'atbirth' ? `${bd} <span class="bmark">★ ${BIRTH}</span> <small class="orig">(${T('began', 'ప్రారంభం')} ${m.start})</small>` : m.start} – ${m.end}
        <small>(${m.years} ${T('yrs', 'సం')})</small></summary>
      <table class="grid"><tr><th>${T('Antardasha', 'అంతర్దశ')}</th><th>${T('From', 'నుండి')}</th><th>${T('To', 'వరకు')}</th><th>${T('Pratyantar', 'ప్రత్యంతర')}</th></tr>
      ${m.sub.map(a => `<tr class="${a.current ? 'cur' : ''} ${st(a)}"><td>${pn(a.lord)}${tag(a)}</td><td>${from(a)}</td><td>${a.end}</td>
        <td><details><summary>${T('show', 'చూపు')}</summary>${a.sub.map(p => `<div class="${p.current ? 'cur' : ''} ${st(p)}">${pn(p.lord)}: ${st(p) === 'atbirth' ? `${bd} ★` : p.start} – ${p.end}${tag(p)}</div>`).join('')}</details></td></tr>`).join('')}
      </table></details>`).join('');
    $('#tab-dasha').innerHTML = `<div class="card"><h3>${T('Current period', 'ప్రస్తుత దశ')}</h3><p class="big">${cur || '-'}</p>
      <p>${T('Dasha balance at birth', 'జనన కాల దశా శేషం')}: <b>${pn(d.birth_lord)} ${bal.years}${T('y', 'సం')} ${bal.months}${T('m', 'నె')} ${bal.days}${T('d', 'రో')}</b></p>
      <p class="note">★ = ${T('period running at birth (dates shown from the birth date)', 'జనన సమయంలో నడుస్తున్న దశ (జనన తేదీ నుండి చూపబడింది)')} · <span class="pbtag">${T('grey = before birth', 'బూడిద రంగు = జననానికి ముందు')}</span></p></div>
      <div class="card">${md}</div>`;
  }


  function renderAshtaka() {
    const a = S.horo.ashtakavarga, lag = S.horo.chart.lagna.sign.index;
    const planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn'];
    let head = `<tr><th></th>${[...Array(12).keys()].map(i => `<th>${rasi(i)}</th>`).join('')}<th>${T('Total', 'మొత్తం')}</th></tr>`;
    const rows = planets.map(p => `<tr><td><b>${pn(p)}</b></td>${a.bav[p].map(n => `<td>${n}</td>`).join('')}<td><b>${a.bav_totals[p]}</b></td></tr>`).join('');
    const sav = `<tr class="sav"><td><b>${T('SAV', 'సర్వాష్టకవర్గ')}</b></td>${a.sav.map(n => `<td class="${n >= 28 ? 'good' : 'weak'}">${n}</td>`).join('')}<td><b>${a.sav_total}</b></td></tr>`;
    const withNums = southChart({}, lag, T('SAV', 'సర్వాష్టకవర్గ'), a.sav_total, [], { nums: a.sav });
    $('#tab-ashtaka').innerHTML = `<div class="charts">${withNums}</div>
      <div class="card scroll"><h3>${T('Bhinnashtakavarga', 'భిన్నాష్టకవర్గ')}</h3><table class="grid">${head}${rows}${sav}</table>
      <p class="note">${T('28+ bindus in a sign = strong for transits through it.', '28 పైన బిందువులు ఉన్న రాశి గోచారానికి బలమైనది.')}</p></div>`;
  }

  function renderPhalitam() {
    const sec = S.horo.predictions;
    const yogas = S.horo.yogas.map(y => `<div class="yoga ${y.strength}"><b>${nm(y)}</b><p>${y.description}</p></div>`).join('');
    $('#tab-phalitam').innerHTML = `<div class="card"><h3>${T('Yogas', 'యోగాలు')}</h3>${yogas || '-'}</div>` +
      sec.filter(s => s.title_english !== 'Yogas').map(s => `<div class="card"><h3>${S.lang === 'telugu' ? s.title_telugu : s.title_english}</h3>${s.items.map(i => `<p>${i}</p>`).join('')}</div>`).join('') +
      `<p class="note">${T('Rule-based draft interpretations — please consult an astrologer before acting on them.', 'నియమాల ఆధారిత ప్రాథమిక ఫలితాలు — నిర్ణయాలకు ముందు జ్యోతిష్కులను సంప్రదించండి.')}</p>`;
  }

  function renderGochara() {
    const g = S.horo.gochara;
    const boxes = {}; for (let i = 0; i < 12; i++) boxes[i] = [];
    g.rows.forEach(r => boxes[r.sign.index].push(r.key));
    const moonSign = S.horo.chart.grahas[1].sign.index;
    const rows = g.rows.map(r => `<tr class="${r.favourable ? 'good' : 'weak'}"><td>${nm(r)}</td><td>${nm(r.sign)} ${r.degree_in_sign}${r.retrograde && !['rahu', 'ketu'].includes(r.key) ? ' (' + S.meta.labels[S.lang].retro + ')' : ''}</td><td>${nm(r.nakshatra)}</td><td>${r.house_from_moon}</td><td>${r.house_from_lagna}</td><td>${r.favourable ? T('Favourable', 'శుభం') : T('Unfavourable', 'అశుభం')}</td></tr>`).join('');
    const sh = g.shani ? `<div class="alert">${nm(g.shani)}</div>` : '';
    $('#tab-gochara').innerHTML = `${sh}<div class="charts">${southChart(boxes, moonSign, T('Gocharam (today)', 'గోచారం (ఈరోజు)'), T('highlight = Janma rasi', 'గుర్తు = జన్మ రాశి'), g.rows)}</div>
      <div class="card scroll"><table class="grid"><tr><th>${T('Planet', 'గ్రహం')}</th><th>${T('Position', 'స్థితి')}</th><th>${T('Nakshatra', 'నక్షత్రం')}</th><th>${T('From Moon', 'చంద్రుని నుండి')}</th><th>${T('From Lagna', 'లగ్నం నుండి')}</th><th></th></tr>${rows}</table></div>`;
  }


  // ------------------------------------------------------------ Remedies (పరిహారాలు)
  function remedyCards(list, opts = {}) {
    if (!list.length) return `<div class="card"><p>${T('No specific dosha requiring a remedy was found.', 'పరిహారం అవసరమైన ప్రత్యేక దోషం కనిపించలేదు.')}</p></div>`;
    const L = (o, k) => o[k + (S.lang === 'telugu' ? '_telugu' : '_english')];
    const PRI = { 1: ['Important', 'ముఖ్యం'], 2: ['Recommended', 'సూచనీయం'], 3: ['Optional', 'ఐచ్ఛికం'] };
    return list.map(r => `<div class="card remedy p${r.priority}">
      <h3>${L(r, 'title')} <span class="badge ${r.priority === 1 ? 'bad' : r.priority === 2 ? 'medium' : 'good'}">${S.lang === 'telugu' ? PRI[r.priority][1] : PRI[r.priority][0]}</span>
        ${r.for ? `<span class="badge medium">${r.for === 'boy' ? T('for the boy', 'వరునికి') : T('for the girl', 'వధువుకు')}</span>` : ''}
        ${r.transit ? `<span class="badge medium">${T('current transit', 'ప్రస్తుత గోచారం')}</span>` : ''}</h3>
      <p class="why"><b>${T('Why', 'కారణం')}:</b> ${(S.lang === 'telugu' ? r.reasons_telugu : r.reasons_english).join('; ')}</p>
      <p><b>${T('Puja', 'పరిహార పూజ')}:</b> ${L(r, 'puja')}</p>
      ${r.japa.map(j => `<div class="japa"><b>${T('Japa', 'జపం')} — ${S.lang === 'telugu' ? j.name_telugu : j.name_english}:</b>
          <span class="mantra">${j.beeja}</span>
          <span>${j.count.toLocaleString('en-IN')} ${T('times', 'సార్లు')} · ${S.lang === 'telugu' ? j.day_telugu : j.day_english}</span></div>`).join('')}
      ${r.mantra ? `<div class="japa"><b>${T('Mantra', 'మంత్రం')}:</b> <span class="mantra">${r.mantra}</span></div>` : ''}
      ${L(r, 'dana') ? `<p><b>${T('Dana', 'దానం')}:</b> ${L(r, 'dana')}</p>` : ''}
      ${L(r, 'temple') ? `<p><b>${T('Temple', 'క్షేత్రం')}:</b> ${L(r, 'temple')}</p>` : ''}
    </div>`).join('') + `<p class="note card">${T('Japa counts and procedures differ between traditions and families. Please have a purohit or astrologer confirm the sankalpam, count and muhurtham before performing them. Remedies are traditional practices, not guarantees.',
      'జప సంఖ్యలు, విధానాలు సంప్రదాయం మరియు కుటుంబ ఆచారాన్ని బట్టి మారుతాయి. చేసే ముందు సంకల్పం, సంఖ్య, ముహూర్తాన్ని పురోహితులు / జ్యోతిష్కులతో నిర్ధారించుకోండి. పరిహారాలు సాంప్రదాయిక ఆచరణలు మాత్రమే, హామీలు కావు.')}</p>`;
  }

  function renderParihara() {
    $('#tab-parihara').innerHTML = `<div class="card"><h3>${T('Remedies — Parihara Pujas & Dosha Nivarana Japa', 'పరిహార పూజలు, దోష నివారణ జపాలు')}</h3>
      <p class="note">${T('Suggested only for doshas actually found in this chart, most important first.', 'ఈ జాతకంలో నిజంగా ఉన్న దోషాలకు మాత్రమే, ముఖ్యమైనవి ముందుగా.')}</p></div>` + remedyCards(S.horo.remedies);
  }

  // ------------------------------------------------------------ Match making
  async function runMatch() {
    try {
      $('#matchOut').innerHTML = T('Calculating…', 'లెక్కిస్తున్నాం…');
      S.match = await post('/match', { boy: readForm($('#boyForm')), girl: readForm($('#girlForm')) });
      renderMatch();
    } catch (e) { $('#matchOut').innerHTML = `<div class="msg err">${e.message}</div>`; }
  }

  function renderMatch() {
    const m = S.match, R = m.result, L = S.meta.labels[S.lang];
    const tt = (pair) => S.lang === 'telugu' ? pair[1] : pair[0];
    const RES = { good: ['Good', 'అనుకూలం'], medium: ['Medium', 'మధ్యమం'], bad: ['Not matching', 'ప్రతికూలం'] };
    const badge = (r) => `<span class="badge ${r}">${tt(RES[r])}</span>`;
    const VERDICT = {
      good: ['Good match', 'ఉత్తమ పొంతన'], average: ['Average — consult an astrologer', 'మధ్యమ పొంతన — జ్యోతిష్కుని సంప్రదించండి'],
      weak: ['Weak match', 'బలహీన పొంతన'], not_recommended: ['Not recommended (Rajju / Vedha dosha)', 'సిఫార్సు చేయబడదు (రజ్జు / వేధ దోషం)'] };
    const FLAGS = { rajju: ['Rajju dosha', 'రజ్జు దోషం'], vedha: ['Vedha dosha', 'వేధ దోషం'],
      kuja_one_sided: ['Kuja dosha in only one chart', 'ఒక జాతకంలో మాత్రమే కుజ దోషం'], nadi: ['Nadi dosha', 'నాడీ దోషం'],
      bhakoot: ['Bhakoot dosha', 'భకూట దోషం'], papa: ['Bride has more papam (Papasamyam)', 'వధువుకు పాపం ఎక్కువ (పాపసామ్యం)'] };
    const GANA = [['Deva', 'దేవ'], ['Manushya', 'మనుష్య'], ['Rakshasa', 'రాక్షస']];
    const YONI = [['Horse', 'అశ్వ'], ['Elephant', 'గజ'], ['Sheep', 'మేష'], ['Serpent', 'సర్ప'], ['Dog', 'శునక'], ['Cat', 'మార్జాల'],
      ['Rat', 'మూషిక'], ['Cow', 'గో'], ['Buffalo', 'మహిష'], ['Tiger', 'వ్యాఘ్ర'], ['Deer', 'మృగ'], ['Monkey', 'వానర'], ['Mongoose', 'నకుల'], ['Lion', 'సింహ']];
    const RAJJU = [['Pada', 'పాద'], ['Kati', 'కటి'], ['Nabhi', 'నాభి'], ['Kantha', 'కంఠ'], ['Siro', 'శిరో']];
    const NADI = [['Adi', 'ఆది'], ['Madhya', 'మధ్య'], ['Antya', 'అంత్య']];
    const KUJA = { none: ['No dosha', 'దోషం లేదు'], cancelled: ['Dosha cancelled', 'దోష భంగం'], present: ['Dosha present', 'దోషం ఉంది'] };
    const KUJA_EXC = { own_exalted: ['Mars in own / exaltation sign', 'కుజుడు స్వక్షేత్ర / ఉచ్ఛ'],
      sign_exception_lagna: ['Classical sign exception (from Lagna)', 'శాస్త్రీయ రాశి మినహాయింపు (లగ్నం నుండి)'],
      sign_exception_moon: ['Classical sign exception (from Moon)', 'శాస్త్రీయ రాశి మినహాయింపు (చంద్రుని నుండి)'],
      jupiter: ['Jupiter conjoins / aspects Mars', 'కుజునిపై గురు యుతి / దృష్టి'],
      moon_conjunct: ['Moon with Mars (some traditions)', 'చంద్ర-కుజ యుతి (కొన్ని సంప్రదాయాలు)'] };
    const CANCEL = { same_rasi_diff_star: ['Cancelled: same rasi, different nakshatra', 'భంగం: ఒకే రాశి, వేర్వేరు నక్షత్రాలు'],
      same_star_diff_rasi: ['Cancelled: same nakshatra, different rasi', 'భంగం: ఒకే నక్షత్రం, వేర్వేరు రాశులు'],
      same_star_diff_pada: ['Cancelled: same nakshatra, different pada', 'భంగం: ఒకే నక్షత్రం, వేర్వేరు పాదాలు'],
      same_lord: ['Cancelled: same rasi lord', 'భంగం: రాశ్యాధిపతి ఒక్కరే'], lords_friends: ['Cancelled: rasi lords are friends', 'భంగం: రాశ్యాధిపతులు మిత్రులు'] };
    const REF = { lagna: ['Lagna', 'లగ్నం'], moon: ['Moon', 'చంద్రుడు'], venus: ['Venus', 'శుక్రుడు'] };
    const pl = (arr) => (arr && arr.length ? arr.map(pn).join(', ') : '—');
    const dig = (d) => (d ? (L[d] || d) : '—');
    const hs = (n) => `${n}${T('th house', 'వ స్థానం')}`;
    const nak = (i) => S.meta.nakshatra[S.lang][i];
    const B = R.individual.boy, G = R.individual.girl;
    const BOY = T('Boy', 'వరుడు'), GIRL = T('Girl', 'వధువు');
    const cmpHead = `<tr><th>${T('Parameter', 'అంశం')}</th><th>${BOY}</th><th>${GIRL}</th></tr>`;
    const cmpRow = (label, fb, fg) => `<tr><td>${label}</td><td>${fb}</td><td>${fg}</td></tr>`;
    const sec = (no, en, te, inner, note) => `<div class="card msec"><h3><span class="no">${no}</span>${T(en, te)}</h3>${inner}${note ? `<p class="note">${note}</p>` : ''}</div>`;

    // ---- Summary
    const s = R.summary;
    const pct = Math.round(s.ashtakoota / 36 * 100);
    const info = (c) => { const mo = c.grahas[1]; return `${esc(c.name || '')}: ${nm(mo.sign)}, ${nm(mo.nakshatra)} ${mo.nakshatra.pada}`; };
    let html = `<div class="card score"><div class="ring" style="--p:${pct}"><span>${s.ashtakoota}<small>/36</small></span></div>
      <div><h3 class="verdict ${s.verdict}">${tt(VERDICT[s.verdict])}</h3>
      <p><b>${T('Dasha poruthams', 'దశ పొంతనలు')}:</b> ${s.porutham_score} / 10 &nbsp; <b>${T('Ashtakoota', 'అష్టకూట')}:</b> ${s.ashtakoota} / 36</p>
      <p>${BOY} – ${info(m.boy)}<br>${GIRL} – ${info(m.girl)}</p>
      ${s.flags.length ? `<p class="flags">${s.flags.map(f => `<span class="badge bad">${tt(FLAGS[f])}</span>`).join(' ')}</p>` : ''}</div></div>`;

    // ---- 1-10 Dasha poruthams
    const pdet = (r) => { const i = r.info; switch (r.key) {
      case 'dina': case 'mahendra': case 'sthree_deergha': case 'rasi': return `${T('Count', 'లెక్క')} ${i.count}`;
      case 'gana': return `${tt(GANA[i.boy])} / ${tt(GANA[i.girl])}`;
      case 'yoni': return `${tt(YONI[i.boy])} / ${tt(YONI[i.girl])}`;
      case 'rasyadhipathi': return `${pn(i.boy)} / ${pn(i.girl)}`;
      case 'vasya': return `${rasi(i.boy)} / ${rasi(i.girl)}`;
      case 'rajju': return `${tt(RAJJU[i.boy])} / ${tt(RAJJU[i.girl])}`;
      case 'vedha': return `${nak(i.boy)} / ${nak(i.girl)}`; } return ''; };
    const prow = R.poruthams.rows.map(r => `<tr class="${r.key === 'rajju' || r.key === 'vedha' ? 'must' : ''}"><td>${r.no}</td><td>${nm(r)}</td><td>${pdet(r)}</td><td>${badge(r.result)}</td></tr>`).join('');
    html += sec(1, 'Dasha Poruthams (1–10)', 'దశ పొంతనలు (1–10)',
      `<div class="scroll"><table class="grid"><tr><th>#</th><th>${T('Porutham', 'పొంతన')}</th><th>${BOY} / ${GIRL}</th><th>${T('Result', 'ఫలితం')}</th></tr>${prow}
       <tr><td></td><td><b>${T('Total', 'మొత్తం')}</b></td><td></td><td><b>${R.poruthams.score} / 10</b></td></tr></table></div>`,
      T('Counts are from the girl\'s nakshatra / rasi to the boy\'s. Rajju and Vedha are mandatory.', 'లెక్కలు వధువు నక్షత్రం / రాశి నుండి వరుని వరకు. రజ్జు, వేధ తప్పనిసరి.'));

    // ---- Ashtakoota
    const ak = R.ashtakoota, order = ['varna', 'vashya', 'tara', 'yoni', 'graha_maitri', 'gana', 'bhakoot', 'nadi'];
    const klabel = (k) => S.lang === 'telugu' ? ak.kootas[k].name_telugu : k.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    const EN2 = { Brahmin: 'బ్రాహ్మణ', Kshatriya: 'క్షత్రియ', Vaishya: 'వైశ్య', Shudra: 'శూద్ర', Chatushpada: 'చతుష్పాద',
      Manava: 'మానవ', Jalachara: 'జలచర', Vanachara: 'వనచర', Keeta: 'కీట' };
    [GANA, YONI, NADI].forEach(list => list.forEach(([en, te]) => { EN2[en] = te; }));
    const kval = (v) => typeof v === 'string' && S.meta.planets[v] ? pn(v) : (S.lang === 'telugu' && EN2[v] ? EN2[v] : v);
    const krows = order.map(k => { const x = ak.kootas[k]; return `<tr class="${x.score === 0 ? 'weak' : ''}"><td>${klabel(k)}</td><td>${kval(x.boy)}</td><td>${kval(x.girl)}</td><td><b>${x.score}</b> / ${x.max}</td></tr>`; }).join('');
    html += sec(2, 'Ashtakoota (36 Gunas)', 'అష్టకూట పొంతన (36 గుణాలు)',
      `<div class="scroll"><table class="grid"><tr><th>${T('Koota', 'కూటమి')}</th><th>${BOY}</th><th>${GIRL}</th><th>${T('Points', 'గుణాలు')}</th></tr>${krows}
       <tr><td><b>${T('Total', 'మొత్తం')}</b></td><td></td><td></td><td><b>${ak.total} / 36</b></td></tr></table></div>`,
      T('18+ is the usual threshold; a score alone should not decide a marriage.', 'సాధారణంగా 18+ ఆమోదయోగ్యం; కేవలం స్కోరుతో నిర్ణయించకూడదు.'));

    // ---- 11-13 Doshas
    const D = R.doshas;
    const kujaCell = (ind) => { const k = ind.kuja;
      const from = Object.entries(k.from).map(([r, v]) => `${tt(REF[r])}: ${hs(v.house)}${v.dosha ? ' ⚠' : ''}`).join('<br>');
      return `<b>${tt(KUJA[k.status])}</b><br><small>${from}${k.status !== 'none' && k.exceptions.length ? '<br>' + k.exceptions.map(e => tt(KUJA_EXC[e])).join('<br>') : ''}</small>`; };
    html += sec(3, 'Doshas — Kuja, Nadi, Bhakoot (11–13)', 'దోషాలు — కుజ, నాడీ, భకూట (11–13)',
      `<div class="scroll"><table class="grid"><tr><th>${T('Dosha', 'దోషం')}</th><th>${BOY}</th><th>${GIRL}</th><th>${T('Result', 'ఫలితం')}</th></tr>
       <tr><td>11. ${T('Kuja dosha', 'కుజ దోషం')}</td><td>${kujaCell(B)}</td><td>${kujaCell(G)}</td><td>${badge(D.kuja.result)}${D.kuja.samyam ? `<br><small>${T('Both have it — samyam', 'ఇద్దరికీ ఉంది — సామ్యం')}</small>` : ''}</td></tr>
       <tr><td>12. ${T('Nadi dosha', 'నాడీ దోషం')}</td><td>${tt(NADI[D.nadi.boy])}</td><td>${tt(NADI[D.nadi.girl])}</td><td>${badge(D.nadi.result)}${D.nadi.cancel ? `<br><small>${tt(CANCEL[D.nadi.cancel])}</small>` : ''}</td></tr>
       <tr><td>13. ${T('Bhakoot dosha', 'భకూట దోషం')}</td><td colspan="2">${T('Rasi count', 'రాశి లెక్క')} ${D.bhakoot.count} (${rasi(m.girl.grahas[1].sign.index)} → ${rasi(m.boy.grahas[1].sign.index)})</td><td>${badge(D.bhakoot.result)}${D.bhakoot.cancel ? `<br><small>${tt(CANCEL[D.bhakoot.cancel])}</small>` : ''}</td></tr>
       </table></div>`,
      T('Kuja dosha: Mars in 1, 2, 4, 7, 8, 12 from Lagna or Moon (Venus shown for reference). Matching is fine when both or neither have it.',
        'కుజ దోషం: లగ్నం లేదా చంద్రుని నుండి 1, 2, 4, 7, 8, 12 స్థానాల్లో కుజుడు (శుక్రుడు సూచన కోసం). ఇద్దరికీ ఉన్నా, ఇద్దరికీ లేకపోయినా పొంతన సరిపోతుంది.'));

    // ---- 14 Papasamyam
    const P = R.papasamyam;
    const papaList = (x) => x.items.length ? x.items.map(i => `${pn(i.planet)} – ${tt(REF[i.from])} ${hs(i.house)} (${i.points})`).join('<br>') : '—';
    html += sec(4, 'Papasamyam (14)', 'పాపసామ్యం (14)',
      `<div class="scroll"><table class="grid">${cmpHead}
       ${cmpRow(T('Papa points', 'పాప బిందువులు'), `<b>${P.boy.total}</b>`, `<b>${P.girl.total}</b>`)}
       ${cmpRow(T('Details', 'వివరాలు'), `<small>${papaList(P.boy)}</small>`, `<small>${papaList(P.girl)}</small>`)}
       <tr><td>${T('Result', 'ఫలితం')}</td><td colspan="2">${badge(P.result)}</td></tr></table></div>`,
      T('Malefics (Mars, Saturn, Rahu, Ketu, Sun ½) in 1, 2, 4, 7, 8, 12 from Lagna (×1), Moon (×½), Venus (×¼). Boy\'s total should be equal or higher.',
        'పాప గ్రహాలు (కుజ, శని, రాహు, కేతు, రవి ½) లగ్నం (×1), చంద్ర (×½), శుక్ర (×¼) నుండి 1, 2, 4, 7, 8, 12 లో. వరుని పాపం సమానంగా లేదా ఎక్కువగా ఉండాలి.'));

    // ---- 15-16 7th house & lord
    const h7 = (x) => x.seventh;
    const lordCell = (h) => `${pn(h.lord)} – ${hs(h.lord_house)}, ${rasi(h.lord_sign)}<br><small>${dig(h.lord_dignity)}${h.lord_combust ? ', ' + T('combust', 'అస్తంగతం') : ''}${h.lord_retro ? ', ' + T('retro', 'వక్రం') : ''}</small>`;
    html += sec(5, '7th House & 7th Lord (15–16)', 'సప్తమ స్థానం, సప్తమాధిపతి (15–16)',
      `<div class="scroll"><table class="grid">${cmpHead}
       ${cmpRow(T('7th house sign', 'సప్తమ రాశి'), rasi(h7(B).sign), rasi(h7(G).sign))}
       ${cmpRow(T('Planets in 7th', 'సప్తమంలో గ్రహాలు'), pl(h7(B).occupants), pl(h7(G).occupants))}
       ${cmpRow(T('Aspects on 7th', 'సప్తమంపై దృష్టి'), pl(h7(B).aspects), pl(h7(G).aspects))}
       ${cmpRow(T('7th lord', 'సప్తమాధిపతి'), lordCell(h7(B)), lordCell(h7(G)))}
       ${cmpRow(T('Indication', 'సూచన'), badge(h7(B).result), badge(h7(G).result))}</table></div>`);

    // ---- 17 Navamsa
    const nv = (x) => x.navamsa;
    const nvl = (n, k) => `${pn(n[k + '_lord'])} – ${hs(n[k + '_lord_house'])} <small>(${dig(n[k + '_lord_dignity'])})</small>`;
    const nvk = (o) => `${rasi(o.sign)}, ${hs(o.house)} <small>(${dig(o.dignity)})</small>`;
    html += sec(6, 'Navamsa — D9 (17)', 'నవాంశ — D9 (17)',
      `<div class="scroll"><table class="grid">${cmpHead}
       ${cmpRow(T('D9 Lagna', 'నవాంశ లగ్నం'), rasi(nv(B).lagna_sign), rasi(nv(G).lagna_sign))}
       ${cmpRow(T('D9 Lagna lord', 'నవాంశ లగ్నాధిపతి'), nvl(nv(B), 'lagna'), nvl(nv(G), 'lagna'))}
       ${cmpRow(T('D9 7th sign', 'నవాంశ సప్తమ రాశి'), rasi(nv(B).seventh_sign), rasi(nv(G).seventh_sign))}
       ${cmpRow(T('D9 7th lord', 'నవాంశ సప్తమాధిపతి'), nvl(nv(B), 'seventh'), nvl(nv(G), 'seventh'))}
       ${cmpRow(T('Planets in D9 7th', 'నవాంశ సప్తమంలో గ్రహాలు'), pl(nv(B).seventh_occupants), pl(nv(G).seventh_occupants))}
       ${cmpRow(T('Venus in D9', 'నవాంశలో శుక్రుడు'), nvk(nv(B).venus), nvk(nv(G).venus))}
       ${cmpRow(T('Jupiter in D9', 'నవాంశలో గురువు'), nvk(nv(B).jupiter), nvk(nv(G).jupiter))}
       ${cmpRow(T('Vargottama', 'వర్గోత్తమ'), pl(nv(B).vargottama), pl(nv(G).vargottama))}</table></div>`);

    // ---- 18 Venus & Jupiter
    const kc = (x, p) => { const k = x.karakas[p];
      return `${x.primary_karaka === p ? '★ ' : ''}${rasi(k.sign)}, ${hs(k.house)}<br><small>${dig(k.dignity)}${k.combust ? ', ' + T('combust', 'అస్తంగతం') : ''}${k.retro ? ', ' + T('retro', 'వక్రం') : ''} · D9: ${dig(k.d9_dignity)}</small>`; };
    html += sec(7, 'Venus & Jupiter — marriage significators (18)', 'శుక్ర, గురు — వివాహ కారకులు (18)',
      `<div class="scroll"><table class="grid">${cmpHead}
       ${cmpRow(pn('venus'), kc(B, 'venus'), kc(G, 'venus'))}${cmpRow(pn('jupiter'), kc(B, 'jupiter'), kc(G, 'jupiter'))}</table></div>`,
      T('★ = primary significator: Venus for the boy, Jupiter for the girl.', '★ = ముఖ్య కారకుడు: వరునికి శుక్రుడు, వధువుకు గురువు.'));

    // ---- 19 Dasha-Bhukti
    const dcol = (x) => { const d = x.dasha;
      const cur = (d.current || []).slice(0, 2).map(c => pn(c.lord)).join(' › ') || '—';
      const rows = d.periods.map(p => `<tr class="${p.current ? 'cur' : ''}"><td>${pn(p.md)} › ${pn(p.ad)}</td><td>${p.start} – ${p.end}</td><td>${p.strong ? '✓✓' : p.supportive ? '✓' : ''}</td></tr>`).join('');
      return `<p><b>${T('Now', 'ప్రస్తుతం')}:</b> ${cur}</p><p class="note">${T('Marriage-related lords', 'వివాహ సంబంధ గ్రహాలు')}: ${pl(d.supportive_lords)}</p>
        <table class="grid"><tr><th>${T('Dasha › Bhukti', 'దశ › భుక్తి')}</th><th>${T('Period', 'కాలం')}</th><th></th></tr>${rows}</table>`; };
    html += sec(8, 'Dasha-Bhukti — next 7 years (19)', 'దశా భుక్తి — రాబోయే 7 సంవత్సరాలు (19)',
      `<div class="two"><div><h4>${BOY}</h4>${dcol(B)}</div><div><h4>${GIRL}</h4>${dcol(G)}</div></div>`,
      T('✓ = Dasha or Bhukti lord is linked to marriage (7th lord, planet in 7th, D9 7th lord, Venus, or the karaka). ✓✓ = both.',
        '✓ = దశ లేదా భుక్తి నాథుడు వివాహానికి సంబంధించినవాడు (సప్తమాధిపతి, సప్తమ గ్రహం, నవాంశ సప్తమాధిపతి, శుక్రుడు లేదా కారకుడు). ✓✓ = రెండూ.'));

    // ---- 20 Houses 2/4/8/12
    const HN = { 2: ['2nd — family', '2వ — కుటుంబం'], 4: ['4th — domestic happiness', '4వ — గృహ సుఖం'],
      8: ['8th — longevity of marriage', '8వ — మాంగల్య బలం'], 12: ['12th — intimacy, private life', '12వ — శయ్యా సుఖం'] };
    const hcell = (h) => `${rasi(h.sign)} · ${T('lord', 'అధిపతి')} ${pn(h.lord)} ${hs(h.lord_house)} <small>(${dig(h.lord_dignity)})</small><br><small>${T('Planets', 'గ్రహాలు')}: ${pl(h.occupants)}</small> ${badge(h.result)}`;
    html += sec(9, 'Houses 2, 4, 8, 12 (20)', '2, 4, 8, 12 స్థానాలు (20)',
      `<div class="scroll"><table class="grid">${cmpHead}${[2, 4, 8, 12].map(h => cmpRow(tt(HN[h]), hcell(B.houses[h]), hcell(G.houses[h]))).join('')}</table></div>`);

    // ---- 21 Santana
    const sc = (x) => { const s5 = x.santana; return `${rasi(s5.sign)} · ${T('lord', 'అధిపతి')} ${pn(s5.lord)} ${hs(s5.lord_house)} <small>(${dig(s5.lord_dignity)})</small><br>
      <small>${T('Planets in 5th', '5వ స్థానంలో')}: ${pl(s5.occupants)} · ${pn('jupiter')}: ${hs(s5.jupiter_house)} (${dig(s5.jupiter_dignity)})</small><br>${badge(s5.result)}`; };
    html += sec(10, 'Santana — progeny indicators (21)', 'సంతాన సూచనలు (21)',
      `<div class="scroll"><table class="grid">${cmpHead}${cmpRow(T('5th house & Jupiter', '5వ స్థానం, గురువు'), sc(B), sc(G))}</table></div>`);

    // ---- 22 Graha bala
    const gb = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn'].map(p =>
      cmpRow(pn(p), `<span class="lvl ${B.graha_bala[p].level}">${B.graha_bala[p].score}</span>`, `<span class="lvl ${G.graha_bala[p].level}">${G.graha_bala[p].score}</span>`)).join('');
    html += sec(11, 'Graha Bala — planetary strength (22)', 'గ్రహ బలం (22)',
      `<div class="scroll"><table class="grid">${cmpHead}${gb}</table></div>`,
      T('Simplified 0–10 strength from dignity (Rasi + Navamsa), house, combustion and retrogression. This is not full Shadbala.',
        'రాశి + నవాంశ స్థితి, స్థానం, అస్తంగత్వం, వక్రం ఆధారంగా 0–10 సరళ బలం. ఇది పూర్తి షడ్బలం కాదు.'));

    // ---- 12 Remedies
    html += `<div class="card msec"><h3><span class="no">12</span>${T('Remedies', 'పరిహారాలు')}</h3></div>` + remedyCards(R.remedies || []);

    // ---- Charts
    html += `<div class="charts">${southChart(m.boy.vargas.D1.boxes, m.boy.vargas.D1.lagna_sign, T('Boy – Rasi', 'వరుడు – రాశి'), m.boy.name, m.boy.grahas)}
        ${southChart(m.boy.vargas.D9.boxes, m.boy.vargas.D9.lagna_sign, T('Boy – Navamsa', 'వరుడు – నవాంశ'), m.boy.name, m.boy.grahas)}</div>
      <div class="charts">${southChart(m.girl.vargas.D1.boxes, m.girl.vargas.D1.lagna_sign, T('Girl – Rasi', 'వధువు – రాశి'), m.girl.name, m.girl.grahas)}
        ${southChart(m.girl.vargas.D9.boxes, m.girl.vargas.D9.lagna_sign, T('Girl – Navamsa', 'వధువు – నవాంశ'), m.girl.name, m.girl.grahas)}</div>
      <p class="note card">${T('These are traditional calculations, not proven predictors of marital success. Communication, values and mutual respect matter as much. Final judgement should come from an astrologer reviewing both full horoscopes.',
        'ఇవి సాంప్రదాయిక లెక్కలు మాత్రమే; వివాహ విజయాన్ని నిర్ధారించవు. పరస్పర గౌరవం, విలువలు, సంభాషణ కూడా అంతే ముఖ్యం. రెండు పూర్తి జాతకాలను జ్యోతిష్కులు పరిశీలించి తుది నిర్ణయం చెప్పాలి.')}</p>`;
    $('#matchOut').innerHTML = html;
  }

  boot();
})();
