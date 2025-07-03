import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
from shapely.validation import explain_validity
import random
from shapely.affinity import rotate, scale


# calculate hexagon points and returning them as well as the polygon
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



class Hexagon:
    def __init__(self, center_x, center_y, size, offset = False, pattern = False, num = 5):
        self.center_x = center_x
        self.center_y = center_y
        self.center = (self.center_x, self.center_y)
        self.size = size
        self.num = num
        
        if not offset:
            self.offset = random.randint(0, 5)
        else:
            self.offset = offset
        
        self.points, self.polygon = generate_hexagon_points(center_x, center_y, size)
        self.draw_area = self.polygon
        self.points2 = self.points[self.offset:] + self.points[:self.offset]
        self.lines = []



        if not pattern :
            self.pattern = random.choices(population=[1, 2, 3, 4, 5],weights=[100,100,100, 100, 100],k=1)[0]
        else: 
            self.pattern = pattern
        
        if self.pattern == 1:
            self.connection = [[(0 + self.offset) % 6,(1 + self.offset) % 6],[(2 + self.offset) % 6,(3 + self.offset) % 6],[(4 + self.offset) % 6,(5 + self.offset) % 6]]
        elif self.pattern == 2:
            self.connection = [[(0 + self.offset) % 6,(1 + self.offset) % 6],[(2 + self.offset) % 6,(4 + self.offset) % 6],[(3 + self.offset) % 6,(5 + self.offset) % 6]]
        elif self.pattern == 3:
            self.connection = [[(0 + self.offset) % 6,(3 + self.offset) % 6],[(1 + self.offset) % 6,(4 + self.offset) % 6],[(2 + self.offset) % 6,(5 + self.offset) % 6]]
        elif self.pattern == 4:
            self.connection = [[(0 + self.offset) % 6,(1 + self.offset) % 6],[(2 + self.offset) % 6,(5 + self.offset) % 6],[(3 + self.offset) % 6,(4 + self.offset) % 6]]
        elif self.pattern == 5:
            self.connection = [[(0 + self.offset) % 6,(2 + self.offset) % 6],[(1 + self.offset) % 6,(4 + self.offset) % 6],[(3 + self.offset) % 6,(5 + self.offset) % 6]]
        else:
            raise ValueError("Ungültiger Wert!")
        
        random.shuffle(self.connection)


    def quadratic_bezier(self, p0, p1, p2, num=90):
        t = np.linspace(0, 1, num)
        return [( (1 - tt)**2 * p0[0] + 2 * (1 - tt) * tt * p1[0] + tt**2 * p2[0],
                (1 - tt)**2 * p0[1] + 2 * (1 - tt) * tt * p1[1] + tt**2 * p2[1]) for tt in t]

    def lerp_np(self, p0, p1, t):
        p0 = np.array(p0)
        p1 = np.array(p1)
        return tuple(p0 + t * (p1 - p0))


    def draw_curve_all(self):
        curves = []
        for connection in self.connection:
            curves.append(self.draw_curve(connection))
        return curves
        

    def draw_curve(self, connection_single):
        connection_class = (connection_single[0]-connection_single[1]) % 6
        if connection_class == 1 or connection_class == 5:
            print("Connection class is " + str(connection_class) )
            return self.curve_neighboring_edges(connection_single)
        elif connection_class == 2 or connection_class == 4:
            return self.curve_distant_edges(connection_single)
        elif connection_class == 3:
            return self.curve_opposite_edges(connection_single)
        else:
             raise ValueError("Ungültiger Wert!")


    def curve_neighboring_edges(self, connection_single, controllpoint=2):

        curves = []

        for i in np.linspace(0, 1, self.num):
            p0 = self.lerp_np(self.points[(connection_single[0]+1)%6], self.points[(connection_single[0]+0)%6], i)
            p2 = self.lerp_np(self.points[(connection_single[1]+0)%6], self.points[(connection_single[1]+1)%6], i)

            center_i = self.lerp_np(self.points[(connection_single[0]+1)%6], self.center, controllpoint*i)

            
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

        # Erzeuge die Kontur für das Clipping    
        contour = [self.points[(connection_single[0]+0)%6], self.points[(connection_single[0]+1)%6], self.points[(connection_single[1]+1)%6]] + self.quadratic_bezier(self.points[(connection_single[1]+1)%6],self.lerp_np(self.points[(connection_single[0]+1)%6], self.center, i*controllpoint),self.points[(connection_single[0]+0)%6])

        # Polygon bauen
        erase_polygon = Polygon(contour)
        if not erase_polygon.is_valid:
            print("→ Fehlerhafte Kontur repariert mit buffer(0)")
            erase_polygon = erase_polygon.buffer(0)

        self.draw_area = self.draw_area.difference(erase_polygon)
        return curves



    def curve_distant_edges(self, connection_single, controllpoint = 2):

        curves = []

        for i in np.linspace(0, 1, self.num):
            p0 = self.lerp_np(self.points[(connection_single[0]+1)%6], self.points[(connection_single[0]+0)%6], i)
            p2 = self.lerp_np(self.points[(connection_single[1]+0)%6], self.points[(connection_single[1]+1)%6], i)

            center_i = self.lerp_np(self.lerp_np(self.points[(connection_single[0]+1)%6], self.points[(connection_single[1]+0)%6],0.5),self.center, (controllpoint-0.6)*i+ 0.3)

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

        # Erzeuge die Kontur für das Clipping    
        contour = [self.points[(connection_single[0]+0)%6]]

        control = self.lerp_np(self.lerp_np(self.points[(connection_single[0]+1)%6], self.points[(connection_single[1]+0)%6],0.5), self.center, (controllpoint-0.6)*1+ 0.3)
        bezier_back = self.quadratic_bezier(self.points[(connection_single[0]+0)%6], control, self.points[(connection_single[1]+1)%6])
        contour += bezier_back[1:]

        contour += [self.points[(connection_single[1]+1)%6]]

        control = self.lerp_np(self.lerp_np(self.points[(connection_single[0]+1)%6], self.points[(connection_single[1]+0)%6],0.5), self.center, (controllpoint-0.6)*0 + 0.3)
        bezier_back = self.quadratic_bezier(self.points[(connection_single[1]+0)%6], control, self.points[(connection_single[0]+1)%6])
        contour += bezier_back[1:]

        contour += [self.points[(connection_single[0]+1)%6]]

        # Polygon bauen
        erase_polygon = Polygon(contour)
        if not erase_polygon.is_valid:
            print("→ Fehlerhafte Kontur repariert mit buffer(0)")
            erase_polygon = erase_polygon.buffer(0)

        self.draw_area = self.draw_area.difference(erase_polygon)
        return curves


    def curve_opposite_edges(self, connection_single):

        curves = []

        for i in np.linspace(0, 1, self.num):
            p0 = self.lerp_np(self.points[(connection_single[0]+0)%6], self.points[(connection_single[0]+1)%6], i)
            p2 = self.lerp_np(self.points[(connection_single[1]+1)%6], self.points[(connection_single[1]+0)%6], i) 

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

        # Erzeuge die Kontur für das Clipping    
        contour = [self.points[(connection_single[0]+0)%6], self.points[(connection_single[0]+1)%6], self.points[(connection_single[1]+0)%6], self.points[(connection_single[1]+1)%6]]

        # Polygon bauen
        erase_polygon = Polygon(contour)
        if not erase_polygon.is_valid:
            print("→ Fehlerhafte Kontur repariert mit buffer(0)")
            erase_polygon = erase_polygon.buffer(0)

        self.draw_area = self.draw_area.difference(erase_polygon)
        return curves
