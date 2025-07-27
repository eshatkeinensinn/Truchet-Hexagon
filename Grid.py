import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
import random
from Hexagon import _Hexagon
from Colouring import _Colouring


class _Grid():

    def __init__(self, width, height, hex_size, offset_x = 10, offset_y = 0, lines_per_segment = 5, background=True, margin_width=10, margin_height=10, hexagon_margin=0.2):
        """
        Initialize a grid with the given parameters.
        """
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.hex_size = hex_size
        self.lines_per_segment = lines_per_segment
        self.background = background
        self.margin_width = margin_width
        self.margin_height = margin_height
        self.hexagon_margin = hexagon_margin

        # hex_r_x horizontal length and hex_r_y the vertical
        self.hex_r_y = hex_size * math.sqrt(3) / 2
        self.hex_r_x = hex_size

        #collection of all hexagon obj
        self.grid = []

        # Draw Area with margin
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
            
            x_offset = 0 if row_index % 2 == 0 else 1.5 * self.hex_r_x

            for j in np.arange(0 - self.offset_x + x_offset, self.width + self.hex_r_x, 3 * self.hex_r_x):
                id = [round((j + self.offset_x - x_offset) / (3 * self.hex_r_x)),round((i + self.offset_y) / self.hex_r_y),]
                hex = _Hexagon(j, i, self.hex_size,id, lines_per_segment=self.lines_per_segment, margin=self.hexagon_margin)
                self.grid.append(hex)


            row_index += 1

    #draw mode to get a svg with every segment in one colour
    def draw_grid_one_colour(self):
        dwg = svgwrite.Drawing("hexagon_one_colour.svg", size=("210mm", "297mm"), viewBox=f"0 0 {self.width} {self.height}")
        main_group = dwg.g()

        list_hexagon = []

        # Background
        if self.background:
            dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

        #generation of lines(segments per hexagons, hexagons per grid)
        for hex in self.grid:
            hexagon_lines = hex.get_curve_all()
            for segment_lines in hexagon_lines:
                for line in segment_lines:
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

        #Add id of hexagon in center of hexagon
        #for hexagon in self.grid:
        #    center_x, center_y = hexagon.center
        #    dwg.add(dwg.text(str(hexagon.id), insert=(center_x, center_y), fill='white', font_size='5px', text_anchor='middle'))


        dwg.add(main_group)
        dwg.save()


    def draw_grid_coloured(self):
        dwg = svgwrite.Drawing("hexagon_obj_coloured.svg", size=("210mm", "297mm"), viewBox=f"0 0 {self.width} {self.height}")
        main_group = dwg.g()

        colouring = _Colouring(grid.grid)
        list_hexagon = []

        # Background
        if self.background:
            dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

        COLORS = ['seagreen', 'red', 'skyblue', 'white', 'purple',
        'orange', 'cyan', 'magenta', 'brown', 'gray', 'black']



        #generation of lines(segments per hexagons, hexagons per grid)
        for id_val in range(0,11):
            color = COLORS[id_val] if id_val < len(COLORS) else 'black'
            for hex in self.grid:
                hexagon_lines = hex.get_curve_colour(id_val)
                for segment_lines in hexagon_lines:
                    for line in segment_lines:
                        # Stelle sicher, dass `line` ein `LineString` ist
                        line_geom = LineString(line)
                        # Führe die Schnittoperation durch
                        intersection = line_geom.intersection(self.draw_area)
                        
                        # Wenn die Schnittstelle nicht leer ist, füge sie zu SVG hinzu
                        if not intersection.is_empty:
                            # Falls es sich um ein MultiLineString handelt, gehe alle Segmente durch
                            if intersection.geom_type == 'MultiLineString':
                                for seg in intersection.geoms:
                                    main_group.add(svgwrite.shapes.Polyline(points=list(seg.coords), stroke=color, fill='none', stroke_width=0.5))
                            # Falls es sich um einen LineString handelt, füge ihn direkt hinzu
                            elif intersection.geom_type == 'LineString':
                                main_group.add(svgwrite.shapes.Polyline(points=list(intersection.coords), stroke=color, fill='none', stroke_width=0.5))

        dwg.add(main_group)
        dwg.save()


        # Save a seprate SVG for each colour group
        for id_val in range(0,11):
            color = COLORS[id_val] if id_val < len(COLORS) else 'black'
            dwg = svgwrite.Drawing(f"hexagon_obj_coloured_{id_val}.svg", size=("210mm", "297mm"), viewBox=f"0 0 {self.width} {self.height}")
            main_group = dwg.g()

            # Background
            if self.background:
                dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

            for hex in self.grid:
                hexagon_lines = hex.get_curve_colour(id_val)
                for segment_lines in hexagon_lines:
                    for line in segment_lines:
                        # Stelle sicher, dass `line` ein `LineString` ist
                        line_geom = LineString(line)
                        # Führe die Schnittoperation durch
                        intersection = line_geom.intersection(self.draw_area)
                        
                        # Wenn die Schnittstelle nicht leer ist, füge sie zu SVG hinzu
                        if not intersection.is_empty:
                            # Falls es sich um ein MultiLineString handelt, gehe alle Segmente durch
                            if intersection.geom_type == 'MultiLineString':
                                for seg in intersection.geoms:
                                    main_group.add(svgwrite.shapes.Polyline(points=list(seg.coords), stroke=color, fill='none', stroke_width=0.5))
                            # Falls es sich um einen LineString handelt, füge ihn direkt hinzu
                            elif intersection.geom_type == 'LineString':
                                main_group.add(svgwrite.shapes.Polyline(points=list(intersection.coords), stroke=color, fill='none', stroke_width=0.5))

            # Check if the main group has any elements befor saving
            if main_group.elements:
                dwg.add(main_group)
                dwg.save()




random.seed(1256)
# Maße in mm
a4_width_mm = 210
a4_height_mm = 297
offset_x = 0
offset_y = 0
margin_mm = 10
hex_size = 20  # Außendurchmesser, ggf. in mm anpassen
x=8

grid = _Grid(a4_width_mm, a4_height_mm, hex_size, offset_y=10, background=True, hexagon_margin=0.15)
grid.draw_grid_one_colour()
grid.draw_grid_coloured()
print("ggs")
