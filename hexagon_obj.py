import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
from shapely.validation import explain_validity
import random
from shapely.affinity import rotate, scale
import hex_structure

class grid:
    def __init__(self, width, height, hex_size, offset_x = 0, offset_y = 0, num = 5, background=True, margin_width=10, margin_height=10):
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.hex_size = hex_size
        self.num = num
        self.background = background
        self.margin_width = margin_width
        self.margin_height = margin_height

        # hex_r_x horizontal length and hex_r_y the vertical
        self.hex_r_y = hex_size * math.sqrt(3) / 2
        self.hex_r_x = hex_size

        #collection of all hexagon obj
        self.grid = []

        # Draw Area without width/height without margin
        self.draw_area = Polygon([(self.margin_width, self.margin_height ), 
                         (self.width - self.margin_width, self.margin_height ), 
                         (self.width - self.margin_width, self.height
                          - self.margin_height ), 
                         (self.margin_width, self.height
                          - self.margin_height )]) 

        #generation of the hexagon center
        #full cover of the width and height
        row_index = 0
        for i in np.arange (0 - self.offset_y, self.height + self.hex_r_y, self.hex_r_y):
            
            x_offset = 0 if row_index % 2 == 0 else 1.5 * self.hex_r_x - self.offset_x

            for j in np.arange(0 - self.offset_x + x_offset, self.width + self.hex_r_x, 3 * self.hex_r_x):
                hex = hex_structure.Hexagon(j, i, self.hex_size)
                self.grid.append(hex)


            row_index += 1



        self.draw_grid_one_colour()

    # a draw mode to get a svg with everything one colour
    def draw_grid_one_colour(self):
        dwg = svgwrite.Drawing("hexagon_obj4.svg", size=("210mm", "297mm"), viewBox=f"0 0 {self.width} {self.height}")
        main_group = dwg.g()

        list_hexagon = []

        # Background
        if self.background:
            dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

        #generation of lines(segments per hexagons, hexagons per grid)
        for hex in self.grid:
            list_hexagon.append(hex.draw_curve_all())

            # would add hexagon outline
            #points, ___ = generate_hexagon_points(hex.center_x, hex.center_y, self.hex_r_x)
            #main_group.add(dwg.polygon(points=points, stroke='white', fill='none', stroke_width=0.5))


        for hexagon in list_hexagon:
            for segment in hexagon:
                for line in segment:
                    # Stelle sicher, dass `line` ein `LineString` ist
                    line_geom = LineString(line)
                    # Führe die Schnittoperation durch
                    intersection = line_geom.intersection(self.draw_area)
                    
                    # Wenn die Schnittstelle nicht leer ist, füge sie zu SVG hinzu
                    if not intersection.is_empty:
                        # Falls es sich um ein MultiLineString handelt, gehe alle Segmente durch
                        if intersection.geom_type == 'MultiLineString':
                            for seg in intersection.geoms:
                                main_group.add(svgwrite.shapes.Polyline(points=list(seg.coords), stroke='white', fill='none', stroke_width=0.5))
                        # Falls es sich um einen LineString handelt, füge ihn direkt hinzu
                        elif intersection.geom_type == 'LineString':
                            main_group.add(svgwrite.shapes.Polyline(points=list(intersection.coords), stroke='white', fill='none', stroke_width=0.5))

        dwg.add(main_group)
        dwg.save()
        print("SVG gespeichert als hex_grid.svg")



#random.seed(32)
# Maße in mm
a4_width_mm = 210
a4_height_mm = 297
offset_x = 0
offset_y = 0
margin_mm = 10
hex_size = 25  # Außendurchmesser, ggf. in mm anpassen
x=8

grid = grid(a4_width_mm, a4_height_mm, hex_size, offset_y=10)
