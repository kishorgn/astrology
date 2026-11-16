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
    renderJathakam(); renderGrahas(); renderVargas(); renderDasha(); renderAshtaka(); renderPhalitam(); renderGochara();
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
      [T('Kuja dosha', 'కుజ దోషం'), kd.present ? T('Present', 'ఉంది') : T('Not present', 'లేదు') + (kd.exceptions.length ? ` (${T('cancelled', 'భంగం')})` : '')],
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
    const d = S.horo.dasha;
    const cur = (d.current || []).map(x => `${pn(x.lord)} (${x.start} – ${x.end})`).join(' › ');
    const md = d.mahadashas.map(m => `
      <details ${m.current ? 'open' : ''} class="${m.current ? 'cur' : ''}"><summary><b>${pn(m.lord)} ${T('Mahadasha', 'మహాదశ')}</b> ${m.start} – ${m.end} <small>(${m.years} ${T('yrs', 'సం')})</small></summary>
      <table class="grid"><tr><th>${T('Antardasha', 'అంతర్దశ')}</th><th>${T('From', 'నుండి')}</th><th>${T('To', 'వరకు')}</th><th>${T('Pratyantar', 'ప్రత్యంతర')}</th></tr>
      ${m.sub.map(a => `<tr class="${a.current ? 'cur' : ''}"><td>${pn(a.lord)}</td><td>${a.start}</td><td>${a.end}</td>
        <td><details><summary>${T('show', 'చూపు')}</summary>${a.sub.map(p => `<div class="${p.current ? 'cur' : ''}">${pn(p.lord)}: ${p.start} – ${p.end}</div>`).join('')}</details></td></tr>`).join('')}
      </table></details>`).join('');
    $('#tab-dasha').innerHTML = `<div class="card"><h3>${T('Current period', 'ప్రస్తుత దశ')}</h3><p class="big">${cur || '-'}</p></div><div class="card">${md}</div>`;
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

  // ------------------------------------------------------------ Match making
  async function runMatch() {
    try {
      $('#matchOut').innerHTML = T('Calculating…', 'లెక్కిస్తున్నాం…');
      S.match = await post('/match', { boy: readForm($('#boyForm')), girl: readForm($('#girlForm')) });
      renderMatch();
    } catch (e) { $('#matchOut').innerHTML = `<div class="msg err">${e.message}</div>`; }
  }

  function renderMatch() {
    const m = S.match, r = m.result;
    const order = ['varna', 'vashya', 'tara', 'yoni', 'graha_maitri', 'gana', 'bhakoot', 'nadi'];
    const label = (k) => S.lang === 'telugu' ? r.kootas[k].name_telugu : k.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    const val = (v) => typeof v === 'string' && S.meta.planets[v] ? pn(v) : v;
    const rows = order.map(k => { const x = r.kootas[k]; return `<tr class="${x.score === 0 ? 'weak' : ''}"><td>${label(k)}</td><td>${val(x.boy)}</td><td>${val(x.girl)}</td><td><b>${x.score}</b> / ${x.max}</td></tr>`; }).join('');
    const info = (c) => { const mo = c.grahas[1]; return `${c.name || ''}: ${nm(mo.sign)}, ${nm(mo.nakshatra)} ${mo.nakshatra.pada}`; };
    const pct = Math.round(r.total / 36 * 100);
    $('#matchOut').innerHTML = `
      <div class="card score"><div class="ring" style="--p:${pct}"><span>${r.total}<small>/36</small></span></div>
        <div><h3>${r.verdict}</h3><p>${T('Boy', 'వరుడు')} – ${info(m.boy)}<br>${T('Girl', 'వధువు')} – ${info(m.girl)}</p></div></div>
      <div class="card scroll"><table class="grid"><tr><th>${T('Koota', 'కూటమి')}</th><th>${T('Boy', 'వరుడు')}</th><th>${T('Girl', 'వధువు')}</th><th>${T('Points', 'గుణాలు')}</th></tr>${rows}
        <tr><td><b>${T('Total', 'మొత్తం')}</b></td><td></td><td></td><td><b>${r.total} / 36</b></td></tr></table></div>
      <div class="card"><table class="kv">
        <tr><th>${T('Rajju', 'రజ్జు')}</th><td>${r.rajju.boy} / ${r.rajju.girl} ${r.rajju.dosha ? '⚠' : '✓'}</td></tr>
        <tr><th>${T('Vedha', 'వేధ')}</th><td>${r.vedha ? '⚠' : '✓'}</td></tr>
        <tr><th>${T('Kuja dosha (boy)', 'కుజ దోషం (వరుడు)')}</th><td>${r.kuja.boy.present ? T('Present', 'ఉంది') : T('No', 'లేదు')}</td></tr>
        <tr><th>${T('Kuja dosha (girl)', 'కుజ దోషం (వధువు)')}</th><td>${r.kuja.girl.present ? T('Present', 'ఉంది') : T('No', 'లేదు')}</td></tr></table>
        ${r.notes.map(n => `<p class="note">• ${n}</p>`).join('')}</div>
      <div class="charts">${southChart(m.boy.vargas.D1.boxes, m.boy.vargas.D1.lagna_sign, T('Boy – Rasi', 'వరుడు – రాశి'), m.boy.name, m.boy.grahas)}
        ${southChart(m.girl.vargas.D1.boxes, m.girl.vargas.D1.lagna_sign, T('Girl – Rasi', 'వధువు – రాశి'), m.girl.name, m.girl.grahas)}</div>`;
  }

  boot();
})();
