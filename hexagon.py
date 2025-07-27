import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
from shapely.validation import explain_validity
import random
from shapely.affinity import rotate, scale
from Segment import _Segment



class _Hexagon:
    def __init__(self, center_x, center_y, size, id, offset = False, pattern = False, lines_per_segment = 5):
        self.center_x = center_x
        self.center_y = center_y
        self.center = (self.center_x, self.center_y)
        self.size = size
        self.lines_per_segment = lines_per_segment
        self.id = id  # ID as a list [row, column]
        self.id_x, self.id_y = id
        self.segments = []

        if not offset:
            self.offset = random.randint(0, 5)
        else:
            self.offset = 0

        self.points, self.polygon = self.generate_hexagon_points()
        self.draw_area = self.polygon
        self.points2 = self.points[self.offset:] + self.points[:self.offset]
       



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

        # Create segments based on connections
        # Draw Area from Hexagon and Update it
        for connection in self.connection:
            segment = _Segment(self.id, connection, self.center_x, self.center_y, self.size, self.draw_area, self.points, lines_per_segment=self.lines_per_segment)
            self.draw_area = self.draw_area.difference(segment.get_erase_polygon())
            self.segments.append(segment)

    # calculate hexagon points and returning them as well as the polygon
    def generate_hexagon_points(self, rotation_deg=0):
        """
        Gibt eine Liste von 6 Punkten für ein regelmäßiges, optional gedrehtes Hexagon zurück
        sowie das entsprechende shapely Polygon.
        """
        angle_offset = math.radians(rotation_deg)
        points = []

        for i in range(6):
            angle = angle_offset + i * math.pi / 3  # 60° Schritte
            x = self.center_x + self.size * math.cos(angle)
            y = self.center_y + self.size * math.sin(angle)
            points.append((x, y))

        return points, Polygon(points) 

    def get_curve_all(self):
        #Get all Lines for all segments
        lines = []
        for segment in self.segments:
            lines.append(segment.get_lines())
        return lines
    
    def get_curve_colour(self, id):
        #Get all Lines for all segments with a specific colour
        lines = []
        for segment in self.segments:
            if segment.colour_group == id:
                lines.append(segment.get_lines())
        return lines