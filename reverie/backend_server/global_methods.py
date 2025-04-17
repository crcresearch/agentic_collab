"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: global_methods.py
Description: Contains functions used throughout my projects.
"""

import csv
import os
import shutil
import errno
from typing import Any


def create_folder_if_not_there(curr_path: str) -> bool:
  """
  Checks if a folder in the curr_path exists. If it does not exist, creates
  the folder.
  Note that if the curr_path designates a file location, it will operate on
  the folder that contains the file. But the function also works even if the
  path designates to just a folder.
  Args:
    curr_list: list to write. The list comes in the following form:
         [['key1', 'val1-1', 'val1-2'...],
          ['key2', 'val2-1', 'val2-2'...],]
    outfile: name of the csv file to write
  RETURNS:
    True: if a new folder is created
    False: if a new folder is not created
  """
  outfolder_name = curr_path.split("/")
  if len(outfolder_name) != 1:
    # This checks if the curr path is a file or a folder.
    if "." in outfolder_name[-1]:
      outfolder_name = outfolder_name[:-1]

    outfolder_name = "/".join(outfolder_name)
    if not os.path.exists(outfolder_name):
      os.makedirs(outfolder_name)
      return True

  return False


def read_file_to_list(curr_file: str, strip_trail=True) -> list[list[str]]:
  """
  Reads in a csv file to a list of list.
  ARGS:
    curr_file: path to the current csv file.
  RETURNS:
    List of list where the component lists are the rows of the file.
  """
  analysis_list: list[list[str]] = []
  with open(curr_file) as f_analysis_file:
    data_reader = csv.reader(f_analysis_file, delimiter=",")
    for count, row in enumerate(data_reader):
      if strip_trail:
        row = [i.strip() for i in row]
      analysis_list += [row]
  return analysis_list


def check_if_file_exists(curr_file: str) -> bool:
  """
  Checks if a file exists
  ARGS:
    curr_file: path to the current csv file.
  RETURNS:
    True if the file exists
    False if the file does not exist
  """
  try:
    with open(curr_file) as f_analysis_file:
      pass
    return True
  except:
    return False


def copyanything(src: str, dst: str) -> None:
  """
  Copy over everything in the src folder to dst folder.
  ARGS:
    src: address of the source folder
    dst: address of the destination folder
  RETURNS:
    None
  """
  try:
    shutil.copytree(src, dst)
  except OSError as exc:  # python >2.5
    if exc.errno in (errno.ENOTDIR, errno.EINVAL):
      shutil.copy(src, dst)
    else:
      raise


def freeze(value: Any) -> Any:
  if isinstance(value, list) or isinstance(value, tuple):
    return tuple(freeze(x) for x in value)
  elif isinstance(value, dict):
    return tuple((k, freeze(v)) for k, v in value.items())
  else:
    return value
