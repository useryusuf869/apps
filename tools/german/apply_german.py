#!/usr/bin/env python3
"""German texts for Cluster Themes and HUD Widgets (centre-screen pages and settings).

python3 tools/german/apply_german.py      (run from the repo root, on the English source)

It rewrites the visible strings in place and reports any it could not find, so it can be
run again after pulling a newer upstream version. Labels drawn on the cluster and the HUD
themselves (OIL, COOLANT, BOOST ...) stay as they are: their fonts have no umlauts.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
MISSING = []


def edit(path, pairs):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    for old, new in pairs:
        if old not in s:
            if new not in s:
                MISSING.append((path, old))
            continue
        s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')


def q(pairs):
    """'text' literals: ("Old", "Neu") -> ("'Old'", "'Neu'") with JS escaping of the apostrophe."""
    esc = lambda t: "'" + t.replace("'", "\\'") + "'"
    return [(esc(a), esc(b)) for a, b in pairs]


PAGE = q([
    ('Readouts', 'Anzeigen'), ('Position', 'Position'), ('Map', 'Karte'), ('Badge', 'Schriftzug'),
    ('Alerts', 'Warnungen'), ('Colours', 'Farben'), ('Settings', 'Einstellungen'),
    ('DEMO DATA', 'DEMODATEN'), ('none here', 'keine vorhanden'),
    ('Waze map · on', 'Waze-Karte · an'), ('Waze map · off', 'Waze-Karte · aus'),
    ('Now showing', 'Aktuell angezeigt'), ('Change with the drive mode', 'Mit dem Fahrmodus wechseln'),
    ('  ·  now', '  ·  jetzt'), ('Theme', 'Theme'), ('Otherwise', 'Sonst'), ('Layout', 'Layout'),
    ('Reset slots', 'Felder zurücksetzen'), ('Move', 'Verschieben'), ('Size', 'Größe'),
    ('The dashed frame is the part of the HUD you can see.', 'Der gestrichelte Rahmen ist der sichtbare Teil des HUD.'),
    ('Every tap moves the real HUD right away.', 'Jedes Tippen verschiebt das echte HUD sofort.'),
    ('Navigation map on the cluster', 'Navigationskarte im Tacho'),
    ('Show Waze map inside the theme', 'Waze-Karte im Theme anzeigen'),
    ('Not available in this app', 'In dieser App nicht verfügbar'),
    ('This theme has no map version (GT3, Sport and M do)', 'Dieses Theme hat keine Kartenversion (GT3, Sport und M schon)'),
    ('On: GT3, Sport and M open a window in the middle and Waze on Cluster draws its map in it, above',
     'An: GT3, Sport und M öffnen in der Mitte ein Fenster, in das Waze on Cluster seine Karte zeichnet, über'),
    ("BMW's own map view, so nothing shows twice. When the map goes away the theme fills back in.",
     'BMWs eigener Kartenansicht, damit nichts doppelt erscheint. Ohne Karte füllt das Theme die Mitte wieder.'),
    ("While on, Waze's map on the HUD is off (the cluster and the HUD share one picture).",
     'Solange an, ist die Waze-Karte im HUD aus (Tacho und HUD teilen sich ein Bild).'),
    ("Needs robertnisipeanu's Waze on Cluster. Turning this off gives Waze its usual place back.",
     'Braucht Waze on Cluster von robertnisipeanu. Ausschalten gibt Waze seinen üblichen Platz zurück.'),
    ('Series', 'Baureihe'), ('Model', 'Modell'), ('On the cluster', 'Im Tacho'), ('No badge', 'Kein Schriftzug'),
    ('BMW lettering', 'BMW-Schriftzug'),
    ("Drawn as text in the theme's own font.", 'Als Text in der Schrift des Themes gezeichnet.'),
    ('GT3: top left. Sport and M: bottom centre.', 'GT3: oben links. Sport und M: unten mittig.'),
    ('Warnings · the readout flashes red over its limit', 'Warnungen · die Anzeige blinkt rot über ihrem Grenzwert'),
    ('Shift lights', 'Schaltblitz'), ('Test the shift lights', 'Schaltblitz testen'),
    ('Running', 'Läuft'), ('Stop the car first', 'Erst anhalten'), ('Run test', 'Test starten'),
    ('Runs the rpm up to the shift point for about 4 seconds: the lights fill, go red and flash.',
     'Fährt die Drehzahl etwa 4 Sekunden bis zum Schaltpunkt hoch: die Lichter füllen sich, werden rot und blinken.'),
    ('Only while the car stands. Set a limit to 0 (Off) to turn that warning off.',
     'Nur im Stillstand. Einen Grenzwert auf 0 (Aus) stellen, um diese Warnung abzuschalten.'),
    ('Range', 'Bereich'), ('Trail', 'Spur'), ('Swap left / right', 'Links / rechts tauschen'),
    ('Brake on top', 'Bremse oben'), ('BEST THIS DRIVE, IN G', 'BESTWERTE DIESER FAHRT, IN G'),
    ('Left', 'Links'), ('Right', 'Rechts'), ('Accel', 'Beschl.'), ('Brake', 'Bremse'), ('Peak', 'Spitze'),
    ('Reset', 'Reset'),
    ("From the car's own acceleration sensor. Parked on level ground it reads 0.00; hills add a little.",
     'Vom Beschleunigungssensor des Autos. Geparkt auf ebenem Boden zeigt er 0,00; am Hang etwas mehr.'),
    ('The outline is the most g this drive in every direction; Reset clears it with the bests.',
     'Die Umrisslinie zeigt das höchste g dieser Fahrt in jede Richtung; Reset löscht sie samt Bestwerten.'),
    ('Live', 'Live'), ('no g reading', 'kein g-Wert'), ('BRAKE', 'BREMSE'), ('ACCEL', 'BESCHL.'),
    ('Colours on the glass', 'Farben auf der Scheibe'), ('In daylight', 'Bei Tageslicht'),
    ('Auto switches to Night after sunset. The HUD is a projector: bright, solid colours read best.',
     'Auto wechselt nach Sonnenuntergang auf Night. Das HUD ist ein Projektor: helle, kräftige Farben liest man am besten.'),
    ('Cancel', 'Abbrechen'), ('Centre', 'Mitte'), ('no picture', 'kein Bild'),
    ('HUD is off', 'HUD ist aus'), ('Tap to turn the HUD off', 'Tippen, um das HUD auszuschalten'),
    ('Turn HUD off', 'HUD ausschalten'), ('Turn theme off', 'Theme ausschalten'),
    ("A cluster theme and the HUD can't show at the same time.", 'Ein Tacho-Theme und das HUD können nicht gleichzeitig laufen.'),
    ("The HUD and a cluster theme can't show at the same time.", 'Das HUD und ein Tacho-Theme können nicht gleichzeitig laufen.'),
    ('At the redline', 'Am roten Bereich'), ('warnings off', 'Warnungen aus'),
]) + [
    ('"BMW\'s own" : this.optLabel', '"BMW original" : this.optLabel'),
    ("return v ? 'On' : 'Off';", "return v ? 'An' : 'Aus';"),
    ("if (!(v > 0)) return 'Off';", "if (!(v > 0)) return 'Aus';"),
    ("fmtInt(v) + ' rpm before' :", "fmtInt(v) + ' U/min davor' :"),
    (": fmtInt(v) + ' rpm';", ": fmtInt(v) + ' U/min';"),
    ("fmtInt(this.get('redline')) + ' rpm';", "fmtInt(this.get('redline')) + ' U/min';"),
    ("fmtInt(o[0]) + ' rpm';", "fmtInt(o[0]) + ' U/min';"),
    ("'Turn HUD Widgets off so ' + this.layoutName(v) + ' shows?'", "'HUD Widgets ausschalten, damit ' + this.layoutName(v) + ' erscheint?'"),
    ("'Turn the cluster theme off so ' + this.layoutName(v) + ' shows?'", "'Das Tacho-Theme ausschalten, damit ' + this.layoutName(v) + ' erscheint?'"),
    ("'Off · ' + scr.otherName + ' has the screen · pick one to take it back'", "'Aus · ' + scr.otherName + ' hat die Anzeige · eines wählen, um sie zurückzuholen'"),
    ("on ? 'ON THE ' + this.cfg.what.toUpperCase() : this.cfg.what.toUpperCase() + ' OFF'",
     "(this.cfg.what === 'cluster' ? 'TACHO' : 'HUD') + (on ? ' AN' : ' AUS')"),
    ("this.hud.slotsOf(l).length + ' slots'", "this.hud.slotsOf(l).length + ' Felder'"),
    ("(p.x || p.y ? 'moved' : 'centred')", "(p.x || p.y ? 'verschoben' : 'mittig')"),
    ("this.get('badgeBMW') === true) || 'none';", "this.get('badgeBMW') === true) || 'keiner';"),
    ("return n ? n + ' warning' + (n > 1 ? 's' : '') + ' on' : 'Warnungen aus';",
     "return n ? n + (n > 1 ? ' Warnungen an' : ' Warnung an') : 'Warnungen aus';"),
    ("+ ' · trail ' + this.optLabel('gTrail', this.get('gTrail')).toLowerCase();", "+ ' · Spur ' + this.optLabel('gTrail', this.get('gTrail'));"),
    ("this.cfg.look.name + ' · tap a drive mode to give it that layout'", "this.cfg.look.name + ' · Fahrmodus antippen, um ihm das Layout zu geben'"),
    ("cv.text(v === 'off' ? 'Off' : this.layoutName(v)", "cv.text(v === 'off' ? 'Aus' : this.layoutName(v)"),
    ("v === 'off' ? 'stock ' + this.cfg.what :", "v === 'off' ? (this.cfg.what === 'cluster' ? 'Serien-Tacho' : 'Serien-HUD') :"),
    ('name === \'off\' ? "BMW\'s own " + this.cfg.what :', "name === 'off' ? (this.cfg.what === 'cluster' ? 'BMW-Tacho original' : 'BMW-HUD original') :"),
    ("['None of these ' + this.cfg.look.name.toLowerCase() + ' has readout slots.']", "['Keines dieser ' + this.cfg.look.name + ' hat Anzeigefelder.']"),
    ("this.layoutName(lay) + ' · readout slots'", "this.layoutName(lay) + ' · Anzeigefelder'"),
    ("'Slot ' + n + ' · pick a sensor'", "'Feld ' + n + ' · Sensor wählen'"),
    ("this.layoutName(shown)) + ' · where it sits on the glass'", "this.layoutName(shown)) + ' · Position auf der Scheibe'"),
    ('shown === \'off\' ? "BMW\'s own HUD" :', "shown === 'off' ? 'BMW-HUD original' :"),
]

SENSORS = [
    ("const CATS = ['Engine', 'Temps', 'Chassis', 'Fuel', 'Tyres', 'Drive'];", "const CATS = ['Motor', 'Temp.', 'Fahrwerk', 'Kraftstoff', 'Reifen', 'Fahrt'];"),
    ("cat: 'Engine'", "cat: 'Motor'"), ("cat: 'Temps'", "cat: 'Temp.'"), ("cat: 'Chassis'", "cat: 'Fahrwerk'"),
    ("cat: 'Fuel'", "cat: 'Kraftstoff'"), ("cat: 'Tyres'", "cat: 'Reifen'"), ("cat: 'Drive'", "cat: 'Fahrt'"),
] + [("name: '%s'" % a, "name: '%s'" % b) for a, b in [
    ('Engine speed', 'Motordrehzahl'), ('Boost', 'Ladedruck'), ('Engine torque', 'Motordrehmoment'), ('Power', 'Leistung'),
    ('Torque, % of max', 'Drehmoment, % vom Maximum'), ('Power, % of max', 'Leistung, % vom Maximum'),
    ('Oil temperature', 'Öltemperatur'), ('Coolant temperature', 'Kühlmitteltemperatur'),
    ('Intake air temperature', 'Ansauglufttemperatur'), ('Outside temperature', 'Außentemperatur'), ('Speed', 'Geschwindigkeit'),
    ('Cornering g', 'Querbeschleunigung (g)'), ('Braking / accel g', 'Bremsen / Beschleunigen (g)'),
    ('Fuel level', 'Tankfüllstand'), ('Range', 'Reichweite'), ('Hybrid battery (plug-in hybrids)', 'Hybridbatterie (Plug-in-Hybride)'),
    ('Tyre pressure, front left', 'Reifendruck, vorn links'), ('Tyre pressure, front right', 'Reifendruck, vorn rechts'),
    ('Tyre pressure, rear left', 'Reifendruck, hinten links'), ('Tyre pressure, rear right', 'Reifendruck, hinten rechts'),
    ('Tyre temperature, front left', 'Reifentemperatur, vorn links'), ('Tyre temperature, front right', 'Reifentemperatur, vorn rechts'),
    ('Tyre temperature, rear left', 'Reifentemperatur, hinten links'), ('Tyre temperature, rear right', 'Reifentemperatur, hinten rechts'),
    ('Shift point', 'Schaltpunkt'), ('Last shift', 'Letzter Gangwechsel'), ('Clock', 'Uhr'),
]]

TZ = q([('Canada Atlantic', 'Kanada Atlantik'), ('Mexico', 'Mexiko'), ('UK, Ireland, Portugal', 'UK, Irland, Portugal'),
        ('Central Europe', 'Mitteleuropa'), ('Eastern Europe', 'Osteuropa'), ('Automatic', 'Automatisch')])

WAZE = q([
    ("Waze on Cluster isn't running", 'Waze on Cluster läuft nicht'),
    ("Waze on Cluster: this car isn't supported", 'Waze on Cluster: dieses Auto wird nicht unterstützt'),
    ('Waze map is turned off in the Waze app', 'Die Waze-Karte ist in der Waze-App ausgeschaltet'),
    ("Off. Waze shows the map in BMW's own map view", 'Aus. Waze zeigt die Karte in BMWs eigener Kartenansicht'),
    ('Waze app is open, retrying', 'Waze-App ist offen, neuer Versuch'),
    ('Moving the map into the theme', 'Verschiebe die Karte ins Theme'),
    ('Map showing in the theme', 'Karte wird im Theme angezeigt'),
    ('Map frozen, waiting for the phone', 'Karte eingefroren, warte auf das Handy'),
    ('Waze on Cluster reports an error', 'Waze on Cluster meldet einen Fehler'),
    ('Waiting for the map', 'Warte auf die Karte'),
]) + [("'Can\\'t reach Waze on Cluster (' +", "'Waze on Cluster nicht erreichbar (' +")]

CLUSTER_MAIN = [
    ("look: { name: 'Themes',", "look: { name: 'Themes',"),
    ("gt3: 'race dash'", "gt3: 'Renn-Dash'"), ("m: 'M8 style'", "m: 'M8-Stil'"), ("minimal: 'just the speed'", "minimal: 'nur das Tempo'"),
    ("roadster: 'round dials'", "roadster: 'Rundinstrumente'"), ("track: 'tyres + temps'", "track: 'Reifen + Temp.'"),
    ("drag: '0-60 timer'", "drag: '0-100-Timer'"), ("rally: 'rev arc · G-meter'", "rally: 'Drehzahlbogen · G-Meter'"),
    ("retro80s: '80s digital'", "retro80s: '80er digital'"), ("cruise: 'calm · trip'", "cruise: 'ruhig · Fahrt'"),
    ("dyno: 'safety tiles'", "dyno: 'Überwachungs-Kacheln'"),
]
HUD_MAIN = [
    ("daily: 'gear · clock · oil'", "daily: 'Gang · Uhr · Öl'"), ("sport: 'rev bar · temps · boost'", "sport: 'Drehzahl · Temp. · Ladedruck'"),
    ("redline: 'shift lights · shift score'", "redline: 'Schaltblitz · Schaltnote'"), ("minimal: 'round BMW speed'", "minimal: 'rundes BMW-Tempo'"),
    ("shiftonly: 'lights · gear'", "shiftonly: 'Lichter · Gang'"), ("boost: 'boost · peak'", "boost: 'Ladedruck · Spitze'"),
    ("warmup: 'oil · coolant · intake'", "warmup: 'Öl · Wasser · Ansaug'"), ("track: 'lights · G-meter'", "track: 'Lichter · G-Meter'"),
    ("cruise: 'range · trip'", "cruise: 'Reichweite · Fahrt'"), ("retro: 'amber digital'", "retro: 'Amber digital'"),
]

LABELS = {
    'All settings': 'Alle Einstellungen',
    'Theme (when not by drive mode)': 'Theme (wenn nicht nach Fahrmodus)',
    'Layout (when not by drive mode)': 'Layout (wenn nicht nach Fahrmodus)',
    'Change with SPORT / COMFORT / ECO PRO': 'Mit SPORT / COMFORT / ECO PRO wechseln',
    'In Comfort': 'In Comfort', 'In Sport': 'In Sport', 'In Eco Pro': 'In Eco Pro',
    'In Comfort (Daily by default; BMW keeps its speed bottom-left)': 'In Comfort (Standard: Daily; BMW behält sein Tempo unten links)',
    "In Sport (off by default: BMW's Sport HUD takes the middle)": 'In Sport (Standard: aus; BMWs Sport-HUD nutzt die Mitte)',
    "In Eco Pro (off by default: BMW's own HUD)": 'In Eco Pro (Standard: aus; BMW-HUD original)',
    'Show Waze map inside the theme': 'Waze-Karte im Theme anzeigen',
    'Units': 'Einheiten', 'Clock': 'Uhr', 'Time zone (clock)': 'Zeitzone (Uhr)', 'Fuel tank size': 'Tankgröße',
    'Redline (shift light)': 'Roter Bereich (Schaltblitz)', 'Shift point before redline': 'Schaltpunkt vor dem roten Bereich',
    'Cold-engine rev guard': 'Drehzahlschutz bei kaltem Motor', 'Cold-engine rev guard (Redline)': 'Drehzahlschutz bei kaltem Motor (Redline)',
    'Show boost': 'Ladedruck anzeigen', 'Show boost (Sport layout)': 'Ladedruck anzeigen (Layout Sport)',
    "Leave BMW's bottom strip clear": 'BMWs untere Leiste frei lassen',
    'Oil temperature warning': 'Öltemperatur-Warnung', 'Coolant temperature warning': 'Kühlmitteltemperatur-Warnung',
    'Boost warning': 'Ladedruck-Warnung', 'G-meter: swap left / right': 'G-Meter: links / rechts tauschen',
    'G-meter: brake on top': 'G-Meter: Bremse oben', 'G-meter range': 'G-Meter-Bereich', 'G-meter trail': 'G-Meter-Spur',
    'Night colours': 'Nachtfarben', 'Badge': 'Schriftzug', 'BMW lettering on the badge': 'BMW im Schriftzug',
    'Demo data': 'Demodaten', 'Theme': 'Theme', 'Daytime theme for Auto': 'Tages-Theme für Auto',
    'HUD position, left / right': 'HUD-Position, links / rechts', 'HUD position, up / down': 'HUD-Position, hoch / runter',
    'HUD size': 'HUD-Größe', 'Show clock': 'Uhr anzeigen', 'Show oil temperature': 'Öltemperatur anzeigen',
    'Show coolant temperature': 'Kühlmitteltemperatur anzeigen',
}
OPTIONS = {
    "Off (BMW's own cluster)": 'Aus (BMW-Tacho original)', "Off (BMW's own HUD)": 'Aus (BMW-HUD original)',
    'Calibration grid': 'Kalibrierraster', 'Map calibration': 'Karten-Kalibrierung', 'Window calibration': 'Fenster-Kalibrierung',
    '12-hour': '12 Stunden', '24-hour': '24 Stunden', 'Off': 'Aus', 'On': 'An', 'None': 'Keiner',
    'Auto (dimmer after sunset)': 'Auto (dunkler nach Sonnenuntergang)', 'Auto (Night after sunset)': 'Auto (Night nach Sonnenuntergang)',
    'Auto (until the car sends data)': 'Auto (bis das Auto Daten sendet)', 'Shift only': 'Nur Schaltblitz', 'Warm-up': 'Warmfahren',
}
DESCRIPTIONS = {
    'cluster_themes': 'Zeichnet den Tacho neu: GT3-Renn-Dash, M-Stil, Sport, Minimal, Roadster, Track, Drag, Rally, Retro 80s, Cruise oder Dyno, '
                      'mit Schaltblitz, Ladedruck, Temperaturen, Reifen, G-Meter und Beschleunigungs-Timer',
    'idrive_hud_widgets': 'Gang, Schaltblitz, Ladedruck, Öl-, Kühlmittel- und Ansauglufttemperatur, G-Meter und Fahrtwerte im Head-up-Display, '
                          'in den Themes Classic, M oder Night',
}
# what a car sold in Germany wants out of the box
DEFAULTS = {'units': 'metric', 'clock': '24h', 'timeZone': 10012}


def manifest(app):
    p = ROOT / 'apps' / app / 'app.json'
    d = json.loads(p.read_text(encoding='utf-8'))
    d['description'] = DESCRIPTIONS[app]
    for screen in d.get('screens', []):
        for b in screen.get('buttons', []):
            b[1] = LABELS.get(b[1], b[1])
    for s in d.get('settings', []):
        if s['label'] not in LABELS and s['label'] not in LABELS.values():
            MISSING.append(('apps/%s/app.json' % app, s['label']))
        s['label'] = LABELS.get(s['label'], s['label'])
        for o in s.get('options', []):
            if isinstance(o, list) and len(o) > 1 and isinstance(o[1], str):
                o[1] = OPTIONS.get(o[1], o[1])
        if s.get('key') in DEFAULTS:
            s['default'] = DEFAULTS[s['key']]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


edit('shared/page.js', PAGE)
edit('shared/sensors.js', SENSORS)
edit('shared/tz.js', TZ)
edit('shared/waze.js', WAZE)
edit('apps/cluster_themes/main.js', CLUSTER_MAIN)
edit('apps/idrive_hud_widgets/main.js', HUD_MAIN)
manifest('cluster_themes')
manifest('idrive_hud_widgets')
for path, old in MISSING:
    print('NOT FOUND in %s: %s' % (path, old))
print('German texts applied;', len(MISSING), 'not found')
sys.exit(1 if MISSING else 0)
