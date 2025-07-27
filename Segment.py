import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
import random

class _Segment:
    def __init__(self, id, connection, center_x, center_y, size, draw_area, hexagon_points, lines_per_segment=5, controllpoint=2, margin=0.2):
        self.id = id
        self.id_x, self.id_y = id
        self.connection = connection
        self.center_x = center_x
        self.center_y = center_y
        self.center = (self.center_x, self.center_y)
        self.size = size
        self.lines_per_segment = lines_per_segment
        self.draw_area = draw_area
        self.margin = margin
        self.controllpoint = controllpoint  # Default control point for bezier curves
        self.colour_group = 0

        # Generate the segment based on the connection points
        self.points = hexagon_points
    
        self.draw_curve()


    def get_erase_polygon(self):
        return self.erase_polygon

    def get_lines(self):
        return self.lines

    def draw_curve(self):
        connection_class = (self.connection[0]-self.connection[1]) % 6
        if connection_class == 1 or connection_class == 5:
            return self.curve_neighboring_edges()
        elif connection_class == 2 or connection_class == 4:
            return self.curve_distant_edges()
        elif connection_class == 3:
            return self.curve_opposite_edges()
        else:
             raise ValueError("Ungültiger Wert!")

    def curve_neighboring_edges(self):

        curves = []

        for i in np.linspace(0 + self.margin, 1 - self.margin, self.lines_per_segment):
            p0 = self.lerp_np(self.points[(self.connection[0]+1)%6], self.points[(self.connection[0]+0)%6], i)
            p2 = self.lerp_np(self.points[(self.connection[1]+0)%6], self.points[(self.connection[1]+1)%6], i)

            center_i = self.lerp_np(self.points[(self.connection[0]+1)%6], self.center, self.controllpoint*i)

            
            bezier_line = LineString(self.quadratic_bezier(p0, center_i, p2))
            clipped = bezier_line.intersection(self.draw_area)

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

        self.lines = curves

        # Erzeuge die Kontur für das Clipping    
        contour = [self.points[(self.connection[0]+0)%6], self.points[(self.connection[0]+1)%6], self.points[(self.connection[1]+1)%6]] + self.quadratic_bezier(self.points[(self.connection[1]+1)%6],self.lerp_np(self.points[(self.connection[0]+1)%6], self.center, i*self.controllpoint+self.margin),self.points[(self.connection[0]+0)%6])

        # Polygon bauen
        self.erase_polygon = Polygon(contour)
        if not self.erase_polygon.is_valid:
            print("→ Fehlerhafte Kontur repariert mit buffer(0)")
            self.erase_polygon = self.erase_polygon.buffer(0)

    def curve_distant_edges(self):

        curves = []

        for i in np.linspace(0 + self.margin, 1 - self.margin, self.lines_per_segment):
            p0 = self.lerp_np(self.points[(self.connection[0]+1)%6], self.points[(self.connection[0]+0)%6], i)
            p2 = self.lerp_np(self.points[(self.connection[1]+0)%6], self.points[(self.connection[1]+1)%6], i)

            center_i = self.lerp_np(self.lerp_np(self.points[(self.connection[0]+1)%6], self.points[(self.connection[1]+0)%6],0.5),self.center, (self.controllpoint-0.6)*i+ 0.3)

            line = LineString(self.quadratic_bezier(p0, center_i, p2))
            clipped = line.intersection(self.draw_area)


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

        self.lines = curves

        # Erzeuge die Kontur für das Clipping    
        contour = [self.points[(self.connection[0]+0)%6]]

        control = self.lerp_np(self.lerp_np(self.points[(self.connection[0]+1)%6], self.points[(self.connection[1]+0)%6],0.5), self.center, (self.controllpoint-0.6)*1+ self.margin)
        bezier_back = self.quadratic_bezier(self.points[(self.connection[0]+0)%6], control, self.points[(self.connection[1]+1)%6])
        contour += bezier_back[1:]

        contour += [self.points[(self.connection[1]+1)%6]]

        control = self.lerp_np(self.lerp_np(self.points[(self.connection[0]+1)%6], self.points[(self.connection[1]+0)%6],0.5), self.center, (self.controllpoint-0.6)*0 + 0.35)
        bezier_back = self.quadratic_bezier(self.points[(self.connection[1]+0)%6], control, self.points[(self.connection[0]+1)%6])
        contour += bezier_back[1:]

        contour += [self.points[(self.connection[0]+1)%6]]

        # Polygon bauen
        self.erase_polygon = Polygon(contour)
        if not self.erase_polygon.is_valid:
            print("→ Fehlerhafte Kontur repariert mit buffer(0)")
            self.erase_polygon = self.erase_polygon.buffer(0)

    def curve_opposite_edges(self):

        curves = []

        for i in np.linspace(0 + self.margin, 1-self.margin, self.lines_per_segment):
            p0 = self.lerp_np(self.points[(self.connection[0]+0)%6], self.points[(self.connection[0]+1)%6], i)
            p2 = self.lerp_np(self.points[(self.connection[1]+1)%6], self.points[(self.connection[1]+0)%6], i) 

            line = LineString([p0,p2])
            clipped = line.intersection(self.draw_area)
            
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

        self.lines = curves

        # Erzeuge die Kontur für das Clipping    
        contour = [self.points[(self.connection[0]+0)%6], self.points[(self.connection[0]+1)%6], self.points[(self.connection[1]+0)%6], self.points[(self.connection[1]+1)%6]]

        # Polygon bauen
        self.erase_polygon = Polygon(contour)
        if not self.erase_polygon.is_valid:
            print("→ Fehlerhafte Kontur repariert mit buffer(0)")
            self.erase_polygon = self.erase_polygon.buffer(0)

    def quadratic_bezier(self, p0, p1, p2, num=90):
        t = np.linspace(0, 1, num)
        return [( (1 - tt)**2 * p0[0] + 2 * (1 - tt) * tt * p1[0] + tt**2 * p2[0],
                (1 - tt)**2 * p0[1] + 2 * (1 - tt) * tt * p1[1] + tt**2 * p2[1]) for tt in t]

    def lerp_np(self, p0, p1, t):
        p0 = np.array(p0)
        p1 = np.array(p1)
        return tuple(p0 + t * (p1 - p0))

    def __repr__(self):
        return f"Segment(id={self.id}, connection={self.connection})"