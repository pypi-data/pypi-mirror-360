import subprocess
from typing import Iterable,Callable,Any
import sys
from json import detect_encoding
encoding = sys.stdout.encoding if sys.stdout.encoding else "utf-8"
class Call():
    def __init__(self,func:Callable[...,Any],*args,**kwargs):
        self.func = func
        self.args=args
        self.kwargs=kwargs
    def __call__(self, *args, **kwds):
        return self.func(*self.args,**self.kwargs)
    
def execute_command(command:str)->str:
    try:
        return subprocess.check_output(command,shell=True,text=True,encoding=encoding).strip()
    except UnicodeDecodeError as e:
        tmp_encoding = detect_encoding(e.object)
        return e.object.decode(encoding=tmp_encoding).strip()
def create_batches(it:Iterable,n:int)->Iterable[Iterable]:
    """create batches of n items for batch using the items in the iterable

    Args:
        it (Iterable): iterable from which batches are created
        n (int): number of items for each batch

    Raises:
        ValueError: If iterable is empty or None and if the number of items for batch is not correct

    Returns:
        Iterable[Iterable]: Iterable containing the batches
    """
    if not n:
        raise ValueError("n must be at least 1")
    if not it:
        raise ValueError("Iterable cannot be None or empty")
    batches=[]
    tmp=list(it)
    n_items=len(tmp)
    if n_items==0:
        raise ValueError("Iterable must not be empty")
    for i in range(0,n_items,n):
        batches.append(tmp[i:i+n])
    return tuple(batches)