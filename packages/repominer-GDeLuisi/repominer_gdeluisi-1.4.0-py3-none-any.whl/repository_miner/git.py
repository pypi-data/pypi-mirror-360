from .utility import execute_command
from .helper import cmd_builder,is_dir_a_repo,is_git_available
from .exceptions import *
from functools import partial
from typing import Iterable
from subprocess import CalledProcessError
class Git():
    def __init__(self,path:str):
        if not is_git_available():
            raise GitNotFoundException("Git not found")
        if not is_dir_a_repo(path):
            raise NotGitRepositoryError(f"Directory {path} is not a git repository")
        self.path=path

    def _execute_command(self,command:str,*args)->str:
        cmd=""
        try:
            if len(args)==1 and not isinstance(args[0],str) and isinstance(args[0],Iterable):
                cmd=cmd_builder(command,self.path,*args[0])
            else:
                cmd=cmd_builder(command,self.path,*args)
            return execute_command(cmd)
        except CalledProcessError as e:
            raise GitCmdError(f"Command {cmd} raised an error {e}")
    
    def __getattr__(self, name:str):
        if name in self.__dict__ or name in self.__class__.__dict__:
            return getattr(self,name)
        name=name.replace("_","-")
        return partial(self._execute_command,name)
    
    #pickle interface methods for multiprocessing compatibility
    
    def __getstate__(self):
        state=self.__dict__.copy()
        return state
    
    def __setstate__(self,state):
        self.__dict__.update(state)