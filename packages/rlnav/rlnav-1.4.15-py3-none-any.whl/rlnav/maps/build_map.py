from maps_index import MapsIndex
from tile_type import TileType
import importlib


def build_map(map_name, corridors_width=3):
    if isinstance(map_name, MapsIndex):
        map_name = map_name.value
    maze_map = importlib.import_module("rlnav.maps." + map_name).maze_array

    # Find rows that can be duplicated
    rows_to_duplicate = []
    for index, row in enumerate(maze_map):
        horizontal_wall_length = 0
        for cell in row:
            if cell == TileType.WALL.value:
                horizontal_wall_length += 1
            if horizontal_wall_length > 1:
                # This row have a horizontal wall. Skip it
                break
        else:
            # This row have no horizontal wall. Save it.
            rows_to_duplicate.append(index)
    del horizontal_wall_length

    # Find columns that can be duplicated
    columns_to_duplicate = []
    for column_index in range(len(maze_map[0])):
        vertical_wall_length = 0
        for cell in row:
            if cell == TileType.WALL.value:
                vertical_wall_length += 1
            else:
                vertical_wall_length = 0
            if vertical_wall_length > 1:
                # This row have a horizontal wall. Skip it
                print("skipped row ", column_index, " because of a too long wall at position ", column_index, sep="")
                vertical_wall_length = 0
                break
        else:
            # This row have no horizontal wall. Save it.
            print("Added row ", index, sep="")
            columns_to_duplicate.append(column_index)

    # Duplicate the rows and columns
    new_maze_array = []
    for index, row in enumerate(maze_map):
        new_maze_array += [row] * (corridors_width if index in rows_to_duplicate else 1)
        # if index in columns_to_duplicate:
        #     new_maze_array += [[row]]
        # else:
        #     new_maze_array += [[row]] * corridors_width

    for column_index in range(len(maze_map[0])):
        if column_index in columns_to_duplicate:
            for row_index in range(len(maze_array[0])):
                element_to_add = maze_array[row_index][column_index]

if __name__ == "__main__":
    build_map(MapsIndex.FOUR_ROOMS, corridors_width=4)
