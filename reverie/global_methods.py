"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: global_methods.py
Description: Contains functions used throughout my projects.
"""

import os

from os import listdir

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


def find_filenames(path_to_dir: str, suffix = ".csv") -> list[str]:
  """
  Given a directory, find all files that ends with the provided suffix and 
  returns their paths.  
  ARGS:
    path_to_dir: Path to the current directory 
    suffix: The target suffix.
  RETURNS: 
    A list of paths to all files in the directory. 
  """
  filenames = listdir(path_to_dir)
  return [ path_to_dir+"/"+filename 
           for filename in filenames if filename.endswith( suffix ) ]
