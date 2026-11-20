'use strict';
/**
 * synthdash.js - the Synthwave dash, the Cluster Themes page's "Dash" tab: the whole centre screen as three neon
 * panels, after the cluster in sl0w.g26's G26 reel.
 *
 *   left    VITALS: speed, rpm, oil and coolant temperature, torque, each with a bar, and this drive's bests
 *   middle  a dusk scene: striped sun, neon mountains and a perspective grid that runs with the speed, a car seen
 *           from behind on it, the speed and gear on top
 *   right   G-RADAR: the friction circle as a radar, a sweep arm turning round it, the car's g as a pink blip
 *
 * The scene is one cached layer; only the grid's cross lines, the numbers and the radar are drawn every frame.
 * Units, the radar's range and the left / right and accel / brake swaps are the app's own settings (units, gRange,
 * gFlipLat, gFlipLong). Colours are this tab's own. Plain Node 8 (the car's 8.16.2).
 */
const G = require('./kit/gauges');

const withAlpha = G.withAlpha;
const MPH = 1.609344;
const C = {
    bg: '#07001a', panel: '#0d0226', pink: '#ff46d2', cyan: '#00e5ff', violet: '#be96ff', white: '#e9fbff',
    gold: '#ffd60a', orange: '#ff8628', red: '#ff2a55',
};
// panels (page coordinates): vitals, scene, radar
const PA = { x: 24, y: 44, w: 480, h: 468 };
const PB = { x: 520, y: 44, w: 560, h: 468 };
const PC = { x: 1096, y: 44, w: 480, h: 468 };
const HZ = 268;          // the scene's horizon (panel-local y)

const isNum = (v) => typeof v === 'number' && isFinite(v);
const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const mix = (a, b, t) => a + (b - a) * t;
const hex = (c) => [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
const fmt = (v, dec) => (isNum(v) ? v.toFixed(dec || 0) : '--');
const temp = (v, mph) => (isNum(v) ? (mph ? v * 9 / 5 + 32 : v) : null);
/** Text that the kit must not translate (the dash is in its own words). */
function T(cv, str, x, y, size, color, opts) { return cv.text(str, x, y, size, color, Object.assign({ literal: true }, opts || {})); }
function lerpHex(a, b, t) { return rgbHex(lerpColor(a, b, t)); }
function lerpColor(c1, c2, t) { const a = hex(c1), b = hex(c2); return [0, 1, 2].map((i) => Math.round(mix(a[i], b[i], t))); }
function rgbHex(v) { return '#' + v.map((n) => ('0' + n.toString(16)).slice(-2)).join(''); }

/** A line with a soft neon glow round it. */
function neonLine(cv, x1, y1, x2, y2, w, color) {
    cv.line(x1, y1, x2, y2, w + 9, withAlpha(color, 0.10));
    cv.line(x1, y1, x2, y2, w + 4, withAlpha(color, 0.22));
    cv.line(x1, y1, x2, y2, w, color);
}

function panelFrame(cv, p, color) {
    cv.roundRect(p.x, p.y, p.w, p.h, 6, C.panel);
    cv.strokeRoundRect(p.x, p.y, p.w, p.h, 6, 11, withAlpha(color, 0.08));
    cv.strokeRoundRect(p.x, p.y, p.w, p.h, 6, 6, withAlpha(color, 0.18));
    cv.strokeRoundRect(p.x + 1, p.y + 1, p.w - 2, p.h - 2, 6, 3, color);
}

/* ---------- the scene (cached layer, panel-local coordinates) ---------- */
function drawScene(c, w, h) {
    const cx = w / 2, R = 122;
    c.gradientRect(0, 0, w, HZ, [[0, '#06001a'], [0.55, '#2a0a56'], [1, '#c81e96']]);
    // stars: a fixed little pattern
    let s = 7;
    const rnd = () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
    for (let i = 0; i < 46; i++) {
        const x = 8 + rnd() * (w - 16), y = 8 + rnd() * (HZ * 0.62);
        c.circle(x, y, 0.9 + rnd() * 0.9, withAlpha('#ffffff', 0.25 + 0.45 * (1 - y / HZ)));
    }
    // halo
    c.circle(cx, HZ, R + 46, withAlpha('#ff4aa8', 0.07));
    c.circle(cx, HZ, R + 28, withAlpha('#ff6a50', 0.11));
    c.circle(cx, HZ, R + 12, withAlpha('#ff9a40', 0.16));
    // the sun: slices, yellow -> orange -> pink, cut by stripes that widen downwards
    for (let y = HZ - R; y < HZ; y += 1) {
        const up = HZ - y - 1, k = 1 - up / R;
        const hw = Math.sqrt(Math.max(0, R * R - up * up));
        const gap = k > 0.42 ? mix(1, 15, clamp((k - 0.42) / 0.58, 0, 1)) : 0;
        if (gap && (up % 21) < gap) continue;
        const col = k < 0.5 ? lerpColor('#ffec46', '#ff8628', k * 2) : lerpColor('#ff8628', '#ff2896', (k - 0.5) * 2);
        c.fillRect(cx - hw, y, hw * 2, 1.6, rgbHex(col));
    }
    // mountains: dark body, neon edge
    const ridge = (x) => {
        const side = x > cx ? 1 : 0, dx = Math.abs(x - cx) / (w / 2), env = clamp((dx - 0.32) / 0.8, 0, 1);
        const e = env * env * (3 - 2 * env), xs = Math.abs(x - cx) + side * 97;
        const tri = (v) => Math.abs((v - Math.floor(v)) * 2 - 1);
        return e * (18 + 118 * (0.55 * tri(xs / 120) + 0.3 * tri(xs / 52 + 0.31) + 0.15 * tri(xs / 23 + 0.7)));
    };
    const pts = [];
    for (let x = 0; x <= w; x += 5) pts.push([x, HZ - ridge(x)]);
    c.fillUnder(pts, HZ, '#22064a');
    c.polyline(pts.map((p) => [p[0], p[1] + 0.5]), 7, withAlpha(C.cyan, 0.10));
    c.polyline(pts, 3, withAlpha(C.cyan, 0.30));
    c.polyline(pts, 1.6, C.cyan);
    // ground
    c.gradientRect(0, HZ, w, h - HZ, [[0, '#8c1478'], [0.16, '#2a0058'], [1, '#10002a']]);
    // grid lines running to the vanishing point
    for (let k = -14; k <= 14; k++) {
        const dx = k * 92, span = (h - HZ);
        let yEnd = h, xEnd = cx + dx;
        if (Math.abs(dx) > cx) { yEnd = HZ + span * cx / Math.abs(dx); xEnd = cx + Math.sign(dx) * cx; }
        c.line(cx, HZ, xEnd, yEnd, 4.5, withAlpha(C.pink, 0.10));
        c.line(cx, HZ, xEnd, yEnd, 1.6, withAlpha(C.pink, k === 0 ? 0.95 : 0.7));
    }
    // horizon glow line
    c.line(0, HZ, w, HZ, 7, withAlpha('#ff9ae6', 0.22));
    c.line(0, HZ, w, HZ, 2.2, '#ffd2f4');
    drawCar(c, cx, 438);
}

/** A car seen from behind: a low wide body, a dark glass roof line, two pink tail lamps. An original silhouette. */
function drawCar(c, cx, base) {
    const P = (pts) => pts.map(([x, y]) => [cx + x, base + y]);
    c.circle(cx, base - 26, 120, withAlpha('#ff2aa0', 0.07));
    const body = P([[-100, 0], [-104, -18], [-92, -38], [-62, -52], [-46, -74], [46, -74], [62, -52], [92, -38], [104, -18], [100, 0]]);
    fillPoly(c, body, '#18042f');
    const glass = P([[-44, -52], [-34, -70], [34, -70], [44, -52]]);
    fillPoly(c, glass, '#0a0120');
    c.polyline(body.concat([body[0]]), 4, withAlpha(C.pink, 0.16));
    c.polyline(body.concat([body[0]]), 1.8, C.pink);
    c.polyline(glass.concat([glass[0]]), 1.4, withAlpha(C.cyan, 0.8));
    // tail lamps: a glowing bar each side of the boot
    [[-86, -30, -36, -30], [36, -30, 86, -30]].forEach((l) => {
        c.line(cx + l[0], base + l[1], cx + l[2], base + l[3], 15, withAlpha(C.red, 0.15));
        c.line(cx + l[0], base + l[1], cx + l[2], base + l[3], 8, withAlpha(C.red, 0.45));
        c.line(cx + l[0], base + l[1], cx + l[2], base + l[3], 4, '#ff6a8a');
    });
    c.roundRect(cx - 24, base - 22, 48, 14, 3, '#0a0120');
    c.strokeRoundRect(cx - 24, base - 22, 48, 14, 3, 1.4, withAlpha(C.cyan, 0.8));
    c.line(cx - 96, base + 2, cx + 96, base + 2, 5, withAlpha(C.pink, 0.25));
}


/** A polygon: the kit's fill() where the recorder has it, else a fan of quads (every polygon here is convex). */
function fillPoly(cv, pts, color) {
    if (cv.fill) return cv.fill(pts, color);
    for (let i = 1; i < pts.length - 1; i++) cv.quad([pts[0], pts[i], pts[i + 1], pts[i + 1]], color);
    return cv;
}

/* ---------- Lambo look (after konsti_m440i's cluster): carbon honeycomb, glass panels, blue to orange to red ---------- */
const L = { bg: '#03060a', glass: '#101c2c', edge: '#d6e8ff', blue: '#28a0ff', mblue: '#1848be', red: '#ff2828', orange: '#ff961e', white: '#f4f7fc', dim: '#96b0cc', hex: '#7896be' };

/** a glass panel with its corners cut (cut: tl, tr, br, bl px) and a bright, glowing edge */
function glass(cv, p, cut) {
    const x = p.x, y = p.y, w = p.w, h = p.h, c = cut || [0, 0, 0, 0];
    const pts = [[x + c[0], y], [x + w - c[1], y], [x + w, y + c[1]], [x + w, y + h - c[2]], [x + w - c[2], y + h], [x + c[3], y + h], [x, y + h - c[3]], [x, y + c[0]]];
    const ring = (wd, a, col) => cv.polyline(pts.concat([pts[0]]), wd, withAlpha(col, a));
    fillPoly(cv, pts, withAlpha(L.glass, 0.92));
    ring(9, 0.10, L.blue); ring(5, 0.18, L.blue); ring(2, 1, L.edge);
}

/** the honeycomb (a cached layer, drawn once): zig-zag rows and the short links between them */
function drawHoneycomb(c, w, h) {
    c.fillRect(0, 0, w, h, L.bg);
    const a = 15, dx = a * 0.866 * 2, col = withAlpha(L.hex, 0.22);
    for (let row = 0; row * a * 1.5 < h + a; row++) {
        const y0 = row * a * 1.5, off = (row % 2) * dx / 2;
        const pts = [];
        for (let x = -dx + off; x < w + dx; x += dx / 2) { const up = Math.round((x - off) / (dx / 2)) % 2 === 0; pts.push([x, y0 + (up ? 0 : a * 0.5)]); }
        c.polyline(pts, 1, col);
        for (let x = -dx + off; x < w + dx; x += dx) c.line(x, y0 + a * 0.5, x, y0 + a * 1.5, 1, col);
    }
}

class SynthDash {
    /** car: the kit's Car (data(): rpm, speed, gLat, gLong, oil, coolant, gear, torque, demo); get(key): the app's setting. */
    constructor(car, get, set) {
        this.car = car; this.get = get; this.setting = set || function () {};
        this.newSession();
        this.shown = { lat: 0, long: 0 };
        this.phase = 0; this.lastT = 0; this.smooth = [];
    }

    newSession() { this.S = { vmax: 0, rpmMax: 0, gMax: 0, trail: [] }; this.smooth = []; }
    mph() { return this.get('units') === 'us'; }

    /** Feed this frame's car data into the session bests and the g blip (a 150 ms average, as G-Force does). */
    sample(d, now) {
        const S = this.S;
        if (isNum(d.speed)) S.vmax = Math.max(S.vmax, d.speed);
        if (isNum(d.rpm)) S.rpmMax = Math.max(S.rpmMax, d.rpm);
        if (!isNum(d.gLong) || Math.abs(d.gLong) > 3 || (isNum(d.gLat) && Math.abs(d.gLat) > 3)) return;
        const lat0 = isNum(d.gLat) ? (this.get('gFlipLat') === true ? -d.gLat : d.gLat) : 0;
        this.smooth.push([now, lat0, d.gLong]);
        while (this.smooth.length && now - this.smooth[0][0] > 150) this.smooth.shift();
        const n = this.smooth.length;
        const lat = this.smooth.reduce((a, v) => a + v[1], 0) / n, lon = this.smooth.reduce((a, v) => a + v[2], 0) / n;
        this.cur = { lat, long: lon };
        S.gMax = Math.max(S.gMax, Math.sqrt(lat * lat + lon * lon));
        S.trail.push([now, lat, lon]);
        while (S.trail.length && now - S.trail[0][0] > 3000) S.trail.shift();
    }

    /** The whole dash into cv (the page's 1600 x 520): panels from y 44 to 512. back(): leave the dash. */
    draw(cv, back) {
        const now = Date.now(), dt = this.lastT ? Math.min(250, now - this.lastT) : 16;
        this.lastT = now;
        const d = this.car.data();
        this.sample(d, now);
        const c = this.cur || { lat: 0, long: 0 };
        this.shown.lat += (c.lat - this.shown.lat) * 0.3; this.shown.long += (c.long - this.shown.long) * 0.3;
        if (this.get('dashStyle') === 'synthwave') {
            this.vitals(cv, d);
            this.scenePanel(cv, d, dt, back);
            this.radar(cv, now);
        } else if (this.get('dashStyle') === 'chrome') {
            this.chrome(cv, d, back);
        } else {
            this.lambo(cv, d, back);
        }
        this.styleButton(cv);
    }

    /** the little switch between the two looks, bottom middle */
    styleButton(cv) {
        const st = this.get('dashStyle'), bx = PB.x + PB.w - 146, by = PB.y + PB.h - 44;
        const col = st === 'synthwave' ? C.cyan : st === 'chrome' ? '#e4e4de' : '#28a0ff';
        const name = st === 'synthwave' ? 'SYNTHWAVE' : st === 'chrome' ? 'CHROM' : 'LAMBO';
        const nxt = st === 'synthwave' ? 'chrome' : st === 'chrome' ? 'lambo' : 'synthwave';
        cv.roundRect(bx, by, 132, 32, 8, withAlpha('#000000', 0.55));
        cv.strokeRoundRect(bx, by, 132, 32, 8, 1.5, withAlpha(col, 0.8));
        T(cv, 'STIL: ' + name, bx + 66, by + 22, 14, col, { font: 'bold', spacing: 0.5, align: 'center' });
        if (cv.target) cv.target(bx, by, 132, 32, () => this.setting('dashStyle', nxt), 'dash-style', 8);
    }

    /**
     * Chrom: three round analogue dials with brushed chrome bezels, white bar ticks and slim needles (the cluster's
     * "Chrom" theme): left the power reserve (full at idle) with the oil temperature, middle the speedometer with the
     * range, right fuel (E-F) and coolant (C-H) with the clock and the gear. The faces are cached layers.
     */
    chrome(cv, d, back) {
        const mph = this.mph(), V = (k) => (isNum(k) ? (mph ? k / MPH : k) : null);
        cv.fillRect(0, 0, 1600, 520, '#08080a');
        cv.gradientRect && cv.gradientRect(0, 0, 1600, 520, '#14141a', '#050506');
        const rad = (a) => a * Math.PI / 180;
        const pt = (cx, cy, a, r) => [cx + r * Math.sin(rad(a)), cy - r * Math.cos(rad(a))];
        const needle = (cx, cy, a, len) => {
            const tip = pt(cx, cy, a, len), tail = pt(cx, cy, a + 180, len * 0.16);
            const l = pt(cx, cy, a - 90, 4.2), r = pt(cx, cy, a + 90, 4.2);
            fillPoly(cv, [l, tip, r, tail], '#ecece8');
            cv.line(cx, cy, tip[0], tip[1], 1.5, '#ffffff');
        };
        const dial = (cx, cy, R, key, spec) => {
            const layer = G.layer('chrome-' + key + (mph ? 'm' : 'k'), 2 * R, 2 * R, (c) => {
                const o = R, bw = Math.round(R * 0.085), rin = R - bw;
                for (let a = 0; a < 360; a += 4) {                      // the brushed bezel: bright top-left, dark bands
                    const t = 0.5 + 0.5 * Math.cos(rad(a - 315)), b = 0.5 + 0.5 * Math.sin(rad(a * 3 + 40));
                    c.arc(o, o, rin, R - 1, a, a + 4.5, lerpHex('#4c4c50', '#f4f4f0', clamp(0.2 + 0.6 * t + 0.2 * b, 0, 1)));
                }
                c.arc(o, o, rin, rin + 2, 0, 360, '#ffffff');
                c.arc(o, o, 0, rin, 0, 360, '#0b0b0d');
                c.arc(o, o, rin * 0.62, rin, 0, 360, withAlpha('#000000', 0.25));
                const tr = rin * 0.93;
                spec.scales.forEach((sc) => {
                    const steps = sc.n * sc.minor;
                    for (let k = 0; k <= steps; k++) {
                        const a = sc.start + k * sc.sweep / steps, major = k % sc.minor === 0;
                        const p0 = pt(o, o, a, tr - (major ? tr * 0.115 : tr * 0.06)), p1 = pt(o, o, a, tr);
                        c.line(p0[0], p0[1], p1[0], p1[1], major ? R * 0.012 + 1 : R * 0.006 + 1, '#f0f0ec');
                    }
                    (sc.labels || []).forEach((lb, i) => {
                        const q = pt(o, o, sc.start + i * sc.sweep / (sc.labels.length - 1), tr * (sc.lr || 0.72));
                        T(c, lb, q[0], q[1] + spec.size * 0.35, spec.size, '#f0f0ec', { font: 'num', align: 'center' });
                    });
                });
            });
            cv.blit(layer, cx - R, cy - R);
        };
        const hub = (cx, cy, r) => {
            cv.arc(cx, cy, 0, r, 0, 360, '#9a9a98');
            cv.arc(cx, cy, 0, r * 0.7, 0, 360, '#dcdcd8');
            cv.arc(cx, cy, r, r + 1.5, 0, 360, '#ffffff');
        };
        const lab = (s, x, y, size, col, al) => T(cv, s, x, y, size, col || '#a8a8a4', { font: 'bold', align: al || 'center', spacing: 0.5 });

        // middle: speedometer 0-260 km/h (0-160 mph)
        const SX = 800, SY = 280, SR = 232, mx = mph ? 160 : 260, nn = mph ? 8 : 13;
        const labs = []; for (let i = 0; i <= nn; i++) labs.push(String(Math.round(mx / nn * i)));
        dial(SX, SY, SR, 'speed', { size: 28, scales: [{ start: -140, sweep: 280, n: nn, minor: 4, labels: labs, lr: 0.73 }] });
        const sp = isNum(d.speed) ? clamp(V(d.speed) / mx, 0, 1) : 0;
        needle(SX, SY, -140 + sp * 280, SR * 0.8);
        hub(SX, SY, 16);
        lab(mph ? 'MPH' : 'KM/H', SX, SY + 78, 18);
        lab(isNum(d.range) ? Math.round(V(d.range)) + (mph ? ' MI' : ' KM') : '-', SX, SY + 140, 22, '#f0f0ec');

        // left: power reserve 0-100
        const LX = 290, LY = 290, LR = 168, pw = isNum(d.powerPct) ? clamp(d.powerPct, 0, 100) : 0;
        dial(LX, LY, LR, 'reserve', { size: 22, scales: [{ start: -140, sweep: 230, n: 5, minor: 4, labels: ['0', '20', '40', '60', '80', '100'], lr: 0.63 }] });
        needle(LX, LY, -140 + (1 - pw / 100) * 230, LR * 0.8);
        hub(LX, LY, 12);
        lab('POWER', LX, LY + 56, 14);
        lab('OIL ' + fmt(temp(d.oil, mph), 0) + (mph ? '°F' : '°C'), LX, LY + 100, 17, '#f0f0ec');

        // right: fuel E-F (left half) and coolant C-H (right half), clock and gear
        const RX = 1310, RY = 290, RR = 168, fu = isNum(d.fuel) ? clamp(d.fuel, 0, 1) : 0;
        const cl = isNum(d.coolant) ? clamp((d.coolant - 40) / 90, 0, 1) : 0;
        dial(RX, RY, RR, 'fuel', { size: 22, scales: [{ start: -150, sweep: 100, n: 4, minor: 2 }, { start: 50, sweep: 100, n: 4, minor: 2 }] });
        [['E', -150], ['F', -50], ['C', 50], ['H', 150]].forEach((e) => { const q = pt(RX, RY, e[1], RR * 0.6); lab(e[0], q[0], q[1] + 7, 20, '#f0f0ec'); });
        needle(RX, RY, -150 + fu * 100, RR * 0.78);
        needle(RX, RY, 50 + cl * 100, RR * 0.78);
        hub(RX, RY, 11);
        lab('FUEL', RX - 40, RY - 20, 13); lab('TEMP', RX + 40, RY - 20, 13);
        const now = new Date(), hh = (now.getHours() < 10 ? '0' : '') + now.getHours(), mm = (now.getMinutes() < 10 ? '0' : '') + now.getMinutes();
        lab(hh + ':' + mm, RX, RY + 52, 20, '#f0f0ec');
        const g = isNum(d.gear) ? (d.gear > 0 ? 'D' + d.gear : d.gear === 0 ? 'N' : 'R') : 'D';
        cv.roundRect(RX - 30, RY + 76, 60, 40, 5, '#3cc46e');
        T(cv, g, RX, RY + 106, 28, '#0c0c0e', { font: 'bold', align: 'center' });
        const bx = PB.x + 14, by = PB.y + PB.h - 44;
        cv.roundRect(bx, by, 132, 32, 8, withAlpha('#000000', 0.55));
        cv.strokeRoundRect(bx, by, 132, 32, 8, 1.5, withAlpha('#e4e4de', 0.8));
        T(cv, '<  ZURÜCK', bx + 66, by + 22, 14, '#e4e4de', { font: 'bold', spacing: 0.5, align: 'center' });
        if (cv.target && back) cv.target(bx, by, 132, 32, back, 'dash-back', 8);
    }

    lambo(cv, d, back) {
        const mph = this.mph(), V = (k) => (isNum(k) ? (mph ? k / MPH : k) : null), S = this.S;
        cv.blit(G.layer('lambo-bg', 1600, 520, (c) => drawHoneycomb(c, 1600, 520)), 0, 0);
        // rail along the top, like the cluster's
        cv.polyline([[14, 520], [24, 150], [110, 66], [520, 40], [800, 36], [1080, 40], [1490, 66], [1576, 150], [1586, 520]], 2, withAlpha(L.edge, 0.5));
        glass(cv, PA, [0, 0, 34, 0]); glass(cv, PB, [34, 34, 34, 34]); glass(cv, PC, [0, 0, 0, 34]);

        // left: the engine's vitals with segmented bars
        const x = PA.x + 28, r = PA.x + PA.w - 28;
        T(cv, 'ENGINE', x, PA.y + 46, 20, L.blue, { font: 'bold', spacing: 3 });
        const rows = [
            [mph ? 'SPEED  MPH' : 'SPEED  KM/H', V(d.speed), 0, mph ? 160 : 260],
            ['RPM', d.rpm, 0, 7000],
            [mph ? 'OIL  °F' : 'OIL  °C', temp(d.oil, mph), mph ? 100 : 40, mph ? 280 : 140],
            [mph ? 'COOLANT  °F' : 'COOLANT  °C', temp(d.coolant, mph), mph ? 100 : 40, mph ? 270 : 130],
            ['TORQUE  NM', d.torque, 0, 500],
        ];
        rows.forEach(([label, v, lo, hi], i) => {
            const y = PA.y + 96 + i * 52;
            T(cv, label, x, y, 16, L.dim, { font: 'bold', spacing: 1.5 });
            T(cv, fmt(v, 0), r, y + 6, 36, isNum(v) ? L.white : withAlpha(L.white, 0.35), { font: 'num', align: 'right' });
            this.segs(cv, x, y + 14, r - x, 9, isNum(v) ? clamp((v - lo) / (hi - lo), 0, 1) : 0, 26);
        });
        const by = PA.y + 96 + 5 * 52 + 10;
        T(cv, 'BEST', x, by + 12, 16, L.blue, { font: 'bold', spacing: 3 });
        T(cv, 'ZURÜCKSETZEN', r, by + 12, 13, L.dim, { font: 'bold', spacing: 1, align: 'right' });
        if (cv.target) cv.target(r - 170, by - 12, 170, 36, () => this.newSession(), 'dash-reset', 8);
        [['TOP ' + (mph ? 'MPH' : 'KM/H'), fmt(V(S.vmax), 0)], ['MAX RPM', fmt(S.rpmMax, 0)], ['MAX G', S.gMax > 0.005 ? S.gMax.toFixed(2) : '-.--']].forEach(([l, v], i) => {
            const cx0 = x + i * 146;
            T(cv, l, cx0, by + 40, 13, L.dim, { font: 'bold', spacing: 1 });
            T(cv, v, cx0, by + 70, 28, v === '--' || v === '-.--' ? withAlpha(L.white, 0.35) : L.white, { font: 'num' });
        });

        // middle: the rev arc with 0-7 inside, the hollow gear, the speed
        const cx = PB.x + PB.w / 2, cy = PB.y + 392, R0 = 292, R1 = 244, A0 = -62, SW = 124, N = 30;
        const rpm = isNum(d.rpm) ? clamp(d.rpm / 7000, 0, 1) : 0;
        for (let i = 0; i < N; i++) {
            const f = (i + 0.5) / N, a = A0 + SW * i / N, a2 = A0 + SW * (i + 1) / N - 1.6;
            const lit = f <= rpm, t = rpm > 0.02 ? Math.min(1, f / rpm) : 0;
            // as the cluster: blue running to pale blue while lit, grey when not, the orange and red zones always in colour
            const col = f > 0.87 ? '#d82a26' : f > 0.70 ? '#ec9a1e' : lit ? lerpHex('#2e9be6', '#d8e6f2', Math.pow(t, 1.4)) : '#9a9ea4';
            cv.arc(cx, cy, R1, R0, a, a2, col);
        }
        for (let k = 0; k < 8; k++) {
            const a = (A0 + SW * k / 7) * Math.PI / 180, rr = R1 - 26;
            T(cv, String(k), cx + Math.sin(a) * rr, cy - Math.cos(a) * rr + 9, 22, k >= 6 ? L.red : L.white, { font: 'num', align: 'center' });
        }
        T(cv, 'RPM X 1000', PB.x + 40, PB.y + PB.h - 62, 12, L.dim, { font: 'bold', spacing: 1 });
        const g = isNum(d.gear) ? (d.gear > 0 ? String(d.gear) : d.gear === 0 ? 'N' : 'R') : '-';
        const gy = PB.y + 268;
        [[-3, 0], [3, 0], [0, -3], [0, 3], [-2.2, -2.2], [2.2, 2.2], [-2.2, 2.2], [2.2, -2.2]].forEach((o) => T(cv, g, cx + o[0], gy + o[1], 124, L.red, { font: 'bold', align: 'center' }));
        T(cv, g, cx, gy, 124, L.glass, { font: 'bold', align: 'center' });
        T(cv, fmt(V(d.speed), 0), cx, PB.y + 356, 76, L.white, { font: 'num', align: 'center' });
        T(cv, mph ? 'MPH' : 'KM/H', cx, PB.y + 384, 16, L.dim, { font: 'bold', spacing: 2, align: 'center' });
        [[L.blue, 0], [L.mblue, 1], [L.red, 2]].forEach(([c, i]) => cv.fillRect(cx - 78 + i * 52, PB.y + 396, 52, 5, c));
        const bx = PB.x + 14, byy = PB.y + PB.h - 44;
        cv.roundRect(bx, byy, 132, 32, 8, withAlpha('#000000', 0.55));
        cv.strokeRoundRect(bx, byy, 132, 32, 8, 1.5, withAlpha(L.blue, 0.8));
        T(cv, '<  ZURÜCK', bx + 66, byy + 22, 14, L.blue, { font: 'bold', spacing: 0.5, align: 'center' });
        if (cv.target && back) cv.target(bx, byy, 132, 32, back, 'dash-back', 8);

        // right: the G-meter
        const gx = PC.x + PC.w / 2, gyy = PC.y + 232, gr = 126, max = Number(this.get('gRange')) || 1.2;
        T(cv, 'G-FORCE', PC.x + 28, PC.y + 46, 20, L.blue, { font: 'bold', spacing: 3 });
        const comb = Math.sqrt(this.shown.lat * this.shown.lat + this.shown.long * this.shown.long);
        T(cv, comb.toFixed(2) + ' G', PC.x + PC.w - 28, PC.y + 50, 28, comb > 0.9 ? L.red : L.white, { font: 'num', align: 'right' });
        [1 / 3, 2 / 3, 1].forEach((f, i) => cv.arc(gx, gyy, gr * f - 1.3, gr * f + 1.3, 0, 360, withAlpha(L.edge, i === 2 ? 0.9 : 0.35)));
        cv.line(gx - gr, gyy, gx + gr, gyy, 1, withAlpha(L.edge, 0.35)); cv.line(gx, gyy - gr, gx, gyy + gr, 1, withAlpha(L.edge, 0.35));
        const flipLong = this.get('gFlipLong') === true, ySign = flipLong ? 1 : -1;
        T(cv, flipLong ? 'BRAKE' : 'ACCEL', gx, gyy - gr - 14, 13, L.dim, { font: 'bold', align: 'center', spacing: 2 });
        T(cv, flipLong ? 'ACCEL' : 'BRAKE', gx, gyy + gr + 26, 13, L.dim, { font: 'bold', align: 'center', spacing: 2 });
        const P = (lat, lon) => [gx - clamp(lat / max, -1.05, 1.05) * gr, gyy + ySign * clamp(lon / max, -1.05, 1.05) * gr];
        const tr = S.trail, n = tr.length;
        tr.forEach((sm, i) => { if (i % 2) return; const p = P(sm[1], sm[2]); cv.circle(p[0], p[1], 3.5, withAlpha(L.blue, 0.08 + 0.5 * (i / n))); });
        const bp = P(this.shown.lat, this.shown.long);
        cv.circle(bp[0], bp[1], 20, withAlpha(L.red, 0.18)); cv.circle(bp[0], bp[1], 11, withAlpha(L.red, 0.5)); cv.circle(bp[0], bp[1], 6, L.red); cv.circle(bp[0], bp[1], 2.5, L.white);
        T(cv, 'TORQUE  NM', PC.x + 28, PC.y + PC.h - 56, 14, L.dim, { font: 'bold', spacing: 1.5 });
        T(cv, fmt(d.torque, 0), PC.x + PC.w - 28, PC.y + PC.h - 50, 30, L.white, { font: 'num', align: 'right' });
        this.segs(cv, PC.x + 28, PC.y + PC.h - 36, PC.w - 56, 9, isNum(d.torque) ? clamp(d.torque / 500, 0, 1) : 0, 26);
    }

    /** a segmented bar: n segments, the first f of it lit, blue to orange to red */
    segs(cv, x, y, w, h, f, n) {
        const gap = 3, sw = (w - gap * (n - 1)) / n;
        for (let i = 0; i < n; i++) {
            const p = (i + 0.5) / n, lit = p <= f;
            cv.fillRect(x + i * (sw + gap), y, sw, h, lit ? (p > 0.85 ? L.red : p > 0.62 ? L.orange : L.blue) : withAlpha('#ffffff', 0.12));
        }
    }

    vitals(cv, d) {
        const S = this.S, mph = this.mph(), V = (k) => (isNum(k) ? (mph ? k / MPH : k) : null);
        panelFrame(cv, PA, C.pink);
        const x = PA.x + 26, r = PA.x + PA.w - 26;
        T(cv, 'VITALS', x, PA.y + 52, 28, C.pink, { font: 'bold', spacing: 4 });
        cv.line(x, PA.y + 66, r, PA.y + 66, 2, withAlpha(C.pink, 0.6));
        const rows = [
            [mph ? 'SPEED  MPH' : 'SPEED  KM/H', V(d.speed), 0, mph ? 160 : 260],
            ['RPM', d.rpm, 0, 7000],
            [mph ? 'OIL  °F' : 'OIL  °C', temp(d.oil, mph), mph ? 100 : 40, mph ? 280 : 140],
            [mph ? 'COOLANT  °F' : 'COOLANT  °C', temp(d.coolant, mph), mph ? 100 : 40, mph ? 270 : 130],
            ['TORQUE  NM', d.torque, 0, 500],
        ];
        rows.forEach(([label, v, lo, hi], i) => {
            const y = PA.y + 108 + i * 50;
            T(cv, label, x, y, 19, C.violet, { font: 'bold', spacing: 1.5 });
            T(cv, fmt(v, 0), r, y + 6, 40, isNum(v) ? C.cyan : withAlpha(C.cyan, 0.35), { font: 'num', align: 'right' });
            const f = isNum(v) ? clamp((v - lo) / (hi - lo), 0, 1) : 0;
            cv.fillRect(x, y + 14, r - x, 5, withAlpha('#ffffff', 0.10));
            if (f > 0.004) cv.gradientRect(x, y + 14, (r - x) * f, 5, [[0, C.cyan], [1, f > 0.85 ? C.red : C.pink]]);
        });
        const by = PA.y + 108 + 5 * 50 + 12;
        T(cv, 'BESTWERTE', x, by, 19, C.pink, { font: 'bold', spacing: 3 });
        cv.line(x, by + 10, r, by + 10, 1.5, withAlpha(C.pink, 0.45));
        // tap the heading's right end to start the bests again
        T(cv, 'ZURÜCKSETZEN', r, by, 15, C.violet, { font: 'bold', spacing: 1, align: 'right' });
        if (cv.target) cv.target(r - 170, by - 24, 170, 40, () => this.newSession(), 'dash-reset', 8);
        const cols = [['TOP ' + (mph ? 'MPH' : 'KM/H'), fmt(V(S.vmax), 0)], ['MAX RPM', fmt(S.rpmMax, 0)], ['MAX G', S.gMax > 0.005 ? S.gMax.toFixed(2) : '-.--']];
        cols.forEach(([l, v], i) => {
            const cx0 = x + i * 148;
            T(cv, l, cx0, by + 38, 16, C.violet, { font: 'bold', spacing: 1 });
            T(cv, v, cx0, by + 74, 34, v === '--' || v === '-.--' ? withAlpha(C.cyan, 0.35) : C.cyan, { font: 'num' });
        });
    }

    scenePanel(cv, d, dt, back) {
        const mph = this.mph(), V = (k) => (isNum(k) ? (mph ? k / MPH : k) : null);
        panelFrame(cv, PB, C.pink);
        const ox = PB.x + 3, oy = PB.y + 3, w = PB.w - 6, h = PB.h - 6;
        cv.blit(G.layer('synth-scene', w, h, (c) => drawScene(c, w, h)), ox, oy);
        // the cross lines run towards you: faster with the speed, slowly when standing
        const spd = isNum(d.speed) ? Math.max(0, d.speed) : 0;
        this.phase = (this.phase + dt / 1000 * (0.12 + spd * 0.011)) % 1;
        const N = 9, span = h - HZ;
        for (let i = 0; i < N; i++) {
            const f = (i + 1 - this.phase) / N;
            if (f <= 0.02) continue;
            const y = oy + HZ + span * Math.pow(f, 2.2);
            cv.line(ox, y, ox + w, y, 5, withAlpha(C.pink, 0.10 * f + 0.04));
            cv.line(ox, y, ox + w, y, 1 + 1.4 * f, withAlpha(C.pink, 0.25 + 0.6 * f));
        }
        T(cv, fmt(V(d.speed), 0), PB.x + 34, PB.y + 120, 78, C.white, { font: 'num' });
        T(cv, mph ? 'MPH' : 'KM/H', PB.x + 38, PB.y + 152, 20, C.violet, { font: 'bold', spacing: 2 });
        const gtxt = isNum(d.gear) ? (d.gear > 0 ? 'D' + d.gear : d.gear === 0 ? 'N' : 'R') : 'D';
        T(cv, gtxt, PB.x + PB.w - 34, PB.y + 120, 78, C.pink, { font: 'num', align: 'right' });
        T(cv, 'GEAR', PB.x + PB.w - 38, PB.y + 152, 20, C.violet, { font: 'bold', spacing: 2, align: 'right' });
        T(cv, 'SYNTHWAVE', PB.x + PB.w / 2, PB.y + 52, 22, withAlpha(C.violet, 0.9), { font: 'bold', spacing: 6, align: 'center' });
        // back to the page's tabs
        const bx = PB.x + 14, by = PB.y + PB.h - 44;
        cv.roundRect(bx, by, 132, 32, 8, withAlpha('#000000', 0.55));
        cv.strokeRoundRect(bx, by, 132, 32, 8, 1.5, withAlpha(C.cyan, 0.8));
        T(cv, '<  ZURÜCK', bx + 66, by + 22, 14, C.cyan, { font: 'bold', spacing: 0.5, align: 'center' });
        if (cv.target && back) cv.target(bx, by, 132, 32, back, 'dash-back', 8);
    }

    radar(cv, now) {
        const S = this.S;
        panelFrame(cv, PC, C.cyan);
        const cx = PC.x + PC.w / 2, cy = PC.y + 250, r = 148, max = Number(this.get('gRange')) || 1.2;
        T(cv, 'G-RADAR', PC.x + 26, PC.y + 52, 28, C.cyan, { font: 'bold', spacing: 4 });
        cv.line(PC.x + 26, PC.y + 66, PC.x + PC.w - 26, PC.y + 66, 2, withAlpha(C.cyan, 0.6));
        cv.circle(cx, cy, r + 8, withAlpha('#001a30', 0.9));
        [1 / 3, 2 / 3, 1].forEach((f, i) => {
            cv.arc(cx, cy, r * f - 2.5, r * f + 2.5, 0, 360, withAlpha(C.cyan, 0.10));
            cv.arc(cx, cy, r * f - 1, r * f + 1, 0, 360, withAlpha(C.cyan, i === 2 ? 0.9 : 0.55));
        });
        neonLine(cv, cx - r, cy, cx + r, cy, 1.4, withAlpha(C.cyan, 0.5));
        neonLine(cv, cx, cy - r, cx, cy + r, 1.4, withAlpha(C.cyan, 0.5));
        for (let a = 0; a < 360; a += 30) {
            const rad = a * Math.PI / 180, s = Math.sin(rad), co = Math.cos(rad);
            cv.line(cx + s * (r + 10), cy - co * (r + 10), cx + s * (r + 20), cy - co * (r + 20), a % 90 ? 1.5 : 3, withAlpha(C.cyan, 0.8));
        }
        const flipLong = this.get('gFlipLong') === true;
        T(cv, flipLong ? 'BRAKE' : 'ACCEL', cx, cy - r - 28, 16, C.violet, { font: 'bold', align: 'center', spacing: 2 });
        T(cv, flipLong ? 'ACCEL' : 'BRAKE', cx, cy + r + 36, 16, C.violet, { font: 'bold', align: 'center', spacing: 2 });
        const a = (now / 1000 * 100) % 360;
        for (let k = 0; k < 14; k++) cv.arc(cx, cy, 0, r, a - (k + 1) * 4, a - k * 4, withAlpha(C.cyan, 0.30 * (1 - k / 14)));
        const rad = a * Math.PI / 180;
        neonLine(cv, cx, cy, cx + Math.sin(rad) * r, cy - Math.cos(rad) * r, 2, C.cyan);
        // the blip: where the car's g points (left is drawn to the left, accel up unless swapped)
        const ySign = flipLong ? 1 : -1;
        const P = (lat, lon) => [cx - clamp(lat / max, -1.05, 1.05) * r, cy + ySign * clamp(lon / max, -1.05, 1.05) * r];
        const tr = S.trail, n = tr.length;
        tr.forEach((s, i) => { if (i % 2) return; const p = P(s[1], s[2]); cv.circle(p[0], p[1], 4, withAlpha(C.pink, 0.08 + 0.5 * (i / n))); });
        const b = P(this.shown.lat, this.shown.long);
        cv.circle(b[0], b[1], 22, withAlpha(C.pink, 0.18));
        cv.circle(b[0], b[1], 13, withAlpha(C.pink, 0.45));
        cv.circle(b[0], b[1], 7, C.pink);
        cv.circle(b[0], b[1], 3, C.white);
        const comb = Math.sqrt(this.shown.lat * this.shown.lat + this.shown.long * this.shown.long);
        T(cv, comb.toFixed(2) + ' G', PC.x + PC.w - 26, PC.y + 52, 30, comb > 0.9 ? C.pink : C.cyan, { font: 'num', align: 'right' });
    }
}

module.exports = { SynthDash };
