import math
import numpy as np
from shapely.geometry import Polygon
import hex_structure
import random
import copy


class Line:
    """Class to represent a outer line in a hexagonal grid. For Example [14,2] with outer line 4."""
    def __init__(self, id, outer_line):
        self.id = id  # Hexagon ID
        self.id_y = id[1]  # Y coordinate of the hexagon
        self.id_x = id[0]  # X coordinate of the hexagon
        self.outer_line = outer_line  # Connection index

    def __repr__(self):
        return f"Line(id={self.id}, outer_line={self.outer_line})"


class Segment:
    """Class to represent a segment in a hexagonal grid. For Example [14,2] with outer lines [4, 5] as lines."""
    def __init__(self, id, connection):
        self.id = id  # Hexagon ID
        self.id_y = id[1]  # Y coordinate of the hexagon
        self.id_x = id[0]  # X coordinate of the hexagon
        self.connection = connection  # Connection index
        self.outer_lines = []
        for i in connection:
            self.outer_lines.append(Line(id, i))

    def __repr__(self):
        return f"Segment(id={self.id}, connection={self.connection})"



class Group:
    """Class to represent a group of connected segments. For Example Group with ID 0 containing segments [14,2][4,5] and as open lines [14,2][4] and [14,2][5] as line."""
    def __init__(self, id, segment = None):
        self.id = id  # Group ID
        self.segments = []  # List of segments in the group
        self.open_ends = []  # List to hold open ends of the group

        if segment is not None:
            self.segments.append(segment)
            self.open_ends.append(segment.outer_lines[0])  # Initialize with the first segment's outer line    
            self.open_ends.append(segment.outer_lines[1])  # Initialize with the second segment's outer line

    def __repr__(self):
        return f"Group(id={self.id}, segments={self.segments}, open_ends={self.open_ends})"
        
    def add_segment(self, segment, new_end, old_end):
        """Add a segment to the group and update open ends."""
        self.segments.append(segment)
        # Update open ends
        self.open_ends.remove(old_end)  # Remove the old end
        self.open_ends.append(new_end)  # Add the new end

    def add_group(self, group, old_end=None, new_end=None):
        """Add a group to the current group and update open ends if provided."""
        self.segments.extend(group.segments)

        if new_end is not None:
            self.open_ends.append(new_end)
        if old_end is not None and old_end in self.open_ends:
            self.open_ends.remove(old_end)



    def test_segment(self, segment):
        """Test if the segment can be added to the group."""
        for open_end in self.open_ends:
            # Check if the segment connects to an open line 0
            if (open_end.id_y + 1) == segment.id_y and (open_end.id_x + 1) == segment.id_x and open_end.outer_line == 0:
                if segment.outer_lines[0].outer_line == 3:
                    return True, segment.outer_lines[1], open_end
                elif segment.outer_lines[1].outer_line == 3:
                    return True, segment.outer_lines[0], open_end
            # Check if the segment connects to an open line 1
            elif (open_end.id_y + 2) == segment.id_y and (open_end.id_x + 0) == segment.id_x and open_end.outer_line == 1:
                if segment.outer_lines[0].outer_line == 4:
                    return True, segment.outer_lines[1], open_end
                elif segment.outer_lines[1].outer_line == 4:
                    return True, segment.outer_lines[0], open_end
            # Check if the segment connects to an open line 2
            elif (open_end.id_y + 1) == segment.id_y and (open_end.id_x - 0) == segment.id_x and open_end.outer_line == 2:
                if segment.outer_lines[0].outer_line == 5:
                    return True, segment.outer_lines[1], open_end
                elif segment.outer_lines[1].outer_line == 5:
                    return True, segment.outer_lines[0], open_end
            # Check if the segment connects to an open line 3
            elif (open_end.id_y - 1) == segment.id_y and (open_end.id_x - 0) == segment.id_x and open_end.outer_line == 3:
                if segment.outer_lines[0].outer_line == 0:
                    return True, segment.outer_lines[1], open_end
                elif segment.outer_lines[1].outer_line == 0:
                    return True, segment.outer_lines[0], open_end
            # Check if the segment connects to an open line 4
            elif (open_end.id_y - 2) == segment.id_y and (open_end.id_x + 0) == segment.id_x and open_end.outer_line == 4:
                if segment.outer_lines[0].outer_line == 1:
                    return True, segment.outer_lines[1], open_end
                elif segment.outer_lines[1].outer_line == 1:
                    return True, segment.outer_lines[0], open_end
            # Check if the segment connects to an open line 5
            elif (open_end.id_y - 1) == segment.id_y and (open_end.id_x + 1) == segment.id_x and open_end.outer_line == 5:
                if segment.outer_lines[0].outer_line == 2:
                    return True, segment.outer_lines[1], open_end
                elif segment.outer_lines[1].outer_line == 2:
                    return True, segment.outer_lines[0], open_end
        return False, False, False


class detection_connected:

    def __init__(self, grid):
        self.grid = grid
        self.segment_group_list = []  # List to hold open group

        self.group_id = 0  # Initialize group ID

        # Iterate through grid and create segments
        for hexagon in self.grid: 
            for connection in hexagon.connection:
                segment_id = hexagon.id
                new_segment = Segment(segment_id, connection)

                
                place_found = False
                # Iterate through existing groups to find a place for the new segment
                for group in self.segment_group_list:
                    # Check if the segment can be added to an existing group
                    result,new_end, old_end = group.test_segment(new_segment)
                    if result:
                        # If it connects to an open segment, add it to the group
                        # Add the segment to the existing group
                        print(f"Adding Segment {new_segment.id} to Group {group.id}")
                        group.add_segment(new_segment, new_end, old_end)
                        place_found = True
                        break    

                # Create a new group if no open group is found
                if not place_found:
                    new_group = Group(self.group_id, new_segment)
                    self.segment_group_list.append(new_group)
                    self.group_id += 1
        

        # Number of groups found
        print(f"Total Groups Found: {len(self.segment_group_list)}")     

        # First Group
        print(f"First Group: {self.segment_group_list[0]}")   

        for group in self.segment_group_list:
            print(group)


    def order_groups_lenght(self):
        """Order the groups by the number of segments in descending order."""
        self.segment_group_list.sort(key=lambda x: len(x.segments), reverse=True)

    def order_groups_shuffle(self):
        """Shuffle the groups randomly."""
        random.shuffle(self.segment_group_list)

    def groups_collouring(self):
        """Give each group a colour such that no groups with a common segment id have the same colour."""
        # Create a list for each Colour with groups
        coloured_groups = []

        copy_segment_group_list = self.segment_group_list  # Copy of the current segment group list

        for group in copy_segment_group_list:
            placed = False  # Flag to check if the group is placed in a colour group

            for colour_group in coloured_groups:
                
                overlap_found = False  # Flag to check if there is an overlap with the colour group
                
                # Check if the group can be added to the colour group
                for segment in group.segments:
                    for colour_segment in colour_group.segments:
                        if segment.id == colour_segment.id:
                            overlap_found = True
                            break


                if not overlap_found:
                    colour_group.add_group(group)
                    placed = True
                    break  # Keine weitere Farbgruppe testen

            if not placed:
                # If no colour group is found, create a new one
                new_coloured_group = Group(len(coloured_groups))
                new_coloured_group.add_group(group)
                coloured_groups.append(new_coloured_group)
        
        # Return len(coloured_groups) to indicate the number of colour groups
        print(f"Total Colour Groups: {len(coloured_groups)}")

        
        return coloured_groups
            

    def merge_groups(self):
        """Check if groups from self.segment_group_list can be merged based on open ends. Repeatedly merge groups until no more merges are possible. Each Group with each group per iteration."""
        merged = True
        x = 0  # Counter for iterations

        # Print number of groups before merging
        print(f"Initial Number of Groups: {len(self.segment_group_list)}")

        while merged:
            
            #count the number of iterations
            print(f"Iteration: {x}")
            x += 1


            unchecked_groups = copy.deepcopy(self.segment_group_list)  # Copy of the current segment group list
            checked_groups = []  # List to hold groups that have been checked
            new_segment_group_list = []

            merged = False  # Reset merged flag for this iteration

            for group in unchecked_groups:
                group_used = False
                if group not in checked_groups:
                    # Check if the group can be merged with any other group
                    for other_group in unchecked_groups:
                        if group != other_group and other_group not in checked_groups and group not in checked_groups:
                            merge, old_end, new_end = self.can_merge(group, other_group)
                            print(merge)
                            if merge:
                                # Merge groups
                                
                                # print group and old group
                                print(f"Merging Group {group.id} with Group {other_group.id}")


                                print(group)
                                print(other_group)

                                group.add_group(other_group, old_end, new_end)
                                new_segment_group_list.append(group)


                                checked_groups.append(other_group)
                                checked_groups.append(group)
                                merged = True
                                group_used = True

                                break  # Exit inner loop if a merge is found
                    if not group_used:
                        # If the group was not merged, add it to the new segment group list
                        new_segment_group_list.append(group)
                        checked_groups.append(group)                
    

            self.segment_group_list = new_segment_group_list
            # Print the number of groups after merging
            print(f"Number of Groups after merging: {len(self.segment_group_list)}")


    
    def can_merge(self, group1, group2):
        """Check if two groups can be merged based on their open ends."""
        for end1 in group1.open_ends:
            for end2 in group2.open_ends:
                # Check if the open ends are compatible for merging
                if (end1.id_y + 1) == end2.id_y and (end1.id_x + 1) == end2.id_x and end1.outer_line == 0 and end2.outer_line == 3:
                    return True, end1, end2
                elif (end1.id_y + 2) == end2.id_y and (end1.id_x + 0) == end2.id_x and end1.outer_line == 1 and end2.outer_line == 4:
                    return True, end1, end2
                elif (end1.id_y + 1) == end2.id_y and (end1.id_x - 0) == end2.id_x and end1.outer_line == 2 and end2.outer_line == 5:
                    return True, end1, end2
                elif (end1.id_y - 1) == end2.id_y and (end1.id_x - 0) == end2.id_x and end1.outer_line == 3 and end2.outer_line == 0:
                    return True, end1, end2
                elif (end1.id_y - 2) == end2.id_y and (end1.id_x + 0) == end2.id_x and end1.outer_line == 4 and end2.outer_line == 1:
                    return True, end1, end2
                elif (end1.id_y - 1) == end2.id_y and (end1.id_x + 1) == end2.id_x and end1.outer_line == 5 and end2.outer_line == 2:
                    return True, end1, end2
        return False, False, False
    '''
    Die conncted Segment List
    Es wird jedes Segment in jedem Hexagon in Grid durchgegangen

        Überprüfen ob das Segment an Passende Stelle Passt
            Wenn nur an eine offene Gruppe
                Segment der Gruppe hinzufügen
                Neues Offene Ende der Gruppe setzten
            Wenn passend auf 2 neue Gruppen
                Segment der ersten Gruppe hinzufügen
                Segment der zweiten an die erste Gruppe anhängen
                Neue offene Enden setzten
            Wenn keine Gruppe
                Eine Neue Gruppe erstellen mit Passenden Enden
    
    Testen der Segment Nach Verbindungen
    offene_segmente = []
        enthält Gruppen (vielleicht ein neues Objekt machen)
         Eigenschaften
            Liste mit Hexagon.ID und Hexagon.Connection Index
            Offene Enden der Line (offene Kante auf die das Zugehörigen Hexagon z.b ([14, 2], 4) letzte Zugefügte Kante wäre 12,1 

            Funktion die Ein Segment prüft ob Teil der Gruppe
                Testen ob durch id und connection das segment anschließt 
                        Schließt [14, 3] [[4, 5], [1, 2], [0, 3]] an ([14, 2], 1)
            
            Funktion die ein Segment in die Gruppe aufnimmt
                Liste einfügen
                Neues Ende setzten
            
            Funktion die eine Gruppe in die Gruppe aufnimmt
                Liste einfügen
                Neues Ende bestimmen
            
    

    ???
    Macht Testen nach Unmöglichen Enden aka Rändern Sinn? in dem Objekt Gruppe wahrscheinlich 



    
    
    
    '''