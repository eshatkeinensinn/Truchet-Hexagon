import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
from shapely.validation import explain_validity
import random
from shapely.affinity import rotate, scale


class grid:
    def __init__(self, width, height, offset_x, offset_y, hex_size, num = 5, background=True, margin_width=10, margin_height=10):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.hex_size = hex_size
        self.num = num
        self.background = background
        self.margin_width = margin_width
        self.margin_height = margin_height

        self.hex_r_y = hex_size * math.sqrt(3) / 2
        self.hex_r_x = hex_size
        self.grid = []

      
        row_index = 0
        for i in np.arange (0 - self.offset_y, self.height + self.hex_r_y, self.hex_r_y):
            
            cy = i + self.offset_y

            for j in np.arange(0 - self.offset_x, self.width + self.hex_r_x, 3 * self.hex_r_x):
                
                offset = self.hex_r_x + self.hex_r_x/2 if row_index % 2 == 0 else 0
                cx = j + offset + self.offset_x
                
                self.grid.append((cx, cy))

            row_index += 1

        self.draw_grid_one_colour()

    
    def draw_grid_one_colour(self):
        dwg = svgwrite.Drawing("hexagon_obj.svg", size=("210mm", "297mm"), viewBox=f"0 0 {self.width} {self.height}")
        main_group = dwg.g()

        if self.background:
            dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

        for cx, cy in self.grid:
            points, ___ = generate_hexagon_points(cx, cy, self.hex_r_x)
            main_group.add(dwg.polygon(points=points, stroke='white', fill='none', stroke_width=0.5))


        dwg.add(main_group)
        dwg.save()
        print("SVG gespeichert als hex_grid.svg")


class Hexagon:
    def __init__(self, center_x, center_y, size, offset = 0, pattern = "none"):
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.offset = offset
        self.pattern = pattern

        self.points, self.polygon = generate_hexagon_points(center_x, center_y, size)

        if pattern == "none":
            self.pattern = random.choices(population=[1, 2, 3, 4, 5],weights=[100,100,100, 100, 100],k=1)[0]







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

#random.seed(32)
# Maße in mm
a4_width_mm = 210
a4_height_mm = 297
offset_x = 10
offset_y = 10
margin_mm = 10
hex_size = 40  # Außendurchmesser, ggf. in mm anpassen
x=8

grid = grid(a4_width_mm, a4_height_mm, offset_x, offset_y, hex_size)
