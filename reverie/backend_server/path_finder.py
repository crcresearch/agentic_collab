"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: path_finder.py
Description: Implements various path finding functions for generative agents.
Some of the functions are defunct. 
"""
import numpy as np
from typing import Optional, Union, Literal

Maze = list[list[str]]
Tile = tuple[int, int]

def print_maze(maze: Maze):
  for row in maze:
    for item in row:
      print(item, end='')
    print()


def path_finder_v1(
  maze: Maze, start: Tile, end: Tile, collision_block_char: str, verbose: bool = False
) -> Union[list[Tile], Literal[False]]:
  def prepare_maze(maze: Maze, start: Tile, end: Tile) -> Maze:
    maze[start[0]][start[1]] = "S"
    maze[end[0]][end[1]] = "E"
    return maze

  def find_start(maze: Maze) -> Optional[Tile]:
    for row in range(len(maze)):
      for col in range(len(maze[0])):
        if maze[row][col] == 'S':
          return row, col

  def is_valid_position(maze: Maze, pos_r: int, pos_c: int) -> bool:
    if pos_r < 0 or pos_c < 0:
      return False
    if pos_r >= len(maze) or pos_c >= len(maze[0]):
      return False
    if maze[pos_r][pos_c] in ' E':
      return True
    return False

  def solve_maze(
    maze: Maze, start: Tile, verbose: bool = False
  ) -> Union[list[Tile], Literal[False]]:
    path: list[Tile] = []
    # We use a Python list as a stack - then we have push operations as
    # append, and pop as pop.
    stack: list[Tile] = []
    # Add the entry point (as a tuple)
    stack.append(start)
    # Go through the stack as long as there are elements
    while len(stack) > 0:
      pos_r, pos_c = stack.pop()
      if verbose: 
        print("Current position", pos_r, pos_c)
      if maze[pos_r][pos_c] == 'E':
        path += [(pos_r, pos_c)]
        return path
      if maze[pos_r][pos_c] == 'X':
        # Already visited
        continue
      # Mark position as visited
      maze[pos_r][pos_c] = 'X'
      path += [(pos_r, pos_c)]
      # Check for all possible positions and add if possible
      if is_valid_position(maze, pos_r - 1, pos_c):
        stack.append((pos_r - 1, pos_c))
      if is_valid_position(maze, pos_r + 1, pos_c):
        stack.append((pos_r + 1, pos_c))
      if is_valid_position(maze, pos_r, pos_c - 1):
        stack.append((pos_r, pos_c - 1))
      if is_valid_position(maze, pos_r, pos_c + 1):
        stack.append((pos_r, pos_c + 1))

      # To follow the maze
      if verbose: 
        print('Stack:' , stack)
        print_maze(maze)

    # We didn't find a path, hence we do not need to return the path
    return False

  # clean maze
  new_maze: Maze = []
  for row in maze: 
    new_row: list[str] = []
    for j in row: 
      if j == collision_block_char: 
        new_row += ["#"]
      else: 
        new_row += [" "]
    new_maze += [new_row]

  prepared_maze = prepare_maze(new_maze, start, end)
  start_tile = find_start(prepared_maze)
  path = solve_maze(prepared_maze, start_tile, verbose)
  return path


def path_finder_v2(
  maze: Maze, start: Tile, end: Tile, collision_block_char: str, verbose: bool = False
) -> list[Tile]:
  def make_step(m: list[list[int]], k: int):
    for i in range(len(m)):
      for j in range(len(m[i])):
        if m[i][j] == k:
          if i>0 and m[i-1][j] == 0 and maze[i-1][j] == 0:
            m[i-1][j] = k + 1
          if j>0 and m[i][j-1] == 0 and maze[i][j-1] == 0:
            m[i][j-1] = k + 1
          if i<len(m)-1 and m[i+1][j] == 0 and maze[i+1][j] == 0:
            m[i+1][j] = k + 1
          if j<len(m[i])-1 and m[i][j+1] == 0 and maze[i][j+1] == 0:
             m[i][j+1] = k + 1

  new_maze: list[list[int]] = []
  for row in maze: 
    new_row: list[int] = []
    for j in row:
      if j == collision_block_char: 
        new_row += [1]
      else: 
        new_row += [0]
    new_maze += [new_row]

  m: list[list[int]] = []
  for i in range(len(new_maze)):
      m.append([])
      for j in range(len(new_maze[i])):
          m[-1].append(0)
  i,j = start
  m[i][j] = 1 

  k = 0
  except_handle = 150
  while m[end[0]][end[1]] == 0:
      k += 1
      make_step(m, k)

      if except_handle == 0: 
        break
      except_handle -= 1 

  i, j = end
  k = m[i][j]
  the_path = [(i,j)]
  while k > 1:
    if i > 0 and m[i - 1][j] == k-1:
      i, j = i-1, j
      the_path.append((i, j))
      k-=1
    elif j > 0 and m[i][j - 1] == k-1:
      i, j = i, j-1
      the_path.append((i, j))
      k-=1
    elif i < len(m) - 1 and m[i + 1][j] == k-1:
      i, j = i+1, j
      the_path.append((i, j))
      k-=1
    elif j < len(m[i]) - 1 and m[i][j + 1] == k-1:
      i, j = i, j+1
      the_path.append((i, j))
      k -= 1
        
  the_path.reverse()
  return the_path


def path_finder(maze: Maze, start: Tile, end: Tile, collision_block_char: str, verbose: bool = False):
  # EMERGENCY PATCH
  start = (start[1], start[0])
  end = (end[1], end[0])
  # END EMERGENCY PATCH

  path = path_finder_v2(maze, start, end, collision_block_char, verbose)

  new_path = []
  for i in path: 
    new_path += [(i[1], i[0])]
  path = new_path
  
  return path


def closest_coordinate(curr_coordinate: Tile, target_coordinates: list[Tile]):
  min_dist: Optional[np.float64] = None
  closest_coordinate: Optional[Tile] = None
  for coordinate in target_coordinates: 
    a = np.array(coordinate)
    b = np.array(curr_coordinate)
    dist: np.float64 = abs(np.linalg.norm(a-b))
    if not closest_coordinate or not min_dist:
      min_dist = dist
      closest_coordinate = coordinate
    else:
      if min_dist > dist: 
        min_dist = dist
        closest_coordinate = coordinate

  return closest_coordinate


def path_finder_2(maze: Maze, start: Tile, end: Tile, collision_block_char: str, verbose: bool = False):
  # start => persona_a
  # end => persona_b
  end_list = list(end)

  t_top = (end_list[0], end_list[1]+1)
  t_bottom = (end_list[0], end_list[1]-1)
  t_left = (end_list[0]-1, end_list[1])
  t_right = (end_list[0]+1, end_list[1])
  pot_target_coordinates = [t_top, t_bottom, t_left, t_right]

  maze_width = len(maze[0]) 
  maze_height = len(maze)
  target_coordinates: list[Tile] = []
  for coordinate in pot_target_coordinates: 
    if coordinate[0] >= 0 and coordinate[0] < maze_width and coordinate[1] >= 0 and coordinate[1] < maze_height: 
      target_coordinates += [coordinate]

  target_coordinate = closest_coordinate(start, target_coordinates)

  path = path_finder(maze, start, target_coordinate, collision_block_char, verbose=False)
  return path


def path_finder_3(maze: Maze, start: Tile, end: Tile, collision_block_char: str, verbose: bool = False):
  # start => persona_a
  # end => persona_b

  curr_path = path_finder(maze, start, end, collision_block_char, verbose=False)
  if len(curr_path) <= 2: 
    return []
  else: 
    a_path = curr_path[:int(len(curr_path)/2)]
    b_path = curr_path[int(len(curr_path)/2)-1:]
  b_path.reverse()

  print (a_path)
  print (b_path)
  return a_path, b_path


if __name__ == '__main__':
  maze = [['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'], 
          [' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#'], 
          ['#', ' ', '#', ' ', ' ', '#', '#', ' ', ' ', ' ', '#', ' ', '#'], 
          ['#', ' ', '#', ' ', ' ', '#', '#', ' ', '#', ' ', '#', ' ', '#'], 
          ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', '#'], 
          ['#', '#', '#', ' ', '#', ' ', '#', '#', '#', ' ', '#', ' ', '#'], 
          ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' '], 
          ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']]
  start = (0, 1)
  end = (0, 1)
  print (path_finder(maze, start, end, "#"))

  print ("-===")
  start = (0, 1)
  end = (11, 4)
  print (path_finder_2(maze, start, end, "#"))

  print ("-===")
  start = (0, 1)
  end = (12, 6)
  print (path_finder_3(maze, start, end, "#"))

  print ("-===")
  path_finder_3(maze, start, end, "#")[0]
  path_finder_3(maze, start, end, "#")[1]
