# base.py

import random

# Define data classes to structure your data
class BoxData:
    def __init__(self, positions, sizes):
        self.positions = positions  # List of positions for the boxes
        self.sizes = sizes          # Corresponding sizes for each box

class LifterData:
    def __init__(self, positions, directions):
        self.positions = positions  # List of positions for the lifters
        self.directions = directions  # List of directions for the lifters

class TrailerData:
    def __init__(self, position):
        self.position = position  # Position of the trailer

# Functions to simulate backend data
def get_box_data(n_boxes, dim_board):
    positions = []
    sizes = []
    sizes_cm = [
        (10, 10, 10),  # Size 1
        (50, 50, 50),  # Size 2
        (70, 70, 70)   # Size 3
    ]
    for _ in range(n_boxes):
        size_cm = random.choice(sizes_cm)
        scale_factor = 0.5
        scaled_size = tuple(s * scale_factor for s in size_cm)
        x = random.uniform(-dim_board, dim_board)
        z = random.uniform(dim_board - 10, dim_board)
        y = scaled_size[1] / 10.0
        positions.append((x, y, z))
        sizes.append(scaled_size)
    return BoxData(positions, sizes)

def get_lifter_data(n_lifters, dim_board, drop_off_point):
    positions = []
    directions = []
    for _ in range(n_lifters):
        x = random.randint(-dim_board, dim_board)
        z = random.randint(-dim_board, dim_board)
        y = 6  # Assuming a fixed Y position
        positions.append([x, y, z])
        # Random direction
        dir_x = random.randint(-10, 10) or 1
        dir_z = random.randint(-10, 10) or 1
        magnitude = (dir_x**2 + dir_z**2) ** 0.5
        directions.append([dir_x / magnitude, 0, dir_z / magnitude])
    return LifterData(positions, directions)

def get_trailer_data(dim_board):
    # Fixed position for the trailer
    position = (0, 0, -dim_board)
    return TrailerData(position)