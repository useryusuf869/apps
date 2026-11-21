#!/usr/bin/env python3
"""gen_lambo.py - writes apps/cluster_themes/hud/layouts/lambo.json (edit here, then regenerate):

    python3 tools/gen_lambo.py

The "Lambo x BMW" cluster, 1:1 after konsti_m440i's reel (the bench photo, measured on the 1920x720 panel): a carbon
honeycomb, two glowing rails along the hood, four glass panels (the two big side panels follow the rev arc's outer edge),
a wedge-segment rev arc with the numbers 0-7 as outlines, a hollow red gear between the gear row 2 3 4 | 6 7 8, the speed
under it and the M stripe. The arc is centred at x 1010 as on the reel; BMW's black gear box (x 1406-1597, y 342-419)
covers a part of its red zone on the car, as it does the reel's right panel.
"""
import json, re, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTS = [os.path.join(ROOT, 'apps', 'yusuf_dash', 'hud', 'layouts', 'lambo.json')]
W = []


def add(**k):
    W.append(k)


CELL = {'l_gear': 159, 'l_speed': 84, 'l_num': 39, 'l_val': 36, 'l_tyre': 34, 'l_unit': 22, 'l_label': 25, 'l_head': 25,
        'l_big': 33, 'l_gears': 51, 'l_trip': 40, 'l_badge': 40}


def text(id, x, y, t, font, color, align='left', w=None, exact=False, **extra):
    """x, y: the text's anchor (left / centre / right edge, vertical centre) in target px."""
    h = CELL[font]
    # shrink the image to what the text needs (pixel memory): about a cell height per character, tokens as 4
    est = int(len(re.sub(r'\{\{[^}]*\}\}', 'XXXX', t)) * h * 0.88) + 10
    w = (w or 300) if exact else min(w or 300, max(est, 40))
    if align == 'left':
        w = min(w, 1920 - x)
    left = x if align == 'left' else x - w / 2 if align == 'center' else x - w
    d = dict(id=id, type='text', z=REGZ(left + w / 2), x=round(left), y=round(y - h / 2), w=w, h=h, text=t, font=font, color=color, align=align)
    d.update(extra)
    add(**d)


COLS = [480, 960, 1440]


def REGZ(cx):
    return 5 + sum(cx >= c for c in COLS)


def icon(id, name, cx, cy, s, color='blue'):
    add(id=id, type='icon', icon=name, z=REGZ(cx), x=round(cx - s / 2), y=round(cy - s / 2), w=s, h=s, color=color)


RULES = []


def rule(id, x0, x1, y):
    RULES.append(dict(x=x0, y=y, w=x1 - x0, h=2, color='sep'))


# ---------- geometry
CX, CY, R, BAND, A0, SW = 1010, 870, 728, 92, -59.0, 118.0
EDGE = 755                       # the side panels' edge, concentric with the arc


def on(theta, r=EDGE):
    a = math.radians(theta)
    return [round(CX + r * math.sin(a)), round(CY - r * math.cos(a))]


left_arc = [on(-t) for t in (37, 41, 45, 49, 53, 57, 62, 67)]
right_arc = [on(t) for t in (35, 39, 43, 47, 51, 55, 59, 64)]
PANELS = [
    dict(points=[[193, 202], [548, 209], [575, 237]] + left_arc + [[39, 582], [9, 557], [11, 363]]),                  # tyres, drivetrain, oil
    dict(points=right_arc + [[1870, 548], [1900, 521], [1900, 358], [1756, 223], [1468, 223]]),                       # power, valve, fuel, water
    dict(points=[[302, 112], [434, 89], [749, 97], [770, 124], [770, 157], [721, 188], [319, 182], [301, 165]]),      # trip
    dict(points=[[1262, 135], [1283, 115], [1563, 115], [1672, 137], [1672, 187], [1655, 201], [1281, 198], [1261, 152]]),   # badge
]
RAILS = [
    [[9, 296], [121, 137], [230, 86], [335, 63], [459, 46], [608, 41], [776, 40], [818, 95]],
    [[1213, 108], [1230, 58], [1267, 56], [1426, 68], [1575, 80], [1714, 118], [1813, 167], [1858, 237], [1903, 309]],
]
add(id='bg', type='lambo', **{'class': 'content'}, z=0, x=0, y=0, w=1920, h=720, panels=PANELS, rails=RAILS,
    band=[683, 447, 637, 52], dome=[600, 615, 45, 32], logo=[1300, 137, 66, 44])

# ---------- rev arc, its numbers
add(id='revs', type='lamboarc', **{'class': 'content'}, z=2, x=360, y=120, w=1320, h=420, center=[CX - 360, CY - 120], r=R, band=BAND,
    start=360 + A0, sweep=SW, segments=32, orangeAt=0.70, redAt=0.87, ticks=14)
for k in range(8):
    a = math.radians(A0 + SW * k / 7)
    r = 579
    text('n%d' % k, CX + r * math.sin(a), CY - r * math.cos(a), str(k), 'l_num', 'red' if k >= 6 else 'fg', 'center', w=60)
text('rpm_unit', 619, 528, 'RPM X 1000', 'l_label', 'fg', 'left')

# ---------- centre: the gear row, the gear, the speed, the M stripe
text('gears_lo', 782, 473, '234', 'l_gears', 'pale', 'center', w=260, spacing=24, exact=True)
text('gears_hi', 1228, 470, '678', 'l_gears', 'pale', 'center', w=260, spacing=24, exact=True)
text('gear', 1017, 388, '{{gearnum}}', 'l_gear', 'red', 'center', w=190, glow=True, hotWhen='now')
text('speed', 1017, 537, '{{speed}}', 'l_speed', 'fg', 'center', w=250, glow=True)
text('speed_unit', 1017, 597, '{{u:speed}}', 'l_label', 'fg', 'center', w=200)
for i, c in enumerate(['stripe1', 'blue', 'red']):
    RULES.append(dict(x=902 + i * 77, y=618, w=77, h=4, color=c))

# ---------- trip panel
icon('trip_i', 'gauge', 468, 109, 26)
text('trip_h', 498, 110, 'TRIP', 'l_head', 'fg')
for i, (cx, tok, lab) in enumerate([(383, '{{time}}', 'TIME'), (523, '{{range}}', '{{u:dist}}'), (652, '{{avgSpeed}}', 'AVG {{u:speed}}')]):
    text('trip_v%d' % i, cx, 142, tok, 'l_trip', 'fg', 'center', w=150)
    text('trip_l%d' % i, cx, 171, lab, 'l_label', 'fg', 'center', w=150)

# ---------- left panel: tyres, drivetrain, oil
icon('tyre_i', 'tyre', 232, 223, 32)
text('tyre_h', 263, 224, 'TYRES', 'l_head', 'fg')
for name, (cx, tx), cy in [('FL', (220, 272), 262), ('FR', (369, 419), 262), ('RL', (220, 272), 302), ('RR', (369, 419), 302)]:
    text('tp_' + name, cx, cy, '{{tyreP:%s}}' % name, 'l_tyre', 'fg', 'center', w=110)
    text('tt_' + name, tx, cy + 3, '{{tyreT:%s}}' % name, 'l_label', 'blue', 'left', w=70)
rule('sep1', 72, 466, 332)
icon('dt_i', 'drivetrain', 62, 361, 30)
text('dt_h', 91, 362, 'DRIVETRAIN', 'l_head', 'fg')
text('dt_v', 91, 393, 'RWD', 'l_big', 'red')
rule('sep2', 29, 379, 429)


BARS = []


def meter(id, x0, x1, ymid, signal, mn, mx, h=20, gap=1.5, n=50, conn=1):
    """a segmented bar, drawn inside the lambo shader (one effect layer for all six)"""
    BARS.append(dict(id=id, x=x0, y=ymid - h // 2, w=x1 - x0, h=h, signal=signal, min=mn, max=mx, segments=n, gap=gap))


icon('oil_i', 'oilcan', 54, 460, 28)
text('oil_l', 81, 460, 'OIL', 'l_head', 'fg')
text('oil_v', 270, 460, '{{oil}}', 'l_val', 'fg', 'right', w=120)
text('oil_u', 290, 462, '{{u:temp}}', 'l_unit', 'fg')
meter('oil_m', 37, 327, 485, 'oil', 40, 150)
text('in_l', 37, 529, 'INTAKE', 'l_head', 'fg')
text('in_v', 270, 527, '{{intake}}', 'l_val', 'fg', 'right', w=120)
text('in_u', 290, 529, '{{u:temp}}', 'l_unit', 'fg')
meter('in_m', 34, 291, 557, 'intake', 0, 80, n=46)

# ---------- right panel: power / torque, the free readout, fuel, water
icon('pw_i', 'engine', 1481, 240, 28)
text('pw_h', 1503, 240, 'POWER / TORQUE', 'l_head', 'fg')
for i, (tok, unit, sig) in enumerate([('{{power}}', 'kW', 'powerPct'), ('{{torque}}', '{{u:torque}}', 'torquePct')]):
    y = 274 + i * 36
    text('pw%d_v' % i, 1622, y, tok, 'l_tyre', 'fg', 'right', w=100)
    text('pw%d_u' % i, 1630, y + 2, unit, 'l_unit', 'fg', w=50)
    meter('pw%d_m' % i, 1674, 1776, y + 1, sig, 0, 100, h=17, n=26)
rule('sep3', 1530, 1853, 336)
icon('ex_i', 'exhaust', 1580, 361, 28)
text('slot1_head', 1602, 363, '{{slotHead:1}}', 'l_head', 'fg')
text('slot1', 1607, 391, '{{slot:1}}{{slotSuffix:1}} {{slotUnit:1}}', 'l_big', 'blue', slot='1', fit=['l_head'], w=260)
rule('sep4', 1602, 1888, 419)
icon('fu_i', 'fuel', 1660, 445, 26)
text('fu_l', 1682, 445, 'FUEL', 'l_head', 'fg')
text('fu_v', 1854, 444, '{{fuelPct}}', 'l_tyre', 'fg', 'right', w=100)
text('fu_u', 1863, 447, '%', 'l_unit', 'fg', w=30)
meter('fu_m', 1647, 1880, 470, 'fuel', 0, 1, n=46)
icon('wa_i', 'therm', 1664, 505, 26)
text('wa_l', 1686, 507, 'WATER', 'l_head', 'fg')
text('wa_v', 1854, 505, '{{coolant}}', 'l_tyre', 'fg', 'right', w=70)
text('wa_u', 1863, 508, '{{u:temp}}', 'l_unit', 'fg', w=40)
meter('wa_m', 1677, 1880, 532, 'coolant', 40, 130, n=40)

# ---------- the model badge, right of the stripes
text('badge', 1490, 162, '{{badge}}', 'l_badge', 'fg', 'center', w=250)


# keep text/icon boxes from overlapping (overlaps force extra sheets = extra cluster layers):
# trim the empty side of a box, else move the later one to a second sheet group
def _hit(a, b):
    return a['x'] < b['x'] + b['w'] and b['x'] < a['x'] + a['w'] and a['y'] < b['y'] + b['h'] and b['y'] < a['y'] + a['h']

_T = [w for w in W if w['type'] in ('text', 'icon')]
for _i, a in enumerate(_T):
    for b in _T[:_i]:
        if a['z'] != b['z'] or not _hit(a, b):
            continue
        ovx = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
        ovy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
        if ovy <= 6:  # a sliver of padding: shave half off each box
            for q, sg in ((a, 1), (b, -1)):
                pass
            top, bot = (a, b) if a['y'] <= b['y'] else (b, a)
            top['h'] -= (ovy + 1) // 2
            bot['y'] += (ovy + 1) // 2
            bot['h'] -= (ovy + 1) // 2
            if not _hit(a, b):
                continue
        for q in (a, b):  # centred box: trim both sides
            o = b if q is a else a
            if q.get('align') == 'center' and ovx <= 40 and q['w'] - ovx >= 140:
                q['x'] += (ovx + 1) // 2
                q['w'] -= ovx + 1
                break
        if not _hit(a, b):
            continue
        if ovx <= 8:
            R0 = a if a['x'] >= b['x'] else b
            if R0.get('align', 'left') == 'left':
                R0['x'] += ovx
                R0['w'] -= ovx
                if not _hit(a, b):
                    continue
        L, R = (b, a) if b['x'] <= a['x'] else (a, b)
        if L.get('align', 'left') == 'left' and R['x'] - L['x'] >= 30:
            L['w'] = R['x'] - L['x']
        elif R.get('align') == 'right' and (L['x'] + L['w'] - R['x']) < R['w'] - 30:
            ov = L['x'] + L['w'] - R['x']
            R['x'] += ov
            R['w'] -= ov
        if _hit(a, b):
            a['z'] = 9 if a['z'] < 9 else a['z'] + 1

for w in W:
    if w.get('type') == 'lambo':
        w['bars'] = BARS
        w['rules'] = RULES

doc = {
    'schemaVersion': 2,
    'name': 'Lambo',
    'theme': 'lambo',
    'slots': [{'id': '1', 'where': 'right, middle', 'default': 'boost'}],
    '_about': "Lambo cluster, generated by tools/gen_lambo.py (edit that and regenerate): 1:1 after konsti_m440i's Lambo x BMW reel.",
    'widgets': W,
}
for out in OUTS:
    with open(out, 'w') as f:
        json.dump(doc, f, indent=2)
        f.write('\n')
print('wrote', len(OUTS), 'layouts,', len(W), 'widgets')
