from pathlib import Path
from shutil import which
import sys
import os
import subprocess
from typing import Optional
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
from math import floor,ceil
from functools import partial
from typing import Iterable
import json
from datetime import datetime
# max_worker = min(32,os.cpu_count())

def date_builder(since:Optional[datetime]=None,to:Optional[datetime]=None)->list[str]:
    args=[]
    if to and since and to<since:
        raise ValueError("'to' cannot come before 'since'")
    if since:
        d_str=since.strftime(r"%Y-%m-%d")
        args.append(f"--since='{d_str}'")
    if to:
        d_str=to.strftime(r"%Y-%m-%d")
        args.append(f"--until='{d_str}'")
    return args
    
def cmd_builder(command:str,repo:str,*args)->str:
    """Base git command generator

    Args:
        command (str): command to use
        repo (str): git directory to execute the command on

    Returns:
        str: The complete command as a string
    """
            
    arg_string=f"git -C \"{repo}\" {command}"
    arg_string=arg_string + " "+ " ".join(args)
    return arg_string

def range_builder(from_commmit:str,to_commit:Optional[str]=None)->str:
    if not from_commmit:
        raise ValueError("'from_commit' parameter must always be valorized")
    if to_commit:
        return f"{to_commit}..{from_commmit}"
    else:
        return from_commmit

def log_builder(from_commit:str,to_commit:Optional[str]=None,pretty:Optional[str]=None,merges:bool=False,max_count:Optional[int]=None,skip:Optional[int]=None,author:Optional[str]=None,follow:Optional[str]=None,since:Optional[datetime]=None,to:Optional[datetime]=None,args=[])->str:
    """Builds the complete command string for a log command

    Args:
        repo (str): Git repository to execute the command on
        commit (str): The commit from which start the logging operation
        pretty (Optional[str], optional): The format used by --pretty. Defaults to None.
        merges (bool, optional): Specifies whether load merge commits. Defaults to False.
        max_count (Optional[int], optional): Paramenter for --max-count flag. Defaults to None.
        skip (Optional[int], optional): Parameter  for --skip flag. Defaults to None.
        author (Optional[str], optional): Filter only commits coming authored by the passed author. Defaults to None.
        follow (Optional[str], optional): Filter only commits which changed the passed file. Defaults to None.

    Returns:
        str: Returns the git command string
    """
    arg_list=[range_builder(from_commit,to_commit)]
    if max_count!=None:
        if max_count<=0:
            raise ValueError("max_count cannot be negative or 0")
        arg_list.append(f"--max-count={max_count}")
    if skip!=None:
        if skip<0:
            raise ValueError("skip cannot be negative")
        arg_list.append(f"--skip={skip}")
    if not merges:
        arg_list.append("--no-merges")
    if pretty!=None:
        arg_list.append(f'--pretty="format:{pretty}"')
    if author:
        arg_list.append(f'--author="{author}"')
    arg_list.extend(date_builder(since,to))
    arg_list.extend(args)
    if follow:
        arg_list.append(f'--follow -- "{follow}"')
    return " ".join(arg_list)

def rev_list_builder(from_commit:str,to_commit:Optional[str]=None,pretty:Optional[str]=None,merges:bool=False,max_count:Optional[int]=None,skip:Optional[int]=None,author:Optional[str]=None,since:Optional[datetime]=None,to:Optional[datetime]=None,args=[])->str:
    """Builds the complete command string for a log command

    Args:
        repo (str): Git repository to execute the command on
        commit (str): The commit from which start the logging operation
        pretty (Optional[str], optional): The format used by --pretty. Defaults to None.
        merges (bool, optional): Specifies whether load merge commits. Defaults to False.
        max_count (Optional[int], optional): Paramenter for --max-count flag. Defaults to None.
        skip (Optional[int], optional): Parameter  for --skip flag. Defaults to None.
        author (Optional[str], optional): Filter only commits coming authored by the passed author. Defaults to None.

    Returns:
        str: Returns the git command string
    """
    arg_list=[range_builder(from_commit,to_commit)]
    if max_count!=None:
        if max_count<=0:
            raise ValueError("max_count cannot be negative or 0")
        arg_list.append(f"--max-count={max_count}")
    if skip!=None:
        if skip<0:
            raise ValueError("skip cannot be negative")
        arg_list.append(f"--skip={skip}")
    if not merges:
        arg_list.append("--no-merges")
    if pretty!=None:
        arg_list.append(f'--pretty="format:{pretty}"')
    if author!=None:
        arg_list.append(f'--author="{author}"')
    arg_list.extend(date_builder(since,to))
    arg_list.extend(args)
    return " ".join(arg_list)

def is_git_available()->bool:
    """Checks whether git is on PATH

    Returns:
        bool: If git is on PATH
    """
    return which("git")!=None

def is_dir_a_repo(path:str)->bool:
    """Checks whether the path points to a git directory

    Args:
        path (str): path to repo dir

    Returns:
        bool: Returns wheter the directory is a repo
    """
    cmd = f"git -C \"{Path(path).resolve().as_posix()}\" rev-parse HEAD"
    try:
        subprocess.check_call(cmd,shell=True,stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def get_head_commit(path:str)->str:
    """Return head commit

    Args:
        path (str): path to git directory

    Returns:
        str: Returns HEAD's commit sha
    """
    cmd = f"git -C \"{Path(path).resolve().as_posix()}\" rev-parse HEAD"
    return subprocess.check_output(cmd,shell=True).decode()[:-1]

