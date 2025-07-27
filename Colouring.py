import math
import svgwrite
from shapely.geometry import Polygon, LineString, LinearRing
import numpy as np
import random
import hex_structure
import line_detection
from Hexagon import _Hexagon
from Segment import _Segment
from Group import _Group

class _Colouring():
    def __init__(self, grid, colour_count=4):
        
        self.grid = grid
        self.segment_group_list = []  # List to hold open group

        self.group_id = 0  # Initialize group ID

        # Iterate through grid and create segments
        for hexagon in self.grid: 
            for segment in hexagon.segments:

                place_found = False
                # Iterate through existing groups to find a place for the new segment
                for group in self.segment_group_list:
                    # Check if the segment can be added to an existing group
                    result, old_end = group.test_segment(segment)
                    if result:
                        # If it connects to an open segment, add it to the group
                        # Add the segment to the existing group
                        group.add_segment(segment, old_end)
                        place_found = True
                        break    

                # Create a new group if no open group is found
                if not place_found:
                    new_group = _Group(self.group_id, segment)
                    self.segment_group_list.append(new_group)
                    self.group_id += 1


        self.merge_groups()
        self.groups_colouring()
        
        # Merge the colour groups until colour_count is reached
        while len(self.coloured_groups) > colour_count:
            self.merge_colour_groups_with_smallest_intersection() 
        self.assign_colour_group()


    def merge_groups(self):
        """Check if groups from self.segment_group_list can be merged based on open ends. Repeatedly merge groups until no more merges are possible. Each Group with each group per iteration."""
        merged = True
        x = 0  # Counter for iterations

        while merged:
            
            #count the number of iterations
            x += 1

            unchecked_groups = self.segment_group_list  # Copy of the current segment group list
            checked_groups = []  # List to hold groups that have been checked
            new_segment_group_list = []

            merged = False  # Reset merged flag for this iteration

            for group in unchecked_groups:
                group_used = False
                if group not in checked_groups:
                    # Check if the group can be merged with any other group
                    for other_group in unchecked_groups:
                        if group != other_group and other_group not in checked_groups and group not in checked_groups:
                            merge, connecting_end_g1, connecting_end_g2 = self.test_merge(group, other_group)
                            if merge:
                                # Merge groups
                                group.add_group(other_group, connecting_end_g1, connecting_end_g2)
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


    
    def groups_colouring(self):
        """Give each group a colour such that no groups with a common segment id have the same colour."""
        # Create a list for each Colour with groups
        self.coloured_groups = []

        copy_segment_group_list = self.segment_group_list  # Copy of the current segment group list

        for group in copy_segment_group_list:
            placed = False  # Flag to check if the group is placed in a colour group

            for colour_group in self.coloured_groups:
                
                overlap_found = False  # Flag to check if there is an overlap with the colour group
                
                # Check if the group can be added to the colour group
                for segment in group.segments:
                    for colour_segment in colour_group.segments:
                        if segment.id == colour_segment.id:
                            overlap_found = True
                            break
                    if overlap_found:
                        break


                if not overlap_found:
                    colour_group.add_segment_to_group(group.segments)
                    placed = True
                    break  # Keine weitere Farbgruppe testen

            if not placed:
                # If no colour group is found, create a new one
                self.coloured_groups.append(group)
        
        # Return len(coloured_groups) to indicate the number of colour groups
        #print(f"Total Colour Groups: {len(self.coloured_groups)}")

    def assign_colour_group(self):
        """Assign colour_group to each segment in the coloured groups."""
        for colour_group in self.coloured_groups:
            for segment in colour_group.segments:
                # Assign the position of clour groups to the segment
                segment.colour_group = self.coloured_groups.index(colour_group)

    
    def test_merge(self, group1, group2):
        """Check if two groups can be merged based on their open ends."""
        for border_group2 in group2.border_segments:
            
                # Check if the open ends are compatible for merging
            result, border = group1.test_segment(border_group2)
            if result:
                # If they can be merged, return True and the connecting segments
                return True, border, border_group2



        return False, False, False

    def merge_colour_groups_with_smallest_intersection(self):
        """Merge the two colour groups with the smallest intersection."""
        if len(self.coloured_groups) < 2:
            print("Not enough colour groups to merge.")
            return

        smallest_intersection = 10000000
        # Search for the two colour groups with the smallest intersection
        for group in self.coloured_groups:
            for other_group in self.coloured_groups:
                if group != other_group:
                    intersection = group.calculate_intersection(other_group)
                    if  intersection < smallest_intersection:
                        # If an intersection is found, merge the two groups
                        smallest_intersection = intersection
                        smallest_group = group
                        second_smallest_group = other_group
        # Merge the two smallest groups
        smallest_group.add_segment_to_group(second_smallest_group.segments)
        self.coloured_groups.remove(second_smallest_group)

    


    def merge_smallest_colour_group(self):
        """Merge the two smallest colour groups."""
        if len(self.coloured_groups) < 2:
            print("Not enough groups to merge.")
            return

        # Sort the groups by the number of segments they contain
        sorted_groups = sorted(self.coloured_groups, key=lambda g: len(g.segments))

        # Get the two smallest groups
        smallest_group = sorted_groups[0]
        second_smallest_group = sorted_groups[1]

        # Merge the two smallest groups
        smallest_group.add_segment_to_group(second_smallest_group.segments)

        # Remove the second smallest group from the list
        self.coloured_groups.remove(second_smallest_group)


    def test_grouping(self):
        """Change the colour_group of all segments of the biggest group to 1."""
        # Find the biggest group
        biggest_group = max(self.segment_group_list, key=lambda g: len(g.segments))
        print(f"Biggest Group ID: {biggest_group.id} with {len(biggest_group.segments)} segments")

        print(biggest_group)

        # Change the colour_group of all segments in the biggest group to 1
        for segment in biggest_group.segments:
            segment.colour_group = 1

        print("Colouring complete for the biggest group.")