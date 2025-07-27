import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
import random
from Hexagon import _Hexagon
from Segment import _Segment

class _Group():
    def __init__(self, id, segment):
        self.id = id  # Group ID
        self.segments = set()  # List of segments in the group
        self.border_segments = set()  # List to hold segmetents at the ends of the group

        if self.segments is not None:
            self.segments.add(segment)  # Add the initial segment if provided
            self.border_segments.add(segment)  # Initialize border segments with the first segment
        
    def add_segment(self, segment, old_end):
        """Add a segment to the group and update open ends."""
        self.segments.add(segment)

        # Update open ends
        self.remove_old_end(old_end)
        self.border_segments.add(segment)

    def add_group(self, group, connecting_end, connecting_end_newgroup):
        """Add another group to this group."""
        for segment in group.segments:
            self.segments.add(segment)
        
        for new_end in group.border_segments:
            self.border_segments.add(new_end)
        
        if len(self.border_segments) == 4:
        # Remove old ends from the border segments
            self.remove_old_end(connecting_end)
            self.remove_old_end(connecting_end_newgroup)
        elif len(group.border_segments) == 2:
            self.remove_old_end(connecting_end_newgroup)
        elif len(group.border_segments) == 1:
            self.remove_old_end(connecting_end)
        else:
            raise ValueError("Ungültige Anzahl von border_segments in der Gruppe!")

    def add_segment_to_group(self, list_segment):
        """Add a list of segments to the group."""
        for segment in list_segment:
            self.segments.add(segment)

    def remove_old_end(self, old_end):
        """Remove an old end from the border segments."""
        if len(self.border_segments) == 1:
            return
        else:
            self.border_segments.discard(old_end)

    def calculate_intersection(self, other_group) -> int:
        """Calculate the intersection between this group and another group."""
        intersection = 0
        for segment in self.segments:
            for other_segment in other_group.segments:
                if segment.id == other_segment.id:
                    intersection += 1
        return intersection

    def test_segment(self, segment):
        """Test if the segment can be added to the group."""
        for segment_border in self.border_segments:
            # Check if the segment connects to an open line 0
            if segment_border.id_y % 2 == 1:
                if (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x + 1) == segment.id_x and segment_border.connection[0]== 0:
                    if segment.connection[0]== 3 or segment.connection[1] == 3:
                        return True, segment_border
                # Check if the segment connects to an open line 1
                elif (segment_border.id_y + 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[0] == 1:
                    if segment.connection[0]== 4 or segment.connection[1] == 4:
                        return True, segment_border
                # Check if the segment connects to an open line 2
                elif (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x - 0) == segment.id_x and segment_border.connection[0] == 2:
                    if segment.connection[0]== 5 or segment.connection[1] == 5:
                        return True, segment_border
                # Check if the segment connects to an open line 3
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x - 0) == segment.id_x and segment_border.connection[0] == 3:
                    if segment.connection[0]== 0 or segment.connection[1] == 0:
                        return True, segment_border
                # Check if the segment connects to an open line 4
                elif (segment_border.id_y - 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[0] == 4:
                    if segment.connection[0]== 1 or segment.connection[1] == 1:
                        return True, segment_border
                # Check if the segment connects to an open line 5
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x + 1) == segment.id_x and segment_border.connection[0] == 5:
                    if segment.connection[0]== 2 or segment.connection[1] == 2:
                        return True, segment_border
                elif (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x + 1) == segment.id_x and segment_border.connection[1]== 0:
                    if segment.connection[0]== 3 or segment.connection[1] == 3:
                        return True, segment_border
                # Check if the segment connects to an open line 1
                elif (segment_border.id_y + 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[1] == 1:
                    if segment.connection[0]== 4 or segment.connection[1] == 4:
                        return True, segment_border
                # Check if the segment connects to an open line 2
                elif (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x - 0) == segment.id_x and segment_border.connection[1] == 2:
                    if segment.connection[0]== 5 or segment.connection[1] == 5:
                        return True, segment_border
                # Check if the segment connects to an open line 3
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x - 0) == segment.id_x and segment_border.connection[1] == 3:
                    if segment.connection[0]== 0 or segment.connection[1] == 0:
                        return True, segment_border
                # Check if the segment connects to an open line 4
                elif (segment_border.id_y - 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[1] == 4:
                    if segment.connection[0]== 1 or segment.connection[1] == 1:
                        return True, segment_border
                # Check if the segment connects to an open line 5
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x + 1) == segment.id_x and segment_border.connection[1] == 5:
                    if segment.connection[0]== 2 or segment.connection[1] == 2:
                        return True, segment_border
                    
            elif segment_border.id_y % 2 == 0:
                if (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[0]== 0:
                    if segment.connection[0]== 3 or segment.connection[1] == 3:
                        return True, segment_border
                # Check if the segment connects to an open line 1
                elif (segment_border.id_y + 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[0] == 1:
                    if segment.connection[0]== 4 or segment.connection[1] == 4:
                        return True, segment_border
                # Check if the segment connects to an open line 2
                elif (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x - 1) == segment.id_x and segment_border.connection[0] == 2:
                    if segment.connection[0]== 5 or segment.connection[1] == 5:
                        return True, segment_border
                # Check if the segment connects to an open line 3
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x - 1) == segment.id_x and segment_border.connection[0] == 3:
                    if segment.connection[0]== 0 or segment.connection[1] == 0:
                        return True, segment_border
                # Check if the segment connects to an open line 4
                elif (segment_border.id_y - 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[0] == 4:
                    if segment.connection[0]== 1 or segment.connection[1] == 1:
                        return True, segment_border
                # Check if the segment connects to an open line 5
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[0] == 5:
                    if segment.connection[0]== 2 or segment.connection[1] == 2:
                        return True, segment_border
                elif (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[1]== 0:
                    if segment.connection[0]== 3 or segment.connection[1] == 3:
                        return True, segment_border
                # Check if the segment connects to an open line 1
                elif (segment_border.id_y + 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[1] == 1:
                    if segment.connection[0]== 4 or segment.connection[1] == 4:
                        return True, segment_border
                # Check if the segment connects to an open line 2
                elif (segment_border.id_y + 1) == segment.id_y and (segment_border.id_x - 1) == segment.id_x and segment_border.connection[1] == 2:
                    if segment.connection[0]== 5 or segment.connection[1] == 5:
                        return True, segment_border
                # Check if the segment connects to an open line 3
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x - 1) == segment.id_x and segment_border.connection[1] == 3:
                    if segment.connection[0]== 0 or segment.connection[1] == 0:
                        return True, segment_border
                # Check if the segment connects to an open line 4
                elif (segment_border.id_y - 2) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[1] == 4:
                    if segment.connection[0]== 1 or segment.connection[1] == 1:
                        return True, segment_border
                # Check if the segment connects to an open line 5
                elif (segment_border.id_y - 1) == segment.id_y and (segment_border.id_x + 0) == segment.id_x and segment_border.connection[1] == 5:
                    if segment.connection[0]== 2 or segment.connection[1] == 2:
                        return True, segment_border
        return False, False
    
    def __repr__(self):
        return f"Group(id={self.id}, segments={len(self.segments)}, border_segments={len(self.border_segments)})"