import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
from shapely.validation import explain_validity
import random
from shapely.affinity import rotate, scale


def quadratic_bezier(p0, p1, p2, num=90):
    """Gibt Punkte einer quadratischen Bézier-Kurve zurück"""
    t = np.linspace(0, 1, num)
    return [( (1 - tt)**2 * p0[0] + 2 * (1 - tt) * tt * p1[0] + tt**2 * p2[0],
              (1 - tt)**2 * p0[1] + 2 * (1 - tt) * tt * p1[1] + tt**2 * p2[1]) for tt in t]

def lerp_np(p0, p1, t):
    p0 = np.array(p0)
    p1 = np.array(p1)
    return tuple(p0 + t * (p1 - p0))

def generate_hexagon_points(center_x, center_y, size, rotation_deg=0):
    """
    Gibt eine Liste von 6 Punkten für ein regelmäßiges, optional gedrehtes Hexagon zurück
    sowie das entsprechende shapely Polygon.
    """
    angle_offset = math.radians(rotation_deg)
    points = []

    for i in range(6):
        angle = angle_offset + i * math.pi / 3  # 60° Schritte
        x = center_x + size * math.cos(angle)
        y = center_y + size * math.sin(angle)
        points.append((x, y))

    return points, Polygon(points)

def curve_neighboring_edges(points, center, clip_area, num, controllpoint=2):
    """
    Erzeugt Bézier-Kurven zwischen benachbarten Kanten eines Hexagons.
    Die Kurven verlaufen von einem Punkt zur Mitte des Hexagons und zurück.
    """
    curves = []

    for i in np.linspace(0, 1, num):
        p0 = lerp_np(points[1], points[0], i)
        p2 = lerp_np(points[1], points[2], i)

        center_i = lerp_np(points[1], center, controllpoint*i)

        
        bezier_line = LineString(quadratic_bezier(p0, center_i, p2))
        clipped = bezier_line.intersection(clip_area)

        if clipped.is_empty:
            pass  
        elif clipped.geom_type == 'LineString':
            curves.append(list(clipped.coords))
        elif clipped.geom_type == 'MultiLineString':
            for seg in clipped.geoms:
                curves.append(list(seg.coords))
        elif clipped.geom_type == 'GeometryCollection':
            for geom in clipped.geoms:
                if not geom.is_empty and isinstance(geom, LineString):
                    curves.append(list(geom.coords))

    # Erzeuge die Kontur für das Clipping    
    contour = [points[0], points[1], points[2]] + quadratic_bezier( points[2],lerp_np(points[1], center, i*controllpoint),points[0])

    # Polygon bauen
    erase_polygon = Polygon(contour)
    if not erase_polygon.is_valid:
        print("→ Fehlerhafte Kontur repariert mit buffer(0)")
        erase_polygon = erase_polygon.buffer(0)

    new_area = clip_area.difference(erase_polygon)
    if not new_area.is_valid:
        new_area = new_area.buffer(0)
    return curves, clip_area.difference(erase_polygon)

def curve_distant_edges(points, center, clip_area, num, controllpoint=2):
    """
    Erzeugt Bézier-Kurven zwischen benachbarten Kanten eines Hexagons.
    Die Kurven verlaufen von einem Punkt zur Mitte des Hexagons und zurück.
    """
    curves = []

    for i in np.linspace(0, 1, num):
        p0 = lerp_np(points[1], points[0], i)
        p2 = lerp_np(points[2], points[3], i)

        center_i = lerp_np(lerp_np(points[1], points[2],0.5), center, (controllpoint-0.6)*i+ 0.3)

        line = LineString(quadratic_bezier(p0, center_i, p2))
        clipped = line.intersection(clip_area)


        if clipped.is_empty:
            pass  
        elif clipped.geom_type == 'LineString':
            curves.append(list(clipped.coords))
        elif clipped.geom_type == 'MultiLineString':
            curves.extend([list(seg.coords) for seg in clipped.geoms])
        elif clipped.geom_type == 'GeometryCollection':
            for geom in clipped.geoms:
                if not geom.is_empty and isinstance(geom, LineString):
                    curves.append(list(geom.coords))

    # Erzeuge die Kontur für das Clipping    
    contour = [points[0]]

    control = lerp_np(lerp_np(points[1], points[2],0.5), center, (controllpoint-0.6)*1+ 0.3)
    bezier_back = quadratic_bezier(points[0], control, points[3])
    contour += bezier_back[1:]

    contour += [points[2]]

    control = lerp_np(lerp_np(points[1], points[2],0.5), center, (controllpoint-0.6)*0 + 0.3)
    bezier_back = quadratic_bezier(points[2], control, points[1])
    contour += bezier_back[1:]

    contour += [points[1]]

    # Polygon bauen
    erase_polygon = Polygon(contour)
    if not erase_polygon.is_valid:
        print("→ Fehlerhafte Kontur repariert mit buffer(0)")
        erase_polygon = erase_polygon.buffer(0)

    new_area = clip_area.difference(erase_polygon)
    if not new_area.is_valid:
        new_area = new_area.buffer(0)
    return curves, new_area

def curve_opposite_edges(points, center, clip_area, num, controllpoint=2):
    """
    Erzeugt Bézier-Kurven zwischen gegenüberliegenden Kanten eines Hexagons.
    Die Kurven verlaufen von einem Punkt zur Mitte des Hexagons und zurück.
    """
    curves = []

    for i in np.linspace(0, 1, num):
        p0 = lerp_np(points[0], points[1], i)
        p2 = lerp_np(points[3], points[2], i) 

        
        line = LineString([p0,p2])
        clipped = line.intersection(clip_area)
        
        
        if clipped.is_empty:
            pass  
        elif clipped.geom_type == 'LineString':
            curves.append(list(clipped.coords))
        elif clipped.geom_type == 'MultiLineString':
            curves.extend([list(seg.coords) for seg in clipped.geoms])
        elif clipped.geom_type == 'GeometryCollection':
            for geom in clipped.geoms:
                if not geom.is_empty and isinstance(geom, LineString):
                    curves.append(list(geom.coords))

    # Erzeuge die Kontur für das Clipping    
    contour = [points[0], points[1], points[2], points[3]]

    # Polygon bauen
    erase_polygon = Polygon(contour)
    if not erase_polygon.is_valid:
        print("→ Fehlerhafte Kontur repariert mit buffer(0)")
        erase_polygon = erase_polygon.buffer(0)


    return curves, clip_area.difference(erase_polygon) 



def draw_hex_pattern_1(parent_group, center_x, center_y, size, draw_area, num, rotation_deg=0, controllpoint = 2):
    """Hexagon mit paarweisen Verbindungen benachbarter Kanten zeichnen"""

    pattern_group = svgwrite.container.Group()
    center = (center_x, center_y)

    points, ___ = generate_hexagon_points(center_x, center_y, size, rotation_deg)
    offset = random.randint(0, 5)
    points = points[offset:] + points[:offset] 

    for i in (0, 2, 4):
        point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 2) % 6]]
        curves, draw_area = curve_neighboring_edges(point_pattern, center, draw_area, num, controllpoint)
        for curve in curves:
            pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))

    #dwg.add(dwg.polygon(list(hexagon.exterior.coords), fill='none', stroke='white', stroke_width=1))
    parent_group.add(pattern_group)
    return draw_area

def draw_hexagon_2(parent_group, center_x, center_y, size, draw_area, num, rotation_deg=0,  controllpoint = 2):
    """Hexagon mit  einer Verbindungen benachbarter Kanten und die andere Kreuzend"""

    center = (center_x, center_y)
    points, ___ = generate_hexagon_points(center_x, center_y, size, rotation_deg)
    offset = random.randint(0, 5)
    points = points[offset:] + points[:offset]
    pattern_group = svgwrite.container.Group()

    # Zeichnen des Muster
    indices = [0, 2, 4]
    random.shuffle(indices)
    for i in indices:
        if i == 0:
            point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 2) % 6]]
            curves, draw_area = curve_neighboring_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))
        elif i == 2:
            point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 2) % 6], points[(i + 3) % 6]]
            curves, draw_area = curve_distant_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))
        elif i == 4:
            point_pattern = [points[(i - 1) % 6], points[i % 6], points[(i + 1) % 6], points[(i + 2) % 6]]
            curves, draw_area = curve_distant_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))

    parent_group.add(pattern_group)
    #dwg.add(dwg.polygon(list(hexagon.exterior.coords), fill='none', stroke='white', stroke_width=1))
    return draw_area

def draw_hexagon_3(parent_group, center_x, center_y, size, draw_area, num,rotation_deg=0, controllpoint=2):
    center = (center_x, center_y)
    points, ___ = generate_hexagon_points(center_x, center_y, size, rotation_deg)
    offset = random.randint(0, 5)
    points = points[offset:] + points[:offset]
    
    pattern_group = svgwrite.container.Group()
    
    for i in (0, 2, 4):
        point_pattern = [
            points[(i + 0) % 6],
            points[(i + 1) % 6],
            points[(i + 3) % 6],
            points[(i + 4) % 6],
        ]
        curves, draw_area = curve_opposite_edges(point_pattern, center, draw_area, num, controllpoint)
        for curve in curves:
            pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))

    
    parent_group.add(pattern_group)

    return draw_area

def draw_hexagon_4(parent_group, center_x, center_y, size, draw_area, num, rotation_deg=0, controllpoint=2):
    center = (center_x, center_y)
    points, ___ = generate_hexagon_points(center_x, center_y, size, rotation_deg)
    offset = random.randint(0, 5)
    points = points[offset:] + points[:offset]
    pattern_group = svgwrite.container.Group()

    indices = [0, 2, 4]
    random.shuffle(indices)
    for i in indices:
        if i == 0:
            point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 2) % 6]]
            curves, draw_area = curve_neighboring_edges(point_pattern, center, draw_area,num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))
        elif i == 2:
            point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 3) % 6], points[(i + 4) % 6]]
            curves, draw_area = curve_opposite_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))
        elif i == 4:
            point_pattern = [points[(i - 1) % 6], points[i % 6], points[(i + 1) % 6]]
            curves, draw_area = curve_neighboring_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))

    
    parent_group.add(pattern_group)
    return draw_area

def draw_hexagon_5(parent_group, center_x, center_y, size, draw_area, num, rotation_deg=0, controllpoint=2):
    center = (center_x, center_y)
    points, ___ = generate_hexagon_points(center_x, center_y, size, rotation_deg)
    offset = random.randint(0, 5)
    points = points[offset:] + points[:offset]

    pattern_group = svgwrite.container.Group()
    draw_area = draw_area

    indices = [0, 2, 4]
    random.shuffle(indices)
    for i in indices:
        if i == 4:
            point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 2) % 6], points[(i + 3) % 6]]
            curves, draw_area = curve_distant_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))
        elif i == 2:
            point_pattern = [points[(i + 0) % 6], points[(i + 1) % 6], points[(i + 3) % 6], points[(i + 4) % 6]]
            curves, draw_area = curve_opposite_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))
        elif i == 0:
            point_pattern = [points[(i + 1) % 6], points[(i + 2) % 6], points[(i + 3) % 6], points[(i + 4) % 6]]
            curves, draw_area = curve_distant_edges(point_pattern, center, draw_area, num, controllpoint)
            for curve in curves:
                pattern_group.add(svgwrite.shapes.Polyline(points=curve, stroke='white', fill='none', stroke_width=0.5))

    parent_group.add(pattern_group)
    return draw_area


def make_grid(dwg, grid_width, grid_height, hex_size, num=5, offset_x=0, offset_y=0, background=True):
    """Erzeugt ein versetztes Hexagon-Raster mit Rand"""
    main_group = dwg.g()
    count = 0
    y = -hex_size

    # Hintergrund hinzufügen, falls gewünscht
    if background:
        dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

    draw_area = Polygon([(offset_x, offset_y), 
                         (grid_width - offset_x, offset_y), 
                         (grid_width - offset_x, grid_height
                          - offset_y), 
                         (offset_x, grid_height
                          - offset_y)])   

    hex_height = hex_size * math.sqrt(3) / 2
    vertical_step = hex_height * 0.75

    while y < grid_height + vertical_step:
        x = 0
        while x < grid_width:
            offset = hex_size * 0.75 if count % 2 == 0 else 0

            # Zufällige Auswahl eines der 5 Muster mit Gewichtung
            pattern = random.choices(
                population=[1, 2, 3, 4, 5],
                weights=[100,100,100, 100, 100],
                k=1
            )[0]

            cx = x + offset + offset_x
            cy = y + offset_y

            if pattern == 1:
                draw_area = draw_hex_pattern_1(main_group, cx, cy, hex_size / 2, draw_area, num, rotation_deg=0)
            elif pattern == 2:
                draw_area = draw_hexagon_2(main_group, cx, cy, hex_size / 2, draw_area,num, rotation_deg=0)
            elif pattern == 3:
                draw_area = draw_hexagon_3(main_group, cx, cy, hex_size / 2, draw_area,num, rotation_deg=0)
            elif pattern == 4:
                draw_area = draw_hexagon_4(main_group, cx, cy, hex_size / 2, draw_area,num,rotation_deg=0)
            elif pattern == 5:
                draw_area = draw_hexagon_5(main_group, cx, cy, hex_size / 2, draw_area ,num, rotation_deg=0)


            x += hex_size * 1.5
        y += hex_size / 2.3
        count += 1

    # Wenn ein Clip definiert ist, die gesamte Gruppe clippen

    dwg.add(main_group)

        
random.seed(32)
# Maße in mm
a4_width_mm = 210
a4_height_mm = 297
margin_mm = 5
hex_size = 45  # Außendurchmesser, ggf. in mm anpassen
x=7

# SVG erstellen mit A4-Größe
dwg = svgwrite.Drawing("hex_grid.svg", size=("210mm", "297mm"), viewBox=f"0 0 {a4_width_mm} {a4_height_mm}")

# Raster generieren und clip anwenden
make_grid(dwg, grid_width=a4_width_mm, grid_height=a4_height_mm, hex_size=hex_size, offset_x=margin_mm, offset_y=margin_mm,num=x)

# SVG speichern
dwg.save()
print("SVG gespeichert als hex_grid.svg")
