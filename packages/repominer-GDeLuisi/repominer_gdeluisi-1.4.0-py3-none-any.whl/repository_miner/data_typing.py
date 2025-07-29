from  dataclasses import dataclass,field
from datetime import datetime
from time import strptime
from typing import Literal,get_args,Iterable,Optional,Union,Generator,Callable
import json
from pathlib import Path
from repository_miner.utility import Call

@dataclass
class Author():
    email:str
    name:str
    commits_authored:list[str]=field(default_factory=lambda: [])
    def __hash__(self):
        return hash(repr(self.name)+repr(self.email))
    def __eq__(self, value):
        if not isinstance(value,Author):
            raise TypeError(f"Expected value of type <Author>, received {type(value)}")
        return self.name==value.name and self.email==value.email
    def __str__(self):
        return f"Name: {self.name} , Email: {self.email}"
    def __repr__(self):
        return  f"Name: {self.name} , Email: {self.email} , Commits: {self.commits_authored}"
    
@dataclass
class CommitInfo():
    commit_hash:str
    abbr_hash:str
    tree:str
    refs:str
    subject:str
    author_name:str
    author_email:str
    date:datetime
    def __hash__(self):
        return hash(self.commit_hash)
    def get_tree(self)->'Tree':
        raise NotImplementedError()

@dataclass
class Head():
    name:str
    hash:str
    def __hash__(self):
        return hash(self.hash)
    def traverse_commits(self)->Generator[CommitInfo,None,None]:
        raise NotImplementedError()
    
class HeadImpl(Head):
    def __init__(self,name:str,hash:str,retrieve_func:Call):
        super().__init__(name,hash)
        self.retrieve_func=retrieve_func
    def traverse_commits(self):
        return self.retrieve_func()


@dataclass
class Blob():
    hash:str
    name:str
    path:str
    size:int
    def __hash__(self):
        return hash(self.hash)
    def get_source(self)->list[str]:
        raise NotImplementedError()

@dataclass
class Tree():
    hash:str
    path:str
    def traverse(self)->Generator[Union['Tree',Blob],None,None]:
        raise NotImplementedError()
    def __hash__(self):
        return hash(self.hash)
    
class TreeImpl(Tree):
    def __init__(self,hash:str,path:str,iter_function:Call):
        super().__init__(hash,path)
        self.iter_func=iter_function
    def traverse(self)->Generator[Union[Tree,Blob],None,None]:
        return self.iter_func()
    
class CommitInfoImpl(CommitInfo):
    def __init__(self
    ,commit_hash:str
    ,abbr_hash:str
    ,tree:str
    ,refs:str
    ,subject:str
    ,author_name:str
    ,author_email:str
    ,date:datetime
    ,tree_func:Call):
        super().__init__(commit_hash,abbr_hash,tree,refs,subject,author_name,author_email,date)
        self.tree_func=tree_func
    
    def get_tree(self)->Tree:
        return self.tree_func()
    
class BlobImpl(Blob):
    def __init__(self,hash:str,name:str,path:str,size:int,source_func:Call):
        super().__init__(hash,name,path,size)
        self.source_func=source_func
    def get_source(self):
        return self.source_func()