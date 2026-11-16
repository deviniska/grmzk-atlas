#!/usr/bin/env python3
"""GRMZK Atlas previews: one simplified line drawing per object on its dominant colour.

640x640 square, drawing kept inside the inscribed circle (map bubbles crop to a circle),
thick round strokes so the shape still reads at 30-48 px.
"""
import math, os, subprocess, sys

S = 640
SW = 22            # main stroke
SW2 = 14           # detail stroke
WHITE = '#ffffff'
DARK = '#1e1c1a'

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
os.makedirs(OUT, exist_ok=True)


def L(x1, y1, x2, y2, w=None):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{sw(w)}/>'

def C(cx, cy, r, w=None):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}"{sw(w)}/>'

def E(cx, cy, rx, ry, w=None, rot=0):
    t = f' transform="rotate({rot} {cx} {cy})"' if rot else ''
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"{sw(w)}{t}/>'

def R(x, y, w_, h, rx=0, w=None, rot=None):
    t = f' transform="rotate({rot[0]} {rot[1]} {rot[2]})"' if rot else ''
    return f'<rect x="{x}" y="{y}" width="{w_}" height="{h}" rx="{rx}"{sw(w)}{t}/>'

def P(d, w=None):
    return f'<path d="{d}"{sw(w)}/>'

def D(cx, cy, r):  # filled dot
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" class="f"/>'

def T(d, w=64, edge=SW2):
    """Tube: an outlined thick stroke; later tubes hide earlier ones."""
    return (f'<path d="{d}" style="stroke-width:{w}"/>'
            f'<path d="{d}" class="bgs" style="stroke-width:{w - 2 * edge}"/>')

def sw(w):
    return f' style="stroke-width:{w}"' if w else ''

def arc_pts(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def svg(bg, line, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{S}" height="{S}" viewBox="0 0 {S} {S}">'
            f'<style>*{{fill:none;stroke:{line};stroke-width:{SW};stroke-linecap:round;stroke-linejoin:round}}'
            f'.f{{fill:{line};stroke:none}}.bg{{fill:{bg};stroke:none}}.bgs{{stroke:{bg}}}</style>'
            f'<rect class="bg" width="{S}" height="{S}"/>{body}</svg>')


# ---------------------------------------------------------------- drawings

def g2():   # Local Nomad: rag-boiling sphere lying on its side
    b = [C(320, 335, 175)]
    b.append(P('M150,320 Q320,395 490,320', SW2))
    b.append(P('M300,162 Q250,335 300,508', SW2))
    b.append(R(395, 150, 70, 50, 10, rot=(35, 430, 175)))       # nozzle
    b.append(C(220, 470, 22, SW2))                               # small flange
    b += [D(x, y, 8) for x, y in [(185, 345), (235, 360), (405, 360), (455, 345)]]
    return b

def g3():   # Silo 468: oil silo with LED holes
    b = [E(320, 205, 175, 40), P('M145,205 V470 Q320,525 495,470 V205')]
    b += [L(x, 205, x, 160, SW2) for x in (175, 245, 320, 395, 465)]
    b.append(P('M155,160 Q320,130 485,160', SW2))
    for row, y0 in enumerate((265, 320, 375, 430)):
        for i in range(7):
            x = 180 + i * 47
            y = y0 + 18 * math.sin(i * 0.9 + row * 1.3)
            b.append(D(round(x), round(y), 11))
    return b

def g4():   # Fröndenberg funnel: tank with cone on legs, railing on top
    b = [E(320, 180, 150, 34), P('M170,180 V300 L280,410 H360 L470,300 V180')]
    b.append(L(170, 300, 470, 300, SW2))
    b += [L(195, 325, 175, 520), L(445, 325, 465, 520), L(285, 410, 280, 520), L(355, 410, 360, 520)]
    b += [L(x, 180, x, 135, SW2) for x in (190, 260, 320, 380, 450)]
    b.append(P('M180,135 Q320,110 460,135', SW2))
    return b

def g5():   # Ladle of Steel: a real ladle tipped over, pouring steel into a mould
    b = [P('M280,115 C350,105 430,130 465,165 C480,210 465,265 430,290 C370,300 290,285 245,265')]
    b.append(E(262, 190, 34, 78, None, 15))
    b.append(L(400, 290, 425, 520)); b.append(L(340, 520, 510, 520))
    b.append(P('M232,240 C190,300 170,380 180,450', SW2))
    b.append(P('M262,262 C230,320 225,390 240,450', SW2))
    b.append(R(130, 450, 160, 60, 8))
    return b
def g6():   # Waypoint: acid ball on splayed legs
    b = [C(320, 265, 160)]
    b.append(P('M168,230 Q320,290 472,230', SW2))
    b.append(P('M180,330 Q320,385 460,330', SW2))
    for x0, x1 in ((205, 165), (265, 245), (375, 395), (435, 475)):
        b.append(L(x0, 375, x1, 530))
    b.append(L(165, 470, 475, 470, SW2))
    b += [D(x, y, 7) for x, y in [(245, 170), (390, 190), (300, 225), (410, 290), (230, 300)]]
    return b

def g7():   # Eco Earth: tiled globe on a low base
    b = [C(320, 285, 185)]
    b.append(P('M175,250 C200,190 260,170 300,195 C330,215 300,250 315,285 C330,325 300,370 260,385 C240,350 250,315 220,300 C190,290 170,280 175,250 Z', SW2))
    b.append(P('M390,290 C420,280 455,300 460,330 C440,370 405,385 385,360 C375,340 370,300 390,290 Z', SW2))
    b.append(P('M150,285 H490 M320,100 V470', 8))
    b.append(P('M230,455 L210,515 H430 L410,455'))
    return b
def g8():   # Savannah Globe: Horton sphere painted as the Earth, on legs
    b = [C(320, 255, 175)]
    for x0, x1 in ((190, 165), (255, 245), (385, 395), (450, 475)):
        b.append(L(x0, 370, x1, 525))
    b.append(L(150, 525, 490, 525, SW2))
    b.append(P('M200,205 c10,-30 50,-35 60,-10 c20,-15 55,0 45,25 c25,5 20,40 -10,40 h-90 c-30,0 -30,-45 -5,-55 z', SW2))
    b.append(P('M330,290 c10,-25 45,-28 55,-8 c18,-12 50,0 40,22 c22,5 18,36 -8,36 h-80 c-27,0 -27,-40 -7,-50 z', SW2))
    return b

def g9():   # Tank with the Crank: rusty tank, crank, whale and boat on top
    b = [E(300, 255, 120, 28), P('M180,255 V500 Q300,535 420,500 V255')]
    b.append(P('M420,380 H475 V440'))
    b.append(C(475, 452, 14, SW2))
    b.append(P('M210,215 C230,165 330,150 385,190 C400,175 420,170 432,155 M385,190 C410,200 425,190 440,180', SW2))
    b.append(P('M200,215 H385', SW2))
    b.append(P('M200,330 c25,-25 60,-25 80,0 c-20,25 -55,25 -80,0 l-20,-15 v30 z', SW2))
    b.append(P('M300,425 c25,-25 60,-25 80,0 c-20,25 -55,25 -80,0 l-20,-15 v30 z', SW2))
    return b

def g10():  # Rusty the mastodon: a boiler on legs with tusks and a trunk
    b = [R(235, 215, 250, 160, 70)]
    b += [L(x, 221, x, 369, SW2) for x in (300, 360, 420)]
    b += [L(265, 375, 265, 495), L(320, 375, 320, 495), L(400, 375, 400, 495), L(455, 375, 455, 495)]
    b.append(C(195, 245, 62))
    b.append(P('M150,280 C135,340 160,400 140,460 C135,480 115,485 110,470'))
    b.append(P('M205,300 C200,350 150,360 105,330 C85,315 80,290 90,270', SW2))
    b.append(P('M215,240 C235,215 240,180 220,165', SW2))
    b.append(D(180, 228, 10))
    b.append(P('M485,260 C510,270 520,300 515,330', SW2))
    return b
def g11():  # The Way: red tanks cut and assembled
    b = [L(110, 480, 530, 480, SW2)]
    b.append(T('M190,480 V250'))
    b.append(T('M450,480 V280'))
    b.append(T('M160,230 L470,190'))
    b.append(T('M300,480 V170'))
    b.append(T('M130,330 L360,430', 56))
    b.append(T('M290,340 L520,420', 56))
    return b
def g12():  # Nikotan: smiling gas sphere on legs
    b = [C(320, 255, 175)]
    for x0, x1 in ((190, 170), (255, 245), (385, 395), (450, 470)):
        b.append(L(x0, 370, x1, 520))
    b.append(L(150, 520, 490, 520, SW2))
    b.append(P('M240,225 Q265,195 290,225'))
    b.append(P('M350,225 Q375,195 400,225'))
    b.append(P('M240,290 Q320,365 400,290'))
    return b

def g13():  # Immerge: cast-iron tank panels sinking into the ground
    b = []
    ox, oy = 170, 140
    def pt(u, v):  # tilted grid
        a = math.radians(-18)
        x, y = u * 85, v * 85
        return ox + x * math.cos(a) - y * math.sin(a), oy + x * math.sin(a) + y * math.cos(a)
    clip = '<clipPath id="g"><rect x="0" y="0" width="640" height="430"/></clipPath>'
    lines = []
    for i in range(5):
        x1, y1 = pt(i, 0); x2, y2 = pt(i, 4)
        lines.append(L(round(x1), round(y1), round(x2), round(y2), SW2 if 0 < i < 4 else None))
        x1, y1 = pt(0, i); x2, y2 = pt(4, i)
        lines.append(L(round(x1), round(y1), round(x2), round(y2), SW2 if 0 < i < 4 else None))
    b.append(clip + '<g clip-path="url(#g)">' + ''.join(lines) + '</g>')
    b.append(P('M110,430 Q320,410 530,430'))
    b.append(P('M150,480 Q240,470 300,485 M360,480 Q430,470 500,482', SW2))
    return b

def g14():  # Martin Luther: steam traction engine
    b = [R(170, 260, 230, 100, 45)]
    b.append(R(205, 140, 34, 120, 6))
    b.append(L(195, 140, 249, 140))
    b.append(C(420, 390, 95))
    b += [L(420, 390, 420 + 95 * math.cos(math.radians(a)), 390 + 95 * math.sin(math.radians(a)), SW2) for a in range(0, 360, 45)]
    b.append(C(205, 415, 55))
    b.append(P('M350,175 H510 M370,175 V260 M495,175 V300', SW2))
    return b

def g15():  # Home. Memories: old fuel tank inside a wire-frame Ukrainian house
    b = [R(240, 300, 160, 190, 20), E(320, 300, 80, 18, SW2)]
    b.append(P('M150,500 V265 L320,130 L490,265 V500', SW2))
    b.append(L(150, 265, 490, 265, SW2))
    b.append(R(178, 330, 46, 60, 4, SW2))
    b.append(R(418, 330, 46, 60, 4, SW2))
    b.append(L(120, 500, 520, 500))
    return b

def g16():  # Nomad's Twin: the second sphere, asleep at the mill
    b = [C(320, 335, 175)]
    b.append(P('M150,320 Q320,395 490,320', SW2))
    b.append(P('M340,162 Q390,335 340,508', SW2))
    b.append(R(175, 150, 70, 50, 10, rot=(-35, 210, 175)))
    b.append(P('M225,265 Q250,285 275,265', SW2))
    b.append(P('M365,265 Q390,285 415,265', SW2))
    return b

def g17():  # Kugelkocher: rotating sphere on a cast-iron stand with a gear
    b = [C(300, 280, 165)]
    b.append(P('M145,250 Q300,320 455,250', SW2))
    b.append(L(300, 280, 500, 280, SW2))
    b.append(C(500, 280, 55))
    b += [L(500, 280, 500 + 55 * math.cos(math.radians(a)), 280 + 55 * math.sin(math.radians(a)), SW2) for a in range(0, 360, 60)]
    b.append(P('M180,520 L235,410 M420,410 L470,520'))
    b.append(L(150, 520, 500, 520))
    b.append(R(265, 105, 70, 30, 8, SW2))
    return b

def g18():  # Canton acid ball: riveted sphere found in the demolition
    b = [C(320, 280, 180)]
    b.append(P('M145,250 Q320,320 495,250', SW2))
    b.append(P('M320,100 Q260,280 320,460', SW2))
    for x, y in arc_pts(320, 280, 155, 200, 340, 7):
        b.append(D(round(x), round(y), 8))
    b.append(P('M120,500 L190,455 L235,490 L290,470 L345,495 L410,460 L460,490 L520,470', SW2))
    return b

def g19():  # Gas Works Park: two towers and their pipes
    b = [R(190, 110, 80, 380, 30), R(370, 160, 80, 330, 30)]
    b += [L(190, y, 270, y, SW2) for y in (200, 300, 400)]
    b += [L(370, y, 450, y, SW2) for y in (250, 340, 430)]
    b.append(P('M270,240 H330 V300 H370', SW2))
    b.append(P('M270,360 C310,360 330,380 370,380', SW2))
    b.append(L(130, 490, 510, 490))
    return b

def g20():  # Worried Buoy: pot-bellied little man with a worried face
    b = [C(320, 370, 135), C(320, 165, 70)]
    b.append(L(320, 235, 320, 238))
    b.append(P('M285,150 L305,140 M335,140 L355,150', SW2))
    b.append(D(295, 170, 9)); b.append(D(345, 170, 9))
    b.append(P('M295,200 Q305,190 320,200 Q335,210 345,198', SW2))
    b.append(P('M190,350 C140,330 140,400 185,395'))
    b.append(P('M450,350 C500,330 500,400 455,395'))
    b.append(L(320, 505, 320, 560))
    return b

def g21():  # Robot Cisterns: two propane tanks turned robots
    b = []
    for cx in (225, 415):
        b.append(R(cx - 70, 150, 140, 360, 70))
        b.append(C(cx - 28, 240, 20, SW2)); b.append(C(cx + 28, 240, 20, SW2))
        b.append(R(cx - 35, 290, 70, 22, 8, SW2))
        b.append(L(cx, 150, cx, 115, SW2)); b.append(D(cx, 108, 11))
        b.append(L(cx - 45, 510, cx - 45, 540, SW2)); b.append(L(cx + 45, 510, cx + 45, 540, SW2))
    return b

def g22():  # Big Rig Jig: two tankers bent into an S
    b = [T('M190,450 C190,330 330,360 380,300 C430,240 400,160 320,150', 74)]
    b.append(R(120, 430, 120, 75, 12))
    b.append(R(140, 445, 40, 30, 4, SW2))
    b.append(C(150, 515, 20, SW2)); b.append(C(215, 515, 20, SW2))
    b.append(R(225, 110, 100, 70, 12))
    b.append(C(245, 100, 18, SW2)); b.append(C(305, 100, 18, SW2))
    return b
def g23():  # Future Returns: oil tanker cut into a forest
    b = [R(120, 260, 120, 160, 18), R(150, 285, 70, 55, 6, SW2)]
    b.append(R(240, 220, 290, 190, 90))
    b.append(L(110, 420, 530, 420, SW2))
    b += [C(x, 450, 32) for x in (175, 380, 470)]
    b.append(P('M300,410 V330 M300,360 L265,315 M300,340 L335,290 M335,290 L330,250 M335,290 L370,270', SW2))
    b.append(P('M430,410 V320 M430,355 L470,320 M430,330 L400,290 M400,290 L410,255 M470,320 L495,300', SW2))
    return b

def g24():  # Moby Train: the Gros Nez locomotive inside a whale
    b = [P('M110,350 C110,250 230,215 350,230 C430,240 470,230 490,200 C470,185 450,160 450,130 C480,150 500,170 505,190 C520,170 545,160 565,165 C545,185 525,205 515,225 C500,330 430,420 300,425 C190,430 110,420 110,350 Z')]
    b.append(R(165, 290, 230, 80, 14, SW2))
    b += [R(x, 306, 32, 28, 4, SW2) for x in (190, 240, 290, 340)]
    b.append(D(150, 300, 10))
    b.append(P('M125,375 Q165,385 200,372', SW2))
    b.append(L(100, 500, 540, 500, SW2))
    return b
def g25():  # Mushrooms and Bird Blind: a water tank cut into mushrooms
    b = [P('M120,300 C130,170 330,140 400,260 C410,285 390,300 360,300 Z')]
    b.append(P('M250,300 C235,370 245,440 225,505 M300,300 C300,370 300,440 290,505'))
    b += [D(x, y, 12) for x, y in [(200, 245), (270, 215), (330, 245)]]
    b.append(P('M400,410 C405,350 500,340 525,410 Z', SW2))
    b.append(P('M450,410 V505 M475,410 V505', SW2))
    b.append(L(150, 505, 540, 505))
    return b

def g26():  # Boston Buoy Trail: mosaic can buoy with a topmark
    b = [P('M200,520 L230,250 H410 L440,520 Z')]
    b.append(P('M215,400 H425', SW2))
    b.append(L(320, 250, 320, 165))
    b.append(P('M320,90 L370,140 L320,190 L270,140 Z'))
    b += [R(x, y, 26, 26, 4, SW2) for x, y in [(255, 290), (300, 320), (350, 290), (270, 345), (340, 350)]]
    return b

def g27():  # Frampton Marsh: conical buoy painted with a sunflower
    b = [P('M170,510 C200,400 260,230 320,160 C380,230 440,400 470,510 Z')]
    b.append(L(320, 160, 320, 110)); b.append(C(320, 95, 16, SW2))
    b.append(C(330, 360, 32, SW2))
    b += [E(330 + 62 * math.cos(math.radians(a)), 360 + 62 * math.sin(math.radians(a)), 24, 12, SW2, a) for a in range(0, 360, 45)]
    b.append(L(130, 510, 510, 510))
    return b

def g28():  # Lakes Entrance: bell buoy with a lattice tower, painted with waves
    b = [P('M175,500 C175,400 230,330 320,330 C410,330 465,400 465,500 Z')]
    b.append(P('M240,330 L300,110 H340 L400,330', SW2))
    b.append(P('M262,250 L380,250 M282,180 L360,180 M262,250 L360,180 M282,180 L340,110', SW2))
    b.append(P('M200,440 q30,-30 60,0 t60,0 t60,0 t60,0', SW2))
    b.append(L(140, 500, 500, 500))
    return b

def g29():  # Woolgoolga: a cluster of old buoys
    b = [P('M120,500 C120,380 160,300 230,300 C300,300 340,380 340,500 Z')]
    b.append(P('M300,500 C300,330 350,230 420,230 C490,230 530,330 530,500 Z'))
    b.append(L(230, 300, 230, 245, SW2)); b.append(C(230, 232, 14, SW2))
    b.append(L(420, 230, 420, 165, SW2)); b.append(C(420, 150, 15, SW2))
    b += [P(f'M160,{y} H300', SW2) for y in (380, 440)]
    b += [P(f'M345,{y} H500', SW2) for y in (320, 390, 450)]
    b.append(L(100, 500, 550, 500))
    return b

def g30():  # Buoy in a field: tall spar light buoy far from the sea
    b = [P('M290,500 L280,250 L305,120 H335 L360,250 L350,500 Z')]
    b += [L(284, 250, 356, 250, SW2), L(290, 300, 350, 300, SW2), L(298, 175, 342, 175, SW2)]
    b.append(L(320, 120, 320, 85, SW2))
    b.append(P('M100,500 Q320,480 540,500'))
    b.append(P('M430,500 V430 M480,500 V440 M430,455 H480', SW2))
    return b

def g31():  # The Bathysphere: steel sphere with portholes and a hatch
    b = [C(320, 300, 170)]
    b += [C(255, 250, 30, SW2), C(330, 225, 30, SW2), C(255, 330, 30, SW2)]
    b.append(C(420, 320, 55, SW2))
    b += [D(round(420 + 40 * math.cos(math.radians(a))), round(320 + 40 * math.sin(math.radians(a))), 6) for a in range(0, 360, 45)]
    b.append(C(320, 112, 18, SW2))
    b.append(L(320, 94, 320, 60, SW2))
    b.append(P('M215,460 L195,520 H445 L425,460'))
    return b

def g32():  # Mantis Dreaming: a praying mantis from a railway tank car
    b = [R(320, 300, 230, 96, 48, rot=(30, 435, 348))]
    b.append(P('M300,180 C240,330 470,250 520,370', SW2))
    b.append(T('M345,315 L290,200', 44, SW2))
    b.append(P('M240,175 C240,135 330,120 330,160 C330,185 290,200 265,200 C250,200 240,190 240,175 Z'))
    b.append(D(262, 160, 10)); b.append(D(305, 152, 10))
    b.append(P('M262,135 L230,85 M300,128 L300,75', SW2))
    b.append(P('M300,235 L215,255 L235,200', SW2))
    b.append(P('M315,260 L230,290 L250,235', SW2))
    b.append(P('M370,370 L330,510 M430,400 L440,515 M500,420 L545,505', SW2))
    return b
def g33():  # Stork's Nest: old port lighting mast with a nest and eggs
    b = [L(320, 540, 320, 260)]
    b.append(P('M290,540 L320,470 L350,540', SW2))
    b.append(P('M170,250 Q320,330 470,250'))
    b.append(P('M180,240 L460,265 M190,265 L450,235 M200,255 L440,250', SW2))
    b += [E(x, 215, 30, 40) for x in (255, 320, 385)]
    return b

def g34():  # Tin Man: rooftop water tank with a funnel hat
    b = [R(205, 230, 230, 210, 20)]
    b.append(P('M195,230 L320,110 L445,230'))
    b.append(L(320, 110, 320, 70, SW2))
    b.append(E(275, 300, 22, 30, SW2)); b.append(E(365, 300, 22, 30, SW2))
    b.append(D(320, 345, 10))
    b.append(P('M285,390 H355', SW2))
    b += [L(235, 440, 215, 530), L(405, 440, 425, 530)]
    b.append(L(150, 530, 490, 530))
    return b

def g35():  # Sky Chair: a giant seat assembled from blue metal barrels
    b = []
    for y in (110, 175, 240, 305):          # back: barrels lying, stacked
        b.append(R(340, y, 150, 58, 28))
    for x in (150, 240, 330):               # seat
        b.append(R(x, 370, 90, 58, 28))
    b.append(R(150, 428, 80, 82, 28)); b.append(R(410, 428, 80, 82, 28))  # legs
    b.append(L(110, 510, 530, 510, SW2))
    return b
def g36():  # Window to the Sun: gas sphere with the Sun projected on it
    b = [C(320, 260, 170)]
    b.append(P('M230,200 C260,170 300,215 340,185 C370,165 400,195 420,215', SW2))
    b.append(P('M210,280 C250,250 290,300 330,270 C370,245 400,290 435,270', SW2))
    b.append(P('M240,350 C270,330 310,365 350,340 C375,325 395,345 410,350', SW2))
    b.append(P('M190,400 C250,450 390,450 450,400 C430,470 360,500 320,500 C270,500 230,470 190,400 Z', SW2))
    b += [D(x, 525, 9) for x in (120, 175, 230, 285, 355, 410, 465, 520)]
    return b


def g37():  # Future SpaceShip: a rusting truck box waiting to become a spaceship (fading)
    dash = ' style="stroke-dasharray:34 22"'
    b = [P('M120,245 L400,215 L520,250')]                       # roof edges
    b.append(P('M120,245 L245,228 L520,250', SW2))               # far roof edge
    b.append(L(120, 245, 130, 460)); b.append(L(400, 215, 405, 505)); b.append(L(520, 250, 515, 440))
    b.append(f'<path d="M130,460 L405,505 L515,440"{dash}/>')     # bottom edges dissolving
    b.append(R(262, 262, 44, 92, 20, SW2)); b.append(R(322, 258, 44, 92, 20, SW2))   # door windows
    b.append(P('M255,250 L258,488 M378,236 L381,500', SW2))       # door
    b.append(R(160, 275, 66, 74, 4, SW2)); b.append(P('M160,275 L226,349 M226,275 L160,349', 8))  # boarded window
    b.append(C(462, 300, 12, SW2))                               # round hole
    b.append(P('M140,520 L232,512 M140,540 L232,532', SW2)); b.append(E(140, 530, 8, 10, SW2))     # pipe on the grass
    b += [D(x, y, r) for x, y, r in [(185, 400, 9), (215, 430, 6), (450, 380, 10), (480, 410, 7), (350, 420, 6)]]  # rust
    b.append(P('M470,120 V160 M450,140 H490', SW2)); b.append(P('M540,175 V199 M528,187 H552', 10))  # stars ahead
    return ['<g transform="translate(-32,-50) scale(1.1)">'] + b + ['</g>']


OBJECTS = {
    2: ('#6b3fa0', WHITE, g2),
    3: ('#d8cbc3', DARK, g3),
    4: ('#30353a', WHITE, g4),
    5: ('#9c3b1f', WHITE, g5),
    6: ('#a8643a', WHITE, g6),
    7: ('#2a8a9a', WHITE, g7),
    8: ('#4f7fc4', WHITE, g8),
    9: ('#7a3e22', WHITE, g9),
    10: ('#4a2e22', WHITE, g10),
    11: ('#c8402a', WHITE, g11),
    12: ('#86c9a6', DARK, g12),
    13: ('#4a4440', WHITE, g13),
    14: ('#1f1c1c', WHITE, g14),
    15: ('#6f9db5', WHITE, g15),
    16: ('#6e6863', WHITE, g16),
    17: ('#3d4046', WHITE, g17),
    18: ('#7b5236', WHITE, g18),
    19: ('#8a4a32', WHITE, g19),
    20: ('#1f2b55', WHITE, g20),
    21: ('#8a7f76', WHITE, g21),
    22: ('#66727f', WHITE, g22),
    23: ('#d6a429', DARK, g23),
    24: ('#2f6b4f', WHITE, g24),
    25: ('#9a5a35', WHITE, g25),
    26: ('#d2553a', WHITE, g26),
    27: ('#6a9a45', WHITE, g27),
    28: ('#22688e', WHITE, g28),
    29: ('#3aa6a6', WHITE, g29),
    30: ('#5f9c8f', WHITE, g30),
    31: ('#2c4f9a', WHITE, g31),
    32: ('#6d5d3f', WHITE, g32),
    33: ('#b08a4a', WHITE, g33),
    34: ('#7e868e', WHITE, g34),
    35: ('#2a7fd0', WHITE, g35),
    36: ('#d4622a', WHITE, g36),
    37: ('#6f8a62', WHITE, g37),
}

if __name__ == '__main__':
    only = [int(a) for a in sys.argv[1:]] or sorted(OBJECTS)
    for n in only:
        bg, line, fn = OBJECTS[n]
        path = os.path.join(OUT, f'GRMZK-{n}.svg')
        with open(path, 'w') as f:
            f.write(svg(bg, line, ''.join(fn())))
        subprocess.run(['rsvg-convert', '-w', str(S), '-h', str(S), path, '-o', path[:-4] + '.png'], check=True)
    print('ok', len(only))
