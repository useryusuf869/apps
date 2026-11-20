#!/usr/bin/env python3
"""gen_lambo.py - writes apps/cluster_themes/hud/layouts/lambo.json (edit here, then regenerate):

    python3 tools/gen_lambo.py

The "Lambo x BMW" cluster after konsti_m440i's reel: a carbon honeycomb with a glowing rail along the hood and angled
glass panels (one "lambo" shader), a wide segmented rev arc (cold blue to orange to red) with the numbers 0-7 along
its inside, a hollow red gear, the speed under it, and the panels: trip, tyres, drivetrain / oil / intake on the
left; model badge, power and torque, fuel, water and one free readout on the right. The arc stops at +-43 degrees
so BMW's black gear box (x 1406-1597, y 342-419) and its belt light (x 587-626, y 663-700) stay clear.
"""
import json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'apps', 'cluster_themes', 'hud', 'layouts', 'lambo.json')
W = []


def add(**k):
    W.append(k)


def text(id, x, y, w, h, t, font, color, align='left', z=5, **extra):
    d = dict(id=id, type='text', z=z, x=x, y=y, w=w, h=h, text=t, font=font, color=color, align=align)
    d.update(extra)
    add(**d)


CELL = {'l_gear': 153, 'l_speed': 84, 'l_num': 34, 'l_val': 29, 'l_label': 18, 'l_head': 25, 'l_gears': 26}

# ---- background: honeycomb, rail, panels
PANELS = [
    dict(x=230, y=112, w=400, h=70, cut=[16, 16, 16, 16]),      # trip
    dict(x=70, y=200, w=400, h=150, cut=[20, 0, 34, 0]),        # tyres
    dict(x=30, y=362, w=440, h=215, cut=[0, 0, 40, 24]),        # drivetrain, oil, intake
    dict(x=1290, y=112, w=400, h=70, cut=[16, 16, 16, 16]),     # badge
    dict(x=1450, y=200, w=400, h=128, cut=[34, 0, 0, 20]),      # power, torque
    dict(x=1450, y=436, w=440, h=141, cut=[24, 0, 0, 40]),      # fuel, water, free readout
]
RAIL = [[4, 600], [12, 430], [38, 300], [70, 224], [100, 156], [200, 101], [300, 73], [400, 52], [500, 37], [600, 34], [700, 28], [800, 19], [806, 54]]
add(id='bg', type='lambo', **{'class': 'content'}, z=0, x=0, y=0, w=1920, h=720, panels=PANELS, rail=RAIL)

# ---- rev arc and its numbers
CX, CY, R, BAND, A0, SW = 960, 850, 700, 64, -43.0, 86.0
add(id='revs', type='revarc', **{'class': 'content'}, z=2, x=400, y=130, w=1120, h=300, center=[CX - 400, CY - 130], r=R, band=BAND,
    start=(360 + A0), sweep=SW, segments=32)
for k in range(8):
    a = math.radians(A0 + SW * k / 7)
    r = R - BAND - 36
    cx, cy = CX + r * math.sin(a), CY - r * math.cos(a)
    text('n%d' % k, round(cx - 24), round(cy - CELL['l_num'] / 2), 48, CELL['l_num'], str(k), 'l_num', 'red' if k >= 6 else 'fg', 'center')
text('rpm_unit', 560, 520, 200, 20, 'RPM X 1000', 'l_label', 'dim', 'left')

# ---- gear, the other gears, speed, M stripe, mode
text('gear', 710, 300, 500, CELL['l_gear'], '{{gearnum}}', 'l_gear', 'red', 'center', glow=True, hotWhen='now')
text('gears_lo', 700, 462, 220, CELL['l_gears'], '234', 'l_gears', 'dim', 'right', spacing=16)
text('gears_hi', 1000, 462, 220, CELL['l_gears'], '678', 'l_gears', 'dim', 'left', spacing=16)
text('speed', 760, 498, 400, CELL['l_speed'], '{{speed}}', 'l_speed', 'fg', 'center', glow=True)
text('speed_unit', 760, 586, 400, CELL['l_label'], '{{u:speed}}', 'l_label', 'dim', 'center', spacing=2)
for i, c in enumerate(['blue', 'mblue', 'red']):
    add(id='mstripe%d' % i, type='fill', **{'class': 'content'}, z=3, x=870 + i * 60, y=612, w=60, h=5, color=c)
text('mode', 760, 628, 400, CELL['l_label'], '{{mode}}', 'l_label', 'dim', 'center', spacing=2)

# ---- left panels
text('trip_t', 254, 124, 120, CELL['l_label'], 'TIME', 'l_label', 'accent', 'left')
text('trip_v', 254, 146, 130, CELL['l_val'], '{{time}}', 'l_val', 'fg', 'left')
text('trip_r', 392, 124, 100, CELL['l_label'], 'RANGE', 'l_label', 'accent', 'left')
text('trip_rv', 392, 146, 110, CELL['l_val'], '{{range}}', 'l_val', 'fg', 'left')
text('trip_ru', 502, 156, 40, CELL['l_label'], '{{u:dist}}', 'l_label', 'dim', 'left')
text('trip_a', 548, 124, 80, CELL['l_label'], 'AVG', 'l_label', 'accent', 'left')
text('trip_av', 548, 146, 70, CELL['l_val'], '{{avgSpeed}}', 'l_val', 'fg', 'left')

text('tyre_h', 100, 212, 160, CELL['l_label'], 'TYRES', 'l_label', 'accent', 'left', spacing=2)
text('tyre_up', 300, 212, 60, CELL['l_label'], '{{u:pressure}}', 'l_label', 'dim', 'left')
text('tyre_ut', 392, 212, 60, CELL['l_label'], '{{u:temp}}', 'l_label', 'dim', 'left')
for name, col, row in [('FL', 0, 0), ('FR', 1, 0), ('RL', 0, 1), ('RR', 1, 1)]:
    x = 96 + col * 188
    y = 244 + row * 50
    text('tp_' + name, x, y, 90, CELL['l_val'], '{{tyreP:%s}}' % name, 'l_val', 'fg', 'left')
    text('tt_' + name, x + 96, y + 8, 70, CELL['l_label'], '{{tyreT:%s}}' % name, 'l_label', 'dim', 'left')

text('dt_h', 60, 376, 220, CELL['l_label'], 'DRIVETRAIN', 'l_label', 'accent', 'left', spacing=2)
text('dt_v', 60, 400, 200, CELL['l_head'], 'RWD', 'l_head', 'red', 'left')


def meter(id, x, y, w, signal, mn, mx, conn=1):
    add(id=id, type='meter', **{'class': 'content'}, z=2, x=x, y=y, w=w, h=12, signal=signal, min=mn, max=mx, segments=int(w / 11),
        gap=3, colors=['blue', 'white', 'red'], at=[0.55, 0.85], conn=conn)


for i, (lab, tok, unit, sig, mn, mx) in enumerate([('OIL', '{{oil}}', '{{u:temp}}', 'oil', 40, 150), ('INTAKE', '{{intake}}', '{{u:temp}}', 'intake', 0, 80)]):
    y = 448 + i * 62
    text('lt%d_l' % i, 60, y + 8, 100, CELL['l_label'], lab, 'l_label', 'dim', 'left')
    text('lt%d_v' % i, 170, y, 150, CELL['l_val'], tok, 'l_val', 'fg', 'right')
    text('lt%d_u' % i, 328, y + 8, 60, CELL['l_label'], unit, 'l_label', 'dim', 'left')
    meter('lt%d_m' % i, 60, y + 36, 360, sig, mn, mx)

# ---- right panels
text('badge', 1290, 134, 400, CELL['l_head'], '{{badge}}', 'l_head', 'fg', 'center', glow=True)
text('pw_h', 1478, 210, 300, CELL['l_label'], 'POWER / TORQUE', 'l_label', 'accent', 'left', spacing=2)
for i, (tok, unit, sig) in enumerate([('{{power}}', 'kW', 'powerPct'), ('{{torque}}', '{{u:torque}}', 'torquePct')]):
    y = 238 + i * 44
    text('pw%d_v' % i, 1470, y, 110, CELL['l_val'], tok, 'l_val', 'fg', 'right')
    text('pw%d_u' % i, 1588, y + 8, 70, CELL['l_label'], unit, 'l_label', 'dim', 'left')
    meter('pw%d_m' % i, 1664, y + 8, 170, sig, 0, 100)

for i, (lab, tok, unit, sig, mn, mx) in enumerate([('FUEL', '{{fuelPct}}', '%', 'fuel', 0, 1), ('WATER', '{{coolant}}', '{{u:temp}}', 'coolant', 40, 130)]):
    y = 448 + i * 44
    text('rt%d_l' % i, 1478, y + 8, 100, CELL['l_label'], lab, 'l_label', 'dim', 'left')
    text('rt%d_v' % i, 1570, y, 90, CELL['l_val'], tok, 'l_val', 'fg', 'right')
    text('rt%d_u' % i, 1668, y + 8, 50, CELL['l_label'], unit, 'l_label', 'dim', 'left')
    meter('rt%d_m' % i, 1730, y + 8, 130, sig, mn, mx)
text('slot1_head', 1478, 546, 150, CELL['l_label'], '{{slotHead:1}} {{slotUnit:1}}', 'l_label', 'dim', 'left')
text('slot1', 1640, 538, 220, CELL['l_val'], '{{slot:1}}', 'l_val', 'fg', 'right', slot='1', fit=['l_label'])

doc = {
    'schemaVersion': 2,
    'name': 'Lambo',
    'packWaste': 3,
    'theme': 'lambo',
    'slots': [{'id': '1', 'where': 'right, bottom', 'default': 'boost'}],
    '_about': 'Lambo cluster, generated by tools/gen_lambo.py (edit that and regenerate): after konsti_m440i\'s Lambo x BMW reel.',
    'widgets': W,
}
with open(OUT, 'w') as f:
    json.dump(doc, f, indent=2)
    f.write('\n')
print('wrote', OUT, len(W), 'widgets')
